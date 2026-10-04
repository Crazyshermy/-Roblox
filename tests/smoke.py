#!/usr/bin/env python3
"""Roblox Apex smoke test: real headless Claude Code sessions, checked for (1) which skills were
actually invoked (Skill tool events) and (2) behavioral markers in the answer that come from
skill content. Runs cases in parallel.

Usage: python3 tests/smoke.py [--model sonnet] [--only id1,id2] [--with-baseline]
Results: tests/results/smoke-<timestamp>/  (JSON per case + summary.md)
Cost: roughly $0.15–0.60 per case with Sonnet.
"""
import argparse, concurrent.futures as cf, datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_case import run

CASES = [
    {
        "id": "status",
        "why": "/roblox-status works and the session really discovers the skills",
        "prompt": "/roblox-status",
        "expect_skills_any": [],  # user slash command: expanded by harness, not a Skill tool call
        "must": [r"\b1\.\d+\.\d+\b", r"roblox-security", r"roblox-game-design", r"(?i)inventory: complete", r"(not connected|Studio MCP)"],
        "must_not": [],
    },
    {
        "id": "router-entry",
        "why": "/roblox routes an architecture task to the right specialists and prints the route",
        "prompt": "/roblox I'm starting a round-based team game (lobby -> intermission -> round -> results). "
                  "Where should the round state machine, team assignment and scoring live, and how should clients learn the round state? Keep it concise.",
        "expect_skills_all": ["roblox-architecture"],
        "expect_skills_any": ["roblox-networking"],
        "must": [r"\*Apex: |Apex:", r"(?i)attribute", r"(?i)late[- ]?join|join(s|ing)? mid|already in the game|existing players|GetPlayers"],
        "must_not": [],
    },
    {
        "id": "security-auto",
        "why": "No /roblox prefix: security review must auto-route and apply the handler contract",
        "prompt": "Is this Roblox server code safe?\n```lua\nTradeRemote.OnServerEvent:Connect(function(plr, otherPlayer, itemId, coins)\n"
                  "  local data = Profiles[plr]\n  if data.Coins >= coins then\n    local ok = DataStore:UpdateAsync(...)\n"
                  "    data.Coins -= coins\n    Profiles[otherPlayer].Coins += coins\n    giveItem(otherPlayer, itemId)\n  end\nend)\n```",
        "expect_skills_any": ["roblox-security", "roblox"],
        "must": [r"(?i)nan|x ~= x|math\.huge|inf", r"(?i)yield", r"(?i)negative", r"(?i)rate[- ]?limit|spam|throttl", r"(?i)confirm|both (players|parties)|consent"],
        "must_not": [],
    },
    {
        "id": "design-auto",
        "why": "No /roblox prefix: design request must trigger anti-slop reasoning and fantasy-first design",
        "prompt": "I'm making a Roblox horror game where you play a lighthouse keeper alone on an island during storms. "
                  "Suggest a progression system for it. Keep it under 400 words.",
        "expect_skills_any": ["roblox-game-design", "roblox-genres", "roblox"],
        "must": [r"(?i)fantasy|pillar", r"(?i)why|belong|serve"],
        # genre defaults may appear only when explicitly rejected ("No coins, pets, rebirths...")
        "must_not": [r"(?im)^(?!.*\b(no|avoid|skip|not|without|instead|reject|cut|drop|remove|never)\b).*\b(egg hatch|rebirth)"],
    },
    {
        "id": "debug-auto",
        "why": "No /roblox prefix: debugging should identify the respawn stale-reference class and use hypotheses",
        "prompt": "My Roblox LocalScript sometimes errors 'attempt to index nil with Humanoid' but only after the player respawns. "
                  "It's in StarterPlayerScripts and does `local hum = player.Character.Humanoid` at the top. What's wrong?",
        "expect_skills_any": ["roblox-debugging", "roblox"],
        "must": [r"CharacterAdded", r"(?i)respawn|new character|old character|stale"],
        "must_not": [],
    },
    {
        "id": "currency",
        "why": "Currentness: DataStore budgets changed in 2026; stale answer is 60 + players x 10",
        "prompt": "/roblox What is the DataStore request budget per minute for GetAsync and SetAsync right now? Short answer.",
        "expect_skills_any": [],
        "expect_reads_any": ["currency.md", "roblox-data"],
        "must": [r"300", r"(?:CCU|concurrent|users)\s*[×x\*]\s*40", r"(?:players|numPlayers)\s*[×x\*]\s*40"],
        # stale figure may only appear when explicitly refuted as outdated
        "must_not": [r"(?i)^(?!.*(outdated|old|stale|no longer|not)).*(players|numPlayers)\s*[×x\*]\s*10\b"],
    },
    {
        "id": "trivial",
        "why": "Proportionality: a trivial script must not trigger a heavy multi-skill process or essay",
        "prompt": "Write a Roblox script that makes a part slowly spin.",
        "expect_skills_any": [],
        "max_specialists": 1,
        "max_chars": 2500,
        "must": [r"(?i)RunService|TweenService|AngularVelocity|HingeConstraint|CFrame"],
        "must_not": [],
    },
    {
        "id": "ambition",
        "why": "Creative ambition: 'Roblox can't do X, let's simplify' must trigger boundary-breaker, not agreement",
        "prompt": "For my Roblox game I wanted players to rewind time for 5 seconds (enemies and projectiles move backwards), "
                  "but Roblox obviously can't do that, so I'll just make it a cooldown-reset ability instead. Good plan?",
        "expect_skills_any": ["roblox-boundary-breaker"],
        "must": [r"(?i)snapshot|record|buffer|history", r"(?i)option|approach"],
        "must_not": [r"(?i)^\s*(yes|good plan|sounds good)[.!,]"],
    },
    {
        "id": "security-nomd",
        "mode": "apex-nomd",
        "why": "Plugin users who never ran /roblox-init: no CLAUDE.md block, security must still auto-route",
        "prompt": "Review this Roblox handler for exploits, findings only: RefuelLamp.OnServerEvent:Connect(function(player, amount) "
                  "player.leaderstats.Oil.Value -= amount; LampService.addFuel(amount) end)",
        "expect_skills_any": ["roblox-security"],
        "must": [r"(?i)negative", r"(?i)nan|math\.huge|inf"],
        "must_not": [],
    },
    {
        "id": "route-inspect",
        "why": "/roblox-route explains routing for a trading system without executing it",
        "prompt": "/roblox-route Build a secure player trading system",
        "expect_skills_any": [],
        "must": [r"roblox-security", r"roblox-data", r"roblox-networking", r"(?i)skipped|skip"],
        "must_not": [],
    },
]


def check(case, r):
    res = {"skills_ok": True, "markers_ok": True, "missing": [], "forbidden": []}
    inv = set(r["skills_invoked"])
    if case.get("expect_skills_all") and not set(case["expect_skills_all"]) <= inv:
        res["skills_ok"] = False
    if case.get("expect_skills_any") and not (set(case["expect_skills_any"]) & inv):
        res["skills_ok"] = False
    if case.get("expect_reads_any"):
        seen = " ".join(r["files_read"]) + " " + " ".join(r["skills_invoked"])
        if not any(x in seen for x in case["expect_reads_any"]):
            res["skills_ok"] = False
    specialists = [s for s in r["skills_invoked"] if s and s.split(":")[-1] != "roblox"]
    if "max_specialists" in case and len(specialists) > case["max_specialists"]:
        res["skills_ok"] = False
        res["missing"].append(f"<= {case['max_specialists']} specialists (got {len(specialists)})")
    text = r["final_text"]
    if "max_chars" in case and len(text) > case["max_chars"]:
        res["markers_ok"] = False
        res["missing"].append(f"<= {case['max_chars']} chars (got {len(text)})")
    for pat in case["must"]:
        if not re.search(pat, text):
            res["markers_ok"] = False
            res["missing"].append(pat)
    for pat in case["must_not"]:
        if re.search(pat, text, re.M):
            res["markers_ok"] = False
            res["forbidden"].append(pat)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--only", default="")
    ap.add_argument("--with-baseline", action="store_true", help="also run each case without Apex for contrast")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    cases = [c for c in CASES if not a.only or c["id"] in a.only.split(",")]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", f"smoke-{stamp}")
    os.makedirs(out, exist_ok=True)
    jobs = [(c, c.get("mode", "apex")) for c in cases] + ([(c, "baseline") for c in cases if not c["prompt"].startswith("/roblox-")] if a.with_baseline else [])
    results = {}
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(run, c["prompt"], mode, a.model, None, 12, 600): (c, mode) for c, mode in jobs}
        for f in cf.as_completed(futs):
            c, mode = futs[f]
            r = f.result()
            r["check"] = check(c, r)
            results[(c["id"], mode)] = r
            json.dump(r, open(os.path.join(out, f"{c['id']}.{mode}.json"), "w"), indent=2)
            ok = r["check"]["skills_ok"] and r["check"]["markers_ok"]
            print(f"[{'PASS' if ok else 'FAIL'}] {c['id']:<14} {mode:<8} skills={r['skills_invoked']} "
                  f"missing={r['check']['missing']} forbidden={r['check']['forbidden']} ${r['cost_usd'] or 0:.2f}", flush=True)
    lines = [f"# Smoke test {stamp} (model: {a.model})", "", "| case | mode | skills invoked | skills ok | markers ok | cost |", "|---|---|---|---|---|---|"]
    total = 0.0
    for c in cases:
        for mode in ("apex", "apex-nomd", "baseline"):
            r = results.get((c["id"], mode))
            if not r:
                continue
            total += r["cost_usd"] or 0
            lines.append(f"| {c['id']} | {mode} | {', '.join(r['skills_invoked']) or '—'} | {r['check']['skills_ok']} | {r['check']['markers_ok']} | ${r['cost_usd'] or 0:.2f} |")
    lines += ["", f"Total cost: ${total:.2f}", "", "Case intents:"] + [f"- **{c['id']}**: {c['why']}" for c in cases]
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    apex_fail = [k for k, r in results.items() if k[1] != "baseline" and not (r["check"]["skills_ok"] and r["check"]["markers_ok"])]
    sys.exit(1 if apex_fail else 0)


if __name__ == "__main__":
    main()
