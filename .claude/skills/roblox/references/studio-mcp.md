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
| See it | `screen_capture` (`camera_position`, `look_at_position`) | Use for visual, UI and feel claims, after cheaper checks. Images are expensive. For visual tuning (brightness, contrast, overlap), measure pixel statistics from screenshots instead of eyeballing them. |
| Act like a player | `character_navigation`, `user_keyboard_input`, `user_mouse_input` | Smoke-test interactions and UI flows. |
| Docs and Roblox skills | `http_get` (Roblox docs), `skill` (Roblox-authored guides. Names observed in 2026 include `rbx-perf-profiling`, `rbx-debug` and `rbx-unit-test`, but they aren't documented and may change, so list what is available at runtime) | Use these to verify current APIs. Don't guess. |
| Assets | `search_asset`, `insert_asset`, `generate_mesh`/`generate_material`/`generate_procedural_model` + `wait_job_finished` | **Vet inserted assets** (see `roblox-security`). |

## When to use what
- **Before editing:** search and read the relevant scripts. Inspect the instances they reference.
- **Every call needs a `studio_id`:** get it from `list_roblox_studios`. With several Studios open, confirm the place name first.
- **Uncertain API or engine behavior:** probe with `execute_luau` rather than reasoning from memory. Prefer the **Server or Client DataModel during a playtest**. Edit-DataModel code changes the saved place, so keep Edit-mode probes read-only unless the change is intended (and then tell the user).
- **Did my edit reach Studio?** After editing files, `script_read` or `script_grep` for a changed line before playtesting. A playtest of stale code verifies nothing.
- **Playtests can write real data.** With "Enable Studio Access to API Services" on, a playtest's DataStore writes hit the experience's real stores. If the game saves data and it's unknown whether playtests use a test place or store, ask once before the first playtest, then record the answer in `.apex/project.md`.
- **After a change:** playtest → console output → (navigate/input) → screenshot if the claim is visual. For multiplayer claims, a solo playtest is **not** sufficient evidence. Say so, and use Server & Clients (manual, or a test harness). From the MCP, `execute_luau` can start one with `StudioTestService:ExecuteMultiplayerTestAsync`, add a mid-session joiner with `AddPlayers`, and end it with `LeaveTest`/`EndTest`. Each client window is then driven and probed separately (verified in live Studio, 2026-10). Latency and device setup are in `roblox-testing`.
- **Performance claims:** measure (Roblox profiling guides via the `skill` tool if listed, MicroProfiler, Developer Console Stats) before and after. Never claim a speedup you didn't measure.

## Tool behavior seen in live Studio (2026-10)
- **Tool calls in one batch run one after another**, not in parallel. Run `screen_capture` calls strictly one at a time: three parallel calls moved the same camera, and two stalled past 120 s until stopped.
- **`execute_luau` in the Edit DataModel already runs inside a ChangeHistory recording.** `IsRecordingInProgress()` returned true and `TryBeginRecording()` returned nil, yet the edits applied and showed as one "Assistant" undo entry. Put related edits in one call, and guard any `TryBeginRecording` with `if rec then … end`. Whether one Ctrl+Z reverts exactly one call is untested.
- **A server-side probe's `require` returns a separate module instance**, so it can't read or set a running module's local state (e.g. a fuel variable). Observe state through instances, attributes or the game's own outputs.
- **Studio clears Output when a playtest starts.** A test `print` confirms the console reader works.
- **`character_navigation`** was slow (~20 s per call), once auto-jumped, and can't target a point inside a solid object. For precise pushes, use `Humanoid:MoveTo` from the Client DataModel.
- **Roblox CoreGui errors** in some test client windows (e.g. "Invalid value for enum CreatorType" from PlayerPermissionsModule, or errors from the legacy ChatScript) come from Roblox's scripts, not the game. Record them, and only investigate if they block the test.

## Before the user saves the place
- **Which place is it?** `game.PlaceId` and `GameId` of 0 mean a local file, not linked to any published place. Studio's window title shows the file path (on Windows: `Get-Process RobloxStudioBeta | Select MainWindowTitle`).
- **Is Rojo connected, and to which project?** A Rojo project with no `servePlaceIds` syncs into any place it connects to. In live testing it pushed one game's scripts and parts into an unrelated test place.
  - Rojo is live if `rojo serve` is running and Studio holds a connection to `127.0.0.1:34872`.
  - `GET http://127.0.0.1:34872/api/rojo` (msgpack) names the project and its `expectedPlaceIds`.
  - If the wrong project is connected, ask the user to disconnect, then scan again for its content before they save.
- **Saving a local place:** recommend **File → Save to File**. Ctrl+S is contextual, and forum reports describe local-file bugs (untested).
- **Don't save over a place file that belongs to a cloned repository or a plugin install** (a test fixture, for example). Copy it into the project and open the copy. A fixture place opened from Roblox Apex's own plugin folder was saved over in 2026-10.

## When Studio isn't connected (files only, or text only)
- Work from the Rojo or Script Sync tree, and use `luau-lsp`/`selene`/`StyLua` if the project has them.
- Pure logic can be unit-tested (Jest-Lua/TestEZ) or run headless (Lune, or Open Cloud Luau Execution if the project already uses it).
- State plainly which behavior is **unverified at runtime**, and give the exact playtest steps that would verify it.
