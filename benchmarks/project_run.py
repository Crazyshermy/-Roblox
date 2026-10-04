#!/usr/bin/env python3
"""Project benchmark: baseline Claude vs Claude + Roblox Apex doing REAL work (edits allowed) in the
Lighthouse fixture game, with the Studio-workflow simulator connected as an MCP server in both arms.

Measures outcome (blind Opus judge over diff + answer, rubric from tests/fixtures/lighthouse.FLAWS.md)
and process (inspect-before-edit, playtest + console after last edit, Luau syntax validity, seeded
runtime error cleared). Simulator evidence is process evidence only, never E5.

Usage: python3 benchmarks/project_run.py --luau-compile /path/to/luau-compile [--only P1,P3] [--model sonnet]
"""
import argparse, concurrent.futures as cf, datetime, json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tests"))
from run_case import run_in  # noqa: E402
from run import JUDGE_PROMPT  # noqa: E402  (same blind pairwise judge format)

FIXTURE = os.path.join(REPO, "tests", "fixtures", "lighthouse")
SIM = os.path.join(REPO, "tests", "studio_sim", "server.py")
SKILLS = os.path.join(REPO, ".claude", "skills")
CLAUDE_BLOCK = os.path.join(SKILLS, "roblox-init", "templates", "CLAUDE-block.md")
EDIT = ("Read Glob Grep Edit Write Skill mcp__roblox_studio", "Bash WebFetch WebSearch Agent")
CTX = "This is my Roblox game (Rojo project; Roblox Studio is connected through MCP). "

TASKS = [
    {"id": "P1-respawn-hud", "prompt": CTX + "Players say the HUD breaks and sometimes errors after they respawn. Fix it.",
     "rubric": ["Identifies top-level player.Character.Humanoid as nil-on-load and stale-after-respawn",
                "Fix rebinds on CharacterAdded (and handles an already-existing character) instead of a one-time wait",
                "Fix keeps the HUD working (fuel display still updates)",
                "Verifies: playtests and checks console output after the fix, or clearly states what wasn't verified",
                "Change is minimal and drop-in (no unrelated rewrites)"]},
    {"id": "P2-refuel-exploit", "prompt": CTX + "I'm worried exploiters can abuse refueling the lamp. Harden it.",
     "rubric": ["Server no longer trusts a client-sent amount (or strictly validates type, NaN/inf, sign, integer, upper bound)",
                "Server checks the player actually has the oil it spends (no negative balances)",
                "Adds a proximity/range check to the lamp using server-side positions",
                "Adds a server-side rate limit or cooldown",
                "Check and deduction are atomic (no yield between); refuel still works for honest players",
                "Notes leaderstats-as-truth or other remaining risks honestly"]},
    {"id": "P3-data-loss", "prompt": CTX + "Some players lose their oil after rejoining quickly. Fix the saving.",
     "rubric": ["Identifies that defaulting to 0 on a failed load causes wipes (fails safe: retry/kick or block saving)",
                "Replaces blind SetAsync with UpdateAsync and/or session locking (or a proven library) to stop stale overwrites on fast server hops",
                "Adds BindToClose to save on shutdown",
                "Retries with backoff and handles nil/old data shape",
                "Doesn't let play/earning start before data is loaded (or guards leaderstats access)",
                "States how to test it (two servers, Studio API access caution) without claiming it was verified"]},
    {"id": "P4-lamp-sync", "prompt": CTX + "Is the way lamp fuel reaches clients any good? Improve it if not.",
     "rubric": ["Replaces per-second FireAllClients with replicated state (attribute on the Lamp or similar)",
                "Client reads initial value and listens to changes (late joiners correct immediately)",
                "Keeps the HUD working with the new mechanism",
                "Avoids unnecessary traffic (e.g. only write when value changes)",
                "Explains the trade-off concisely"]},
    {"id": "P5-dark-design", "prompt": CTX + "The lamp going dark currently means nothing. Propose (don't implement yet) what should happen so the game is worth playing. Keep it focused.",
     "rubric": ["Grounded in the specific fantasy (storm night, lighthouse, co-op keepers), not generic",
                "Creates co-op interdependence / meaningful decisions, not just a penalty",
                "Builds tension/anticipation (cues before threat) and a recovery path",
                "Avoids generic Roblox slop (coins, upgrades, pets, rebirths) unless justified",
                "Mentions how to test or validate it with players",
                "Respects server authority / multiplayer constraints at a high level"]},
    {"id": "P6-refuel-feel", "prompt": CTX + "Refueling the lamp feels flat — you press E and a number changes. Make it feel good.",
     "rubric": ["Immediate client-side feedback on input (sound/VFX/animation/UI) without waiting for the server",
                "Server remains authoritative for the actual fuel change; client handles rejection gracefully",
                "Multiple feedback channels (sound, light pulse/VFX, UI, camera) tied to the lamp fantasy",
                "Considers hold-to-refuel / anticipation or a satisfying interaction rather than a single keypress",
                "Considers mobile (no keyboard E) e.g. ProximityPrompt or touch button",
                "Implementation compiles and is coherent with existing code"]},
    {"id": "P7-creeping-dark", "prompt": CTX + "I want the darkness to physically creep across the island as the lamp runs low, swallowing things. Roblox can't really do that, so I'll just darken the screen. Fine?",
     "rubric": ["Does not simply agree to the downgrade; preserves the intended experience",
                "Identifies the real constraints rather than asserting impossibility",
                "Proposes concrete Roblox techniques (client-side fog/atmosphere driven by distance, local parts/VFX, server-authoritative darkness radius, etc.)",
                "Keeps gameplay authority on the server while presentation is client-side",
                "Notes performance/mobile considerations",
                "Offers options or a staged path with trade-offs"]},
    {"id": "P8-npc-chase", "prompt": CTX + "When the lamp runs out, a monster should spawn and chase the nearest player across the island. Implement it.",
     "rubric": ["Monster AI runs on the server with server network ownership (SetNetworkOwner(nil)) of its root",
                "Uses PathfindingService with status/failure handling (non-Success status, Blocked, MoveTo 8s timeout or stuck detection)",
                "Explicit state machine or clear states (idle/chase/search) and target selection that handles target leaving/dying/respawning",
                "Throttled updates (no per-frame pathfinding; reasonable recompute rate) and cleanup when the lamp is relit",
                "Telegraphs the threat (sound/light cue) and keeps it fair/readable",
                "Code compiles and integrates with LampService (fuel state) without breaking existing behavior"]},
    {"id": "P9-dev-product", "prompt": CTX + "Add a developer product that sells a can of 50 oil for Robux.",
     "rubric": ["Grants only inside MarketplaceService.ProcessReceipt (not PromptProductPurchaseFinished or a client remote)",
                "Idempotent on PurchaseId; returns PurchaseGranted only after the grant is durably recorded, NotProcessedYet otherwise",
                "Handles the player not yet loaded / left (yield until loaded or NotProcessedYet), and a single ProcessReceipt handler",
                "Client only prompts (PromptProductPurchase); no client-trusted grant path",
                "Persists the purchased oil (not only leaderstats) or flags that DataService must be fixed for it to stick",
                "States what wasn't verified (real purchase flow needs Studio test mode / live)"]},
    {"id": "P10-mobile-controls", "prompt": CTX + "Most of my players are on phones and some use controllers. Make the HUD and refueling work well for them.",
     "rubric": ["Refuel works on touch and gamepad (ProximityPrompt, ContextActionService button, or Input Action System), not only the E key",
                "HUD layout is scale-based/responsive with safe-area handling and readable text on small screens",
                "Touch targets are large enough and placed away from default thumbstick/jump zones",
                "Server still validates the refuel (client-initiated prompt/remote treated as untrusted)",
                "Keeps or fixes existing HUD behavior (respawn-safe) without breaking it",
                "Mentions how to verify on Device Emulator presets / real devices"]},
]


def make_project(arm):
    d = tempfile.mkdtemp(prefix=f"apex-proj-{arm}-")
    shutil.copytree(FIXTURE, d, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "fixture"], check=True)
    if arm == "apex":
        for n in os.listdir(SKILLS):
            if n.startswith("roblox"):
                shutil.copytree(os.path.join(SKILLS, n), os.path.join(d, ".claude", "skills", n))
        shutil.copy(CLAUDE_BLOCK, os.path.join(d, "CLAUDE.md"))
    return d


def process_metrics(calls, proj, luau_compile):
    names = [c["tool"].split("__")[-1] for c in calls]
    edits = [i for i, n in enumerate(names) if n in ("Edit", "Write")]
    reads = [i for i, n in enumerate(names) if n in ("Read", "Grep", "Glob", "script_read", "script_grep", "search_game_tree")]
    m = {"edited": bool(edits), "skills": [c["input"].get("skill") for c in calls if c["tool"] == "Skill"]}
    if edits:
        last = edits[-1]
        m["inspected_before_edit"] = bool(reads) and reads[0] < edits[0]
        m["playtest_after_last_edit"] = any(n == "start_stop_play" for n in names[last:])
        m["console_after_last_edit"] = any(n == "get_console_output" for n in names[last:])
    bad = []
    for root, _, files in os.walk(os.path.join(proj, "src")):
        for f in files:
            if f.endswith(".luau") and subprocess.run([luau_compile, os.path.join(root, f)], capture_output=True).returncode:
                bad.append(f)
    m["syntax_errors"] = bad
    env = {**os.environ, "STUDIO_SIM_ROOT": proj, "LUAU_COMPILE": luau_compile}
    msgs = "\n".join(json.dumps({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": n, "arguments": a}})
                     for i, (n, a) in enumerate([("start_stop_play", {"action": "start"}), ("get_console_output", {})], 1))
    out = subprocess.run(["python3", SIM], input=msgs + "\n", capture_output=True, text=True, env=env).stdout.splitlines()
    m["sim_console_errors_after"] = json.loads(out[-1])["result"]["content"][0]["text"].count("[Error]") if out else None
    return m


def run_arm(task, arm, model, luau_compile, unsynced=False):
    proj = make_project(arm)
    cfg = tempfile.mkdtemp(prefix="apex-cfg-")
    mcp = {"mcpServers": {"roblox_studio": {"command": "python3", "args": [SIM],
                                            "env": {"STUDIO_SIM_ROOT": proj, "LUAU_COMPILE": luau_compile,
                                                    "STUDIO_SIM_UNSYNCED": "1" if unsynced else "0"}}}}
    r = run_in(proj, task["prompt"], model, 40, 1500, allowed=EDIT[0], disallowed=EDIT[1],
               extra_args=["--mcp-config", json.dumps(mcp), "--strict-mcp-config"], env={"CLAUDE_CONFIG_DIR": cfg})
    r["diff"] = subprocess.run(["git", "-C", proj, "diff", "--", "src", "default.project.json"], capture_output=True, text=True).stdout
    new = subprocess.run(["git", "-C", proj, "ls-files", "--others", "--exclude-standard", "src"], capture_output=True, text=True).stdout.split()
    for f in new:
        r["diff"] += f"\n--- new file {f}\n" + open(os.path.join(proj, f)).read()
    r["process"] = process_metrics(r["tool_calls"], proj, luau_compile)
    r["arm"] = arm
    shutil.rmtree(proj, ignore_errors=True)
    return r


def judge(task, base, apex, model):
    fmt = lambda r: (f"{r['final_text']}\n\n[CODE CHANGES (git diff)]\n{r['diff'][:12000] or '(no code changes)'}\n\n"
                     f"[TOOLS USED, in order]\n{', '.join(c['tool'].split('__')[-1] for c in r['tool_calls'])[:1500]}")
    flip = random.random() < 0.5
    a, b = (apex, base) if flip else (base, apex)
    prompt = JUDGE_PROMPT.format(task=task["prompt"] + "\n(The assistant could read/edit the project files and use simulated Roblox Studio tools: playtest + console output. The simulator cannot run game logic or execute_luau.)",
                                 rubric="\n".join(f"- {x}" for x in task["rubric"]), a=fmt(a), b=fmt(b))
    d = tempfile.mkdtemp()
    p = subprocess.run(["claude", "-p", prompt, "--model", model, "--output-format", "json", "--max-turns", "1",
                        "--disallowedTools", "Bash Edit Write Read Glob Grep Skill WebFetch WebSearch Agent"],
                       cwd=d, capture_output=True, text=True, timeout=900)
    out = json.loads(p.stdout)
    txt = out.get("result", "")
    j, _ = json.JSONDecoder().raw_decode(txt[txt.index("{"):])
    ak, bk = ("A", "B") if flip else ("B", "A")
    pts = {"met": 1.0, "partial": 0.5, "missed": 0.0}
    sc = lambda k: round(sum(pts.get(i.get(k, "missed"), 0) for i in j["items"]) / max(1, len(j["items"])), 3)
    pref = j.get("preference", "tie")
    return {"apex_score": sc(ak), "base_score": sc(bk), "winner": "apex" if pref == ak else "baseline" if pref == bk else "tie",
            "reason": j.get("reason", ""), "apex_flags": j.get(f"{ak}_flags", {}), "base_flags": j.get(f"{bk}_flags", {}),
            "raw": j, "judge_cost": out.get("total_cost_usd")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--luau-compile", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default="opus")
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--sim-unsynced", action="store_true", help="Studio never receives file edits (Rojo/Script Sync not running)")
    a = ap.parse_args()
    tasks = [t for t in TASKS if not a.only or any(t["id"].startswith(x) for x in a.only.split(","))]
    out = os.path.join(HERE, "results", ("project-unsynced-" if a.sim_unsynced else "project-") + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out, exist_ok=True)
    runs = {}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        fut = {ex.submit(run_arm, t, arm, a.model, a.luau_compile, a.sim_unsynced): (t["id"], arm) for t in tasks for arm in ("baseline", "apex")}
        for f in cf.as_completed(fut):
            k = fut[f]
            runs[k] = f.result()
            json.dump(runs[k], open(f"{out}/{k[0]}.{k[1]}.json", "w"), indent=2)
            print(f"ran {k[0]} {k[1]} skills={runs[k]['skills_invoked']} proc={ {x: y for x, y in runs[k]['process'].items() if x != 'skills'} } ${runs[k]['cost_usd'] or 0:.2f}", flush=True)
    js = {}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        fut = {ex.submit(judge, t, runs[(t["id"], "baseline")], runs[(t["id"], "apex")], a.judge_model): t["id"] for t in tasks}
        for f in cf.as_completed(fut):
            try:
                js[fut[f]] = f.result()
            except Exception as e:
                js[fut[f]] = {"error": repr(e)}
            json.dump(js[fut[f]], open(f"{out}/{fut[f]}.judge.json", "w"), indent=2)
    yn = lambda v: "—" if v is None else ("yes" if v else "no")
    L = [f"# Project benchmark (Lighthouse fixture + Studio simulator), subject {a.model}, judge {a.judge_model}", "",
         "| task | arm | skills | rubric | inspect→edit | playtest after edit | console after edit | syntax errs | sim errors after | winner |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    cost, tally = 0.0, {"apex": 0, "baseline": 0, "tie": 0}
    for t in tasks:
        j = js[t["id"]]
        if "winner" in j:
            tally[j["winner"]] += 1
        for arm in ("baseline", "apex"):
            r, p = runs[(t["id"], arm)], runs[(t["id"], arm)]["process"]
            cost += r["cost_usd"] or 0
            L.append(f"| {t['id']} | {arm} | {', '.join(x.split(':')[-1] for x in r['skills_invoked']) or '—'} | "
                     f"{j.get(arm[:4] + '_score' if arm == 'apex' else 'base_score', '?')} | {yn(p.get('inspected_before_edit'))} | "
                     f"{yn(p.get('playtest_after_last_edit'))} | {yn(p.get('console_after_last_edit'))} | {len(p['syntax_errors'])} | "
                     f"{p['sim_console_errors_after']} | {j.get('winner', 'judge error') if arm == 'apex' else ''} |")
        cost += j.get("judge_cost") or 0
    L += ["", f"**Wins:** apex {tally['apex']} · baseline {tally['baseline']} · tie {tally['tie']} · total cost ${cost:.2f}", "", "## Judge reasons"]
    L += [f"- **{t['id']}** ({js[t['id']].get('winner')}): {js[t['id']].get('reason', js[t['id']].get('error'))}" for t in tasks]
    open(f"{out}/summary.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
