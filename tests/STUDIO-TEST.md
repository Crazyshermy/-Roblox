# Real Roblox Studio test (live Studio MCP)

**Live Roblox Studio: NOT VERIFIED — requires local Windows Roblox Studio validation.** This test has not been run yet. Roblox Apex was built in a Linux cloud container where Roblox Studio can't run. Everything below is prepared so that someone with Studio (Windows or macOS) can run it in about 30–45 minutes. Until it has been run, nothing in Roblox Apex is E5 (live-runtime) verified.

What has been verified instead:
- **Fixture validity:** all fixture scripts compile with the official Luau compiler, and Rojo 7.4.4 builds the place file.
- **Simulated Studio workflow:** in `benchmarks/project_run.py`, Apex followed the edit → playtest → console → report loop in every implementation task. The baseline never did.

The simulator imitates only Studio's *tool surface*. It is not Studio.

## Setup
1. Install Roblox Apex into an empty folder, e.g. `C:\ApexStudioTest`, using any method in the README. Copy `tests/fixtures/lighthouse/` into it, so the Rojo files are there for Claude to read and edit.
2. Open `tests/fixtures/LighthouseKeeper.rbxl` in Studio. It was built from the same fixture with Rojo 7.4.4. If you use Rojo, run `rojo serve` in the folder instead and connect, so file edits sync into Studio. **Without Rojo or Script Sync, Claude's file edits won't reach Studio.** Then either enable Script Sync, or tell Claude to edit through the Studio MCP tools.
3. In Studio: Assistant → ⋯ → Manage MCP Servers → enable **Studio as MCP server**. Connect Claude Code (quick-connect, or `claude mcp add` with the command from the Studio docs).
4. Start Claude Code in the folder, then run `/roblox-status`. It should report **Studio MCP: connected**. If not, stop and fix the connection first.
5. Run `/roblox-init Co-op lighthouse keepers keep the lamp burning through a storm night.`

## The 10 steps
For each step, record what Claude actually did (tools called) and the outcome in the table at the bottom. **Expected Apex behavior** is what the skills should cause. Deviations are findings.

| # | Prompt to give Claude | Expected Apex behavior |
|---|---|---|
| 1 | "Inspect this Roblox project and summarize what's in it." | Uses `list_roblox_studios`/`search_game_tree`/`script_read` (or the files). Gives an accurate inventory and doesn't invent instances. |
| 2 | "Explain the architecture: who owns what state and how it flows between server and client." | Server services, remotes, the leaderstats-as-truth problem, the per-second `FireAllClients`. Route line names architecture/networking. |
| 3 | "Players say the HUD errors after respawning. Fix it." | Reads HUD, edits it (CharacterAdded rebinding, `ResetOnSpawn=false`), and makes no unrelated rewrites. |
| 4 | (continues 3) | **Without being asked:** confirms Studio has the edited code (`script_read` or `script_grep` for the changed line) and, because this game saves data, asks once whether playtests use a test place or store. Then it starts a playtest. **Extra check:** stop `rojo serve` and repeat step 3. Claude should detect that Studio lacks the edit and refuse to count the playtest. |
| 5 | (continues 3) | Reads `get_console_output` and reports the actual console lines. |
| 6 | If errors appear: "Fix what the console shows." | Corrects them from the console evidence, not by guessing. |
| 7 | "Respawn the character during a playtest and confirm the HUD still works." | Uses `execute_luau` **in the Server or Client DataModel during the playtest, not Edit** (Server: `LoadCharacter` or set Health to 0), then reads the HUD state via Client `execute_luau` or a screenshot. Ends with `Verified: … · Not verified: …`. |
| 8 | "Security-review the refuel system, then fix it." | Loads security. Finds the negative/NaN amount, missing balance check, range check, rate limit and leaderstats truth. Ideally reproduces an exploit with Client-side `execute_luau` (`FireServer(-1e9)`) before and after the fix. |
| 9 | "Review the game design: is this worth playing? What should the lamp going dark do?" | Fantasy-first and co-op interdependence, no pets, coins or rebirth defaults, includes how to playtest the idea. |
| 10 | "Review the visuals and the feel of refueling, and improve the refuel feel." | Uses `screen_capture` for visual claims. Lighting advice uses `LightingStyle`, not deprecated `Technology`. Refuel gets instant client feedback and works on touch and gamepad. Playtests afterwards. |

## What to record (copy into `docs/BENCHMARKS.md` → "Live Studio results")
| Step | Tools Claude called | Outcome | Matched expectation? | Notes / defect found |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3–6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

Also record: the Studio version, the Claude Code version, the model, any Studio MCP tool names or parameters that differ from `roblox/references/studio-mcp.md` (update that file), and any skill guidance that was wrong in practice. Each defect you find should become a skill fix plus a smoke or benchmark case.
