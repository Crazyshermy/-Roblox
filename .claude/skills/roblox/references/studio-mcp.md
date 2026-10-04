# Using Roblox Studio tools (knowledge, not implementation)

Roblox Studio ships a built-in MCP server (Assistant → … → Manage MCP Servers → "Enable Studio as MCP server"). In Claude Code, these tools usually appear as `mcp__<server>__<tool>`. Every call needs a `studio_id`, which you get from `list_roblox_studios`. **Don't rebuild what these tools already do.** (E4, `studio/mcp.md`, 2026-10.)

| Need | Tool | Notes |
|---|---|---|
| Which Studio or place am I on? | `list_roblox_studios`, `get_studio_state` | Confirm the place before any edit when several Studios are open. |
| Find code | `script_search` (name, ≤ 10 results), `script_grep` (pattern, ≤ 50 matches) | Grep for remotes (`RemoteEvent`, `OnServerEvent`), DataStore calls, and so on. |
| Read and edit code | `script_read`, `multi_edit` (creates if missing) | Read the whole script before editing it. |
| Inspect the world | `search_game_tree`, `inspect_instance` | Check real hierarchy and properties instead of assuming them. |
| Probe engine behavior or state | `execute_luau` (`datamodel_type`: Edit/Server/Client) | The cheapest path to **E5**. Probe an uncertain API, read live values, assert invariants. |
| Run the game | `start_stop_play`, then `get_console_output` | Always read console output after a playtest. A silent failure is still a failure. |
| See it | `screen_capture` | Use for visual, UI and feel claims, after cheaper checks. Images are expensive. |
| Act like a player | `character_navigation`, `user_keyboard_input`, `user_mouse_input` | Smoke-test interactions and UI flows. |
| Docs and Roblox skills | `http_get` (Roblox docs), `skill` (e.g. `rbx-perf-profiling`, `rbx-debug`, `rbx-unit-test`, `rbx-docs-search`) | Use these to verify current APIs. Don't guess. |
| Assets | `search_asset`, `insert_asset`, `generate_mesh`/`generate_material`/`generate_procedural_model` + `wait_job_finished` | **Vet inserted assets** (see `roblox-security`). |

## When to use what
- **Before editing:** search and read the relevant scripts. Inspect the instances they reference.
- **Uncertain API or engine behavior:** probe it with `execute_luau` in Edit or Server, rather than reasoning from memory.
- **After a change:** playtest → console output → (navigate/input) → screenshot if the claim is visual. For multiplayer claims, a solo playtest is **not** sufficient evidence. Say so, and use Server & Clients (manual, or a test harness).
- **Performance claims:** measure (Roblox `rbx-perf-profiling` skill, MicroProfiler, Developer Console Stats) before and after. Never claim a speedup you didn't measure.

## When Studio isn't connected (files only, or text only)
- Work from the Rojo or Script Sync tree, and use `luau-lsp`/`selene`/`StyLua` if the project has them.
- Pure logic can be unit-tested (Jest-Lua/TestEZ) or run headless (Lune, or Open Cloud Luau Execution if the project already uses it).
- State plainly which behavior is **unverified at runtime**, and give the exact playtest steps that would verify it.
