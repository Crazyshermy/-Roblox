#!/usr/bin/env python3
"""Studio-workflow SIMULATOR: a stdio MCP server that mimics the *tool surface* of Roblox Studio's
built-in MCP server over a Rojo project on disk. It is NOT Roblox Studio and never runs game logic.

Purpose: measure whether an agent follows a sound Studio workflow (inspect → edit → playtest →
read console → fix → re-verify → report honestly). Results from it are process evidence only and
must never be reported as E5 (live runtime) evidence.

Playtest console output is derived from:
  1. real Luau syntax checks (luau-compile, if LUAU_COMPILE points to it), and
  2. a small set of known runtime-error patterns (e.g. top-level `.Character.Humanoid` in a client script).
`execute_luau` and `screen_capture` honestly report that they are not supported.

Env: STUDIO_SIM_ROOT (project dir with default.project.json), LUAU_COMPILE (optional path).
"""
import json, os, re, subprocess, sys

ROOT = os.environ.get("STUDIO_SIM_ROOT", os.getcwd())
LUAU_COMPILE = os.environ.get("LUAU_COMPILE")
STATE = {"mode": "Edit", "console": [], "plays": 0}
SID = "sim-studio-1"

TOOLS = [
    ("list_roblox_studios", "List connected Roblox Studio instances.", {}),
    ("get_studio_state", "Get the current Studio mode (Edit/Play) for a studio_id.", {"studio_id": "string"}),
    ("search_game_tree", "Search the DataModel instance tree. Optional 'query' filters by name substring.", {"studio_id": "string", "query": "string"}),
    ("script_read", "Read a script's source by DataModel path (e.g. ServerScriptService.Server.OilService).", {"studio_id": "string", "path": "string"}),
    ("script_grep", "Search all scripts for a pattern (max 50 matches).", {"studio_id": "string", "pattern": "string"}),
    ("start_stop_play", "Start or stop a playtest. action: 'start' or 'stop'.", {"studio_id": "string", "action": "string"}),
    ("get_console_output", "Get Output window messages from the current/last playtest.", {"studio_id": "string"}),
    ("execute_luau", "Run Luau in a DataModel (datamodel_type: Edit, Server or Client).", {"studio_id": "string", "code": "string", "datamodel_type": "string"}),
    ("screen_capture", "Capture the Studio viewport.", {"studio_id": "string"}),
]


def scripts():
    """Map DataModel paths -> (file path, class) from the Rojo project's $path mappings."""
    proj = json.load(open(os.path.join(ROOT, "default.project.json")))
    out = {}

    def walk(node, dm_path):
        if isinstance(node, dict):
            if "$path" in node:
                base = os.path.join(ROOT, node["$path"])
                for dirpath, _, files in os.walk(base):
                    for f in sorted(files):
                        if not f.endswith((".lua", ".luau")):
                            continue
                        name = re.sub(r"\.(server|client)?\.?luau?$", "", f).rstrip(".")
                        cls = "Script" if ".server." in f else "LocalScript" if ".client." in f else "ModuleScript"
                        rel = os.path.relpath(os.path.join(dirpath, f), base).split(os.sep)[:-1]
                        out[".".join([dm_path] + rel + [name])] = (os.path.join(dirpath, f), cls)
            for k, v in node.items():
                if not k.startswith("$"):
                    walk(v, f"{dm_path}.{k}" if dm_path else k)

    walk(proj["tree"], "")
    return out


def tree_lines(query=""):
    proj = json.load(open(os.path.join(ROOT, "default.project.json")))
    lines = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("$"):
                    continue
                p = f"{path}.{k}" if path else k
                cls = v.get("$className", "Folder" if "$path" in v else "Instance") if isinstance(v, dict) else "?"
                lines.append(f"{p} ({cls})")
                walk(v, p)

    walk(proj["tree"], "")
    lines += [f"{p} ({c})" for p, (_, c) in scripts().items()]
    return [l for l in sorted(set(lines)) if query.lower() in l.lower()]


def playtest_console():
    out = ["[Studio] Playtest started (1 player: Player1)."]
    for dm, (fp, cls) in scripts().items():
        src = open(fp, encoding="utf-8").read()
        if LUAU_COMPILE:
            r = subprocess.run([LUAU_COMPILE, fp], capture_output=True, text=True)
            if r.returncode != 0:
                m = re.search(r"\((\d+),\d+\): (SyntaxError: .*)", r.stdout + r.stderr)
                out.append(f"[Error] {dm}:{m.group(1) if m else '?'}: {m.group(2) if m else 'syntax error'}")
                continue
        if cls == "LocalScript":
            for i, line in enumerate(src.splitlines(), 1):
                # top-level (unindented) direct index into Character before it exists
                if re.match(r"^local\s+\w+\s*=\s*[\w.]*\.Character\.(\w+)", line):
                    member = re.match(r"^local\s+\w+\s*=\s*[\w.]*\.Character\.(\w+)", line).group(1)
                    out.append(f"[Error] Players.Player1.PlayerScripts.{dm.split('StarterPlayerScripts.')[-1]}:{i}: attempt to index nil with '{member}'")
                    out.append(f"[Error] Stack Begin / Script '{dm}', Line {i} / Stack End")
                    break
    out.append("[Simulator] Note: this simulator performs syntax checks and detects a few known runtime-error "
               "patterns only. It does not execute game logic; absence of errors is not proof of correct behavior.")
    return out


def call(name, args):
    if name == "list_roblox_studios":
        return json.dumps([{"studio_id": SID, "name": "LighthouseKeeper (simulated)", "place_id": 0}])
    if name == "get_studio_state":
        return json.dumps({"mode": STATE["mode"]})
    if name == "search_game_tree":
        return "\n".join(tree_lines(args.get("query", ""))[:200]) or "(no matches)"
    if name == "script_read":
        p = args.get("path", "")
        s = scripts()
        hit = s.get(p) or next((v for k, v in s.items() if k.endswith(p) or v[0].endswith(p)), None)
        if not hit:
            return f"Script not found: {p}"
        return f"-- {p} ({hit[1]}), synced from {os.path.relpath(hit[0], ROOT)}\n" + open(hit[0], encoding="utf-8").read()
    if name == "script_grep":
        pat, res = args.get("pattern", ""), []
        for dm, (fp, _) in scripts().items():
            for i, line in enumerate(open(fp, encoding="utf-8").read().splitlines(), 1):
                if re.search(pat, line) or pat in line:
                    res.append(f"{dm}:{i}: {line.strip()}")
        return "\n".join(res[:50]) or "(no matches)"
    if name == "start_stop_play":
        if args.get("action", "start").lower().startswith("stop"):
            STATE["mode"] = "Edit"
            return "Playtest stopped."
        STATE["mode"] = "Play"
        STATE["plays"] += 1
        STATE["console"] = playtest_console()
        return "Playtest started."
    if name == "get_console_output":
        return "\n".join(STATE["console"]) if STATE["console"] else "(no output yet; start a playtest first)"
    if name == "execute_luau":
        return ("execute_luau is NOT supported by this simulator (no Roblox engine is running). "
                "Treat engine/runtime behavior as unverified.")
    if name == "screen_capture":
        return "screen_capture is NOT supported by this simulator (no renderer)."
    return f"Unknown tool {name}"


def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid, method = msg.get("id"), msg.get("method")
        if mid is None:
            continue  # notification
        if method == "initialize":
            res = {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-06-18"),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "roblox-studio-sim", "version": "0.1"}}
        elif method == "tools/list":
            res = {"tools": [{"name": n, "description": d + " (SIMULATED Studio)",
                              "inputSchema": {"type": "object", "properties": {k: {"type": t} for k, t in props.items()}}}
                             for n, d, props in TOOLS]}
        elif method == "tools/call":
            p = msg.get("params", {})
            res = {"content": [{"type": "text", "text": call(p.get("name"), p.get("arguments") or {})}]}
        elif method == "ping":
            res = {}
        else:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "not found"}}) + "\n")
            sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
