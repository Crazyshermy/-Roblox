#!/usr/bin/env python3
"""Run one prompt through a real headless Claude Code session and report which skills it used.

Usage:
  python3 tests/run_case.py --prompt "/roblox ..." [--mode apex|baseline] [--model sonnet] [--out DIR]

- mode=apex      : temp project with Roblox Apex skills installed into .claude/skills
- mode=baseline  : temp project with no Apex skills (control)

Writes <out>/<name>.json containing: skills_invoked (from real Skill tool_use events),
files_read (Read tool paths, to observe progressive disclosure), final_text, cost_usd, turns.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_SRC = os.path.join(REPO, ".claude", "skills")


def make_project(mode: str, fixture: str | None) -> str:
    d = tempfile.mkdtemp(prefix=f"apex-{mode}-")
    subprocess.run(["git", "init", "-q", d], check=True)
    if mode == "apex":
        dst = os.path.join(d, ".claude", "skills")
        os.makedirs(dst)
        for name in os.listdir(SKILLS_SRC):
            if name.startswith("roblox"):
                shutil.copytree(os.path.join(SKILLS_SRC, name), os.path.join(dst, name))
        tpl = os.path.join(SKILLS_SRC, "roblox-init", "templates", "CLAUDE-block.md")
        if os.path.exists(tpl):
            shutil.copy(tpl, os.path.join(d, "CLAUDE.md"))
    if fixture:
        src = os.path.join(REPO, "tests", "fixtures", fixture)
        shutil.copytree(src, d, dirs_exist_ok=True)
    return d


READ_ONLY = ("Skill Read Glob Grep", "Bash Edit Write WebFetch WebSearch Agent")


def run_in(proj: str, prompt: str, model: str, max_turns: int = 12, timeout: int = 600,
           allowed: str = READ_ONLY[0], disallowed: str = READ_ONLY[1],
           extra_args: list | None = None, env: dict | None = None) -> dict:
    """Run one headless session in an existing project dir and parse the event stream."""
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--model", model, "--max-turns", str(max_turns),
           "--allowedTools", allowed, "--disallowedTools", disallowed] + (extra_args or [])
    t0 = time.time()
    p = subprocess.run(cmd, cwd=proj, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, **(env or {})})
    skills, reads, calls, text, cost, turns, available = [], [], [], "", None, None, None
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            available = sorted(s for s in ev.get("skills", []) if "roblox" in s)
        if ev.get("type") == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") != "tool_use":
                    continue
                inp = c.get("input", {})
                calls.append({"tool": c["name"], "input": {k: (v[:200] if isinstance(v, str) else v) for k, v in inp.items()}})
                if c["name"] == "Skill":
                    skills.append(inp.get("skill") or inp.get("command"))
                if c["name"] == "Read":
                    reads.append(os.path.relpath(inp.get("file_path", ""), proj))
        if ev.get("type") == "result":
            text = ev.get("result", "")
            cost = ev.get("total_cost_usd")
            turns = ev.get("num_turns")
    # A slash-command invocation by the user is expanded by the harness, not a Skill tool call.
    user_slash = prompt.strip().split()[0][1:] if prompt.strip().startswith("/") else None
    return {"model": model, "prompt": prompt, "user_slash_command": user_slash,
            "skills_available": available, "skills_invoked": skills, "files_read": reads,
            "tool_calls": calls, "final_text": text, "cost_usd": cost, "turns": turns,
            "seconds": round(time.time() - t0, 1), "stderr_tail": p.stderr[-500:]}


def run(prompt: str, mode: str, model: str, fixture: str | None, max_turns: int, timeout: int) -> dict:
    proj = make_project(mode, fixture)
    try:
        r = run_in(proj, prompt, model, max_turns, timeout)
    finally:
        shutil.rmtree(proj, ignore_errors=True)
    r["mode"] = mode
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--mode", default="apex", choices=["apex", "baseline"])
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--fixture", default=None)
    ap.add_argument("--name", default="case")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-turns", type=int, default=12)
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()
    r = run(a.prompt, a.mode, a.model, a.fixture, a.max_turns, a.timeout)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, f"{a.name}.{a.mode}.json"), "w") as f:
            json.dump(r, f, indent=2)
    print(json.dumps({k: r[k] for k in ("mode", "skills_available", "skills_invoked", "files_read", "cost_usd", "turns", "seconds")}, indent=2))
    print("----- FINAL TEXT (first 1500 chars) -----")
    print(r["final_text"][:1500])
