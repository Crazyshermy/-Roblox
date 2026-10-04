#!/usr/bin/env python3
"""Fresh-install acceptance test. Clones Roblox Apex from GitHub (not this workspace), installs it
into a fresh copy of the Lighthouse fixture game with an ISOLATED Claude config directory, then runs
fresh headless sessions for every command and for automatic routing.

Usage: python3 tests/install_test.py [--ref main] [--method project|plugin|both] [--model sonnet]
Writes tests/results/install-<time>/report.md and per-session JSON.
"""
import argparse, datetime, json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_case import run_in  # noqa: E402

REPO_URL = "https://github.com/Crazyshermy/-Roblox.git"
REPO_SLUG = "Crazyshermy/-Roblox"
HERE = os.path.dirname(os.path.abspath(__file__))
SPECIALISTS = ["roblox-architecture", "roblox-assets", "roblox-boundary-breaker", "roblox-data", "roblox-debugging",
               "roblox-game-design", "roblox-game-feel", "roblox-genres", "roblox-level-design", "roblox-luau",
               "roblox-networking", "roblox-performance", "roblox-physics-animation", "roblox-review", "roblox-security",
               "roblox-testing", "roblox-ui-ux", "roblox-visual-direction"]
VERSION = __import__("re").search(r"version: (\S+)", open(os.path.join(os.path.dirname(HERE), ".claude", "skills", "roblox", "SKILL.md")).read()).group(1)
WRITE_TOOLS = ("Skill Read Glob Grep Write Edit", "Bash WebFetch WebSearch Agent")


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def fresh_game(src_fixture):
    d = tempfile.mkdtemp(prefix="apex-game-")
    shutil.copytree(src_fixture, d, dirs_exist_ok=True)
    sh(["git", "init", "-q", d])
    return d


def norm(names):
    return {n.split(":")[-1] for n in names}


def project_method(ref, model, out, checks):
    cfg = tempfile.mkdtemp(prefix="apex-cfg-")
    env = {"CLAUDE_CONFIG_DIR": cfg}
    clone = tempfile.mkdtemp(prefix="apex-clone-")
    sh(["git", "clone", "-q", "--depth", "1", "-b", ref, REPO_URL, clone])
    game = fresh_game(os.path.join(clone, "tests", "fixtures", "lighthouse"))
    inst = sh([os.path.join(clone, "install", "install.sh"), game]).stdout.strip()
    checks.append(("project: install.sh", "Installed Roblox Apex" in inst, inst.splitlines()[0]))

    s = run_in(game, "/roblox-status", model, 15, 600, env=env)
    json.dump(s, open(f"{out}/project-status.json", "w"), indent=2)
    disc = norm(s["skills_available"] or [])
    checks.append(("project: all 22 skills discovered in fresh session", len(disc) == 22 and set(SPECIALISTS) <= disc, f"{len(disc)} discovered"))
    checks.append(("project: /roblox-status reports version", VERSION in s["final_text"], s["final_text"][:120].replace("\n", " ")))

    r = run_in(game, "/roblox-route Build a secure player trading system", model, 8, 600, env=env)
    json.dump(r, open(f"{out}/project-route.json", "w"), indent=2)
    t = r["final_text"]
    checks.append(("project: /roblox-route names security+data+networking", all(x in t for x in ("roblox-security", "roblox-data", "roblox-networking")), ""))
    checks.append(("project: /roblox-route does not execute (no specialist loaded)", not r["skills_invoked"], str(r["skills_invoked"])))

    i = run_in(game, "/roblox-init Co-op night-shift lighthouse keepers keep the lamp burning through a storm.", model, 25, 900,
               allowed=WRITE_TOOLS[0], disallowed=WRITE_TOOLS[1], env=env)
    json.dump(i, open(f"{out}/project-init.json", "w"), indent=2)
    apex_files = [f for f in ("project.md", "decisions.md", "debt.md") if os.path.isfile(os.path.join(game, ".apex", f))]
    claude_md = open(os.path.join(game, "CLAUDE.md")).read() if os.path.isfile(os.path.join(game, "CLAUDE.md")) else ""
    checks.append(("project: /roblox-init created .apex/ memory", len(apex_files) == 3, str(apex_files)))
    checks.append(("project: /roblox-init added CLAUDE.md block", "## Roblox Apex" in claude_md, ""))

    a = run_in(game, "Where should a new storm-intensity system live in this project, and how should clients learn the "
                     "current storm level? Keep it short.", model, 12, 600, env=env)
    json.dump(a, open(f"{out}/project-auto-architecture.json", "w"), indent=2)
    inv = norm(a["skills_invoked"])
    checks.append(("project: auto-routing (no prefix) loads router/architecture", bool(inv & {"roblox", "roblox-architecture", "roblox-networking"}), str(a["skills_invoked"])))
    checks.append(("project: CLAUDE.md + .apex memory consulted", any(".apex/" in f for f in a["files_read"]), str(a["files_read"])))

    x = run_in(game, "/roblox Review the RefuelLamp remote handler for exploits. Findings only, no code.", model, 12, 600, env=env)
    json.dump(x, open(f"{out}/project-roblox-security.json", "w"), indent=2)
    checks.append(("project: /roblox routes security review to roblox-security", "roblox-security" in norm(x["skills_invoked"]), str(x["skills_invoked"])))
    checks.append(("project: security review finds negative/untrusted amount", any(w in x["final_text"].lower() for w in ("negative", "-1e", "-math.huge")), ""))
    return [s, r, i, a, x]


def plugin_method(ref, model, out, checks):
    cfg = tempfile.mkdtemp(prefix="apex-cfg-")
    env = {**os.environ, "CLAUDE_CONFIG_DIR": cfg}
    work = tempfile.mkdtemp()
    m = subprocess.run(["claude", "plugin", "marketplace", "add", f"{REPO_SLUG}#{ref}"], cwd=work, env=env, capture_output=True, text=True, timeout=180)
    p = subprocess.run(["claude", "plugin", "install", "roblox-apex@roblox-apex"], cwd=work, env=env, capture_output=True, text=True, timeout=180)
    checks.append(("plugin: marketplace add + install from GitHub", m.returncode == 0 and p.returncode == 0, (m.stdout + p.stdout)[-160:].replace("\n", " ")))
    clone = tempfile.mkdtemp(prefix="apex-clone-")
    sh(["git", "clone", "-q", "--depth", "1", "-b", ref, REPO_URL, clone])
    game = fresh_game(os.path.join(clone, "tests", "fixtures", "lighthouse"))  # no .claude/skills here
    s = run_in(game, "/roblox-status", model, 15, 600, env={"CLAUDE_CONFIG_DIR": cfg})
    json.dump(s, open(f"{out}/plugin-status.json", "w"), indent=2)
    checks.append(("plugin: skills discovered (namespaced)", len(s["skills_available"] or []) == 22 and all(x.startswith("roblox-apex:") for x in s["skills_available"]), f"{len(s['skills_available'] or [])}"))
    checks.append(("plugin: bare /roblox-status works", VERSION in s["final_text"], s["final_text"][:100].replace("\n", " ")))
    a = run_in(game, "Review the RefuelLamp handler in src/server/OilService.luau for exploits. Findings only.", model, 12, 600, env={"CLAUDE_CONFIG_DIR": cfg})
    json.dump(a, open(f"{out}/plugin-auto-security.json", "w"), indent=2)
    checks.append(("plugin: auto-routing reaches namespaced security skill", "roblox-security" in norm(a["skills_invoked"]), str(a["skills_invoked"])))
    return [s, a]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main")
    ap.add_argument("--method", default="both", choices=["project", "plugin", "both"])
    ap.add_argument("--model", default="sonnet")
    a = ap.parse_args()
    out = os.path.join(HERE, "results", "install-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out, exist_ok=True)
    checks, runs = [], []
    if a.method in ("project", "both"):
        runs += project_method(a.ref, a.model, out, checks)
    if a.method in ("plugin", "both"):
        runs += plugin_method(a.ref, a.model, out, checks)
    cost = sum(r.get("cost_usd") or 0 for r in runs)
    lines = [f"# Fresh-install test (ref `{a.ref}`, model {a.model})", "", "| check | result | detail |", "|---|---|---|"]
    lines += [f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n, ok, d in checks]
    lines += ["", f"Session cost: ${cost:.2f}"]
    open(os.path.join(out, "report.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(0 if all(ok for _, ok, _ in checks) else 1)


if __name__ == "__main__":
    main()
