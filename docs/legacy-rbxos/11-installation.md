# 11: Installation (T): One Installation, Honest Edition

## T.1 What "one installation" can realistically mean
**One install command plus guided consent clicks that Roblox requires.** These cannot be automated without bypassing Roblox's own safety prompts, and we should not try:
1. Enable *Studio as MCP server* (Assistant → Manage MCP Servers). This is one toggle.
2. Approve the companion plugin's HTTP access to `localhost`. Studio prompts on first request.
3. Approve screenshot capture (`StudioCaptureService:RequestScreenshotPermissionAsync`).
4. *(Optional, later)* Create Open Cloud API keys on the Creator Hub for live features.

Everything else is automated.

## T.2 Entry points

```bash
# Inside Claude Code (primary)
/plugin marketplace add rbxos/rbxos
/plugin install rbxos@rbxos
# Equivalent shell one-liner (CI/scripts): the installer calls `claude plugin` under the hood
curl -fsSL https://get.rbxos.dev | sh        # verifies signature, then runs the same steps
```

## T.3 Bootstrap sequence (`SessionStart` → `rbxos doctor --bootstrap`, idempotent)

```
1. Platform detect: OS/arch; Studio presence (Win: %LOCALAPPDATA%\Roblox\Versions, mac: /Applications/RobloxStudio.app)
   → if no Studio (Linux/cloud): configure HEADLESS profile; skip 3–6.
2. Binary: plugin bin/rbxos shim downloads the platform binary into ${CLAUDE_PLUGIN_DATA}/bin,
   verifies minisign/sigstore signature + sha256 pinned in the plugin release manifest.
3. Studio companion plugin: build RBXOS.rbxm with per-install token → copy to Studio Plugins folder
   (Win: %LOCALAPPDATA%\Roblox\Plugins, mac: ~/Documents/Roblox/Plugins); token → OS keychain.
4. Built-in MCP: detect enablement (gateway probes StudioMCP; Studio reports via plugin hello).
   If disabled → show 1-step instructions; plugin dock widget shows the same with a button that
   opens Assistant settings where possible.
5. Duplicate check: if Roblox_Studio is also configured directly in Claude Code → offer removal.
6. Toolchain: ensure luau-lsp, selene, StyLua, Lune, Rojo (if the project uses it), luau-analyze —
   via rokit if present, else pinned downloads into ${CLAUDE_PLUGIN_DATA}/tools (checksummed).
   Never modifies the user's global toolchain without asking.
7. Daemon: start on demand; register as login service only if user opts in.
8. Knowledge pack: unpack bundled pack; fetch K1 for current Studio API dump version.
9. Report: one table of green/yellow/red items with exact next actions.
```

## T.4 Project initialization (`/roblox init`, which is `roblox-init`, user-invoked)
1. **Identify:** bind to the open Studio's `{universe_id, place_id}` via the bridge, or to a Rojo project file, or prompt.
2. **Detect the sync provider:** Rojo (`*.project.json`), Script Sync (folders with sync metadata), or none. Recommend, never force:
   - Existing Rojo stays Rojo.
   - A Studio-first project gets Script Sync for code.
   - A new project gets Rojo.
3. **Generate the mirror** (if none): `.rbxos/mirror/` sources plus `sourcemap.json` for luau-lsp.
4. **Index** (Brain L1 → L2), runtime-free.
5. **Baseline:**
   - static gates
   - guardian metrics
   - remote table
   - a 60-second smoke playtest (solo) for errors and a perf baseline
   - UI device matrix (desktop and phone)
   - asset inventory and permission check
   - security static scan
6. **Constitution draft:** inferred from the game (genre signals, existing UI style, systems) plus **a 6-question interview**: vision, core fantasy, audience, phase, refusals, risk appetite. The user approves.
7. **Write `.rbxos/`** and the `CLAUDE.md` snippet (≤ 6 lines) and the `/roblox` project shim skill. Add `.rbxos/cache/` to `.gitignore`.
8. **Report:** `.rbxos/reports/baseline-<date>.md` with a risk list and opportunity list. Claude receives only the 15-line summary.

## T.5 Upgrades
- The plugin version pins the binary, runtime-lib, companion-plugin, and knowledge-pack versions (a lockstep release manifest).
- `doctor` detects version skew, for example when Studio still has an old companion plugin, and fixes it.
- The bridge protocol negotiates capabilities so mixed versions degrade instead of breaking.

## T.6 Uninstall
`rbxos uninstall` removes:
- the Studio plugin file
- the daemon login item
- keychain entries
- `${CLAUDE_PLUGIN_DATA}`, unless `--keep-data`

Project `.rbxos/` folders are left untouched. They belong to the user's repositories.

## T.7 Profiles
| Profile | Where | Capabilities |
|---|---|---|
| `local-full` | Windows or macOS with Studio | Everything |
| `headless` | Linux, Claude Code on the web, containers | Brain from files and mirror, static gates, Lune tests, Open Cloud Luau Execution, analytics, configs, experiments. **No** visual, input, multiplayer, or live-DataModel features (reported as `unknown`, never faked). |
| `ci` | GitHub Actions and similar | `rbxos ci`: static → unit → upload to dev place → Luau Execution suites → gates report (JUnit, Markdown) |
