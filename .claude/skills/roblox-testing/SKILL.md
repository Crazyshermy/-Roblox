---
name: roblox-testing
description: "Roblox verification: unit tests (Jest-Lua/TestEZ), Studio MCP playtests and runtime checks, multi-client and latency tests, device testing, edge cases, exploit and data-safety tests, regression suites, and reporting what was actually verified."
---

# Roblox testing and verification

Goal: **evidence that the intended behavior happens, and that the likely failures don't.** State the evidence level you reached. A runtime observation is E5; reasoning about code is not.

## Choose the cheapest test that can actually fail
| Claim | Test |
|---|---|
| Pure logic (damage formula, inventory ops, migrations, validation) | **Unit test.** Extract it as a pure ModuleScript and test it with Jest-Lua (current) or TestEZ (legacy, common), or run it under Lune/Luau Execution in CI. |
| Engine API behaves as assumed | `execute_luau` probe in Studio (Edit or Server DataModel) |
| A feature works in play | `start_stop_play` → act (`character_navigation`/input or `execute_luau` in the Client DataModel) → `get_console_output` → assert state via `execute_luau` (Server) |
| Visual or UI claim | `screen_capture`, after the state assertions pass |
| Multiplayer behavior | **Server & Clients**, 2–3 clients (up to 8) plus the Network Simulator. A solo test is not evidence for multiplayer. Through the Studio MCP, start it with `StudioTestService:ExecuteMultiplayerTestAsync` (`${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`). |
| Device and UI fit | Device Emulator presets (small phone, tablet, console) with safe-area checks. Use real devices for performance claims. |
| Exploit resistance | Reproduce the exploit on the unfixed code first, fix it, then re-run the **same** attacks, including under simulated latency. Fire remotes with malicious args from the Client DataModel (see `roblox-security` fuzz checklist), then assert server invariants. |
| Data safety | Use a test place or test store name only. Simulate leave mid-save, rejoin quickly, a failed load and `BindToClose` (techniques below). |

## Live Studio techniques (verified 2026-10)
- **Latency:** set the Network Simulator in **each client window** through `NetworkSettings`, then confirm the measured ping before trusting the run. Wired Broadband, Standard Mobile 4G and Bad 3G measured ~56, ~127 and ~390 ms. A blink-teleport fix that held at zero latency failed under Bad 3G, so re-run security fixes under latency.
- **Devices:** `StudioDeviceSimulatorService` switches presets from a probe. Test client windows start with the **last preset active in the main window**, even after stopping. Activate a desktop preset before a desktop multi-client test.
- **Forced load failure without code changes:** `DataStoreService:SetRateLimitForRequestType(Enum.DataStoreRequestType.StandardRead, 0, 0)`, then 30+ pending reads to fill the queue. Further `GetAsync` calls then fail with `StandardReadGameServerThrottled`. Setting the `GetAsync` request type to 0 didn't throttle `DataStore` reads, because those count as `StandardRead` (`DataStoreRequestType` docs). Restore the limits afterwards.
- **Prove `UpdateAsync` merges:** plant a marker field in the player's record mid-session and check it survives the game's save. A blind `SetAsync` would erase it.
- **Shutdown saves:** on a Studio stop and on `EndTest`, `PlayerRemoving` fired 2–3 ms before `BindToClose` every time. A save that `BindToClose` itself starts for a still-present player can't be exercised in Studio, so report it as not verified.

## Edge-case catalog (pick the relevant ones)
join mid-round · leave mid-action · respawn mid-action · two players on one object · spam input · high latency · streaming out of the target · zero, max and overflow values · first-time player with empty data · returning player with old schema · server shutdown · teleport failure · purchase while data not loaded · mobile touch-only · controller-only · tiny screen.

## Writing testable Roblox code
Separate **decisions** (pure functions) from **effects** (Instances, remotes, DataStores). Inject services or stores so tests can pass fakes. Seed randomness (`Random.new(seed)`). Expose server-side invariant checks (e.g. "sum of currency equals sum of ledger") that a test can call.

## Report format
```
Verified (how): …
Not verified (why, and how to verify): …
Risks remaining: …
```
Never claim "tested" for something that was only read or reasoned about.

## Playtesting for experience (not just bugs)
Correctness tests don't show whether something is fun or clear. For player-experience claims, define what you'd observe (time to first objective, where players hesitate, what they ignore), run sessions with real players when possible, and treat AI or simulated playtests as hypothesis generators, not evidence of fun. See `roblox-game-design` → experiments.
