# Lighthouse Keeper: live Roblox Studio results (2026-10-07)

**Run details:** Claude Code v2.1.293 · Opus 5.5 at xhigh effort · Roblox Apex 1.2.0 · Rojo 7.7.1 · Windows · Roblox Studio version **not recorded**. One tester, one day. This was open-ended workflow testing on the fixture, not the scripted 10 steps in `tests/STUDIO-TEST.md`. `docs/BENCHMARKS.md` maps it to those steps. The resulting code is in `tests/fixtures/lighthouse-reference/`.

**Possible answer-key contamination:** during the run, `lighthouse.FLAWS.md` sat **one folder above** the test project, where Claude could have read it. Nothing shows whether it did, so **contamination can't be ruled out for the planted flaws F1–F8**. The ten live-found bugs L1–L10 (`tests/fixtures/lighthouse.FLAWS.md` → "Found live, not planted") aren't in the answer key, so they aren't affected.

This file is the summary Claude wrote in the test project (`.apex/benchmark-summary.md`). Account-specific IDs were removed; nothing else changed.

---

**Setup:** Claude Code with the Roblox Apex 1.2.0 skills, Rojo 7.7.1 (`rojo serve`), and Roblox Studio's built-in MCP server. The fixture is a small Rojo project (5 server/shared modules, 2 client scripts). It was tested as an **unpublished** place, then published as a **private experience** (Studio API access on) for a real-DataStore pass. Everything below was observed in live Studio playtests unless it says otherwise. Code-only reasoning is listed separately.

## What the workflow showed it can do

- **Diagnose from live Output.** The first playtest surfaced 3 errors (server boot crash, HUD crash, refuel error) and traced them to root causes.
- **Edit through Rojo and prove sync** (`script_read`/`script_grep`, property reads) before every test, so no test ran on stale code.
- **Run solo and multi-client tests from the MCP.** `StudioTestService:ExecuteMultiplayerTestAsync` started 2-client sessions, `AddPlayers` added a mid-session join, and `LeaveTest`/`EndTest` ended them. Each client window was driven separately: keyboard, emulated mouse/touch, navigation, and server/client Luau probes.
- **Simulate network conditions.** The Network Simulator was set through `NetworkSettings` in each client window, and measured ping confirmed each level: ~56 / ~127 / ~390 ms.
- **Simulate devices.** `StudioDeviceSimulatorService` was used for the iPhone 7 (666×374) and Average Laptop (1365×768) presets.
- **Measure visuals rather than eyeball them.** Screenshots plus pixel statistics chose the lamp brightness: clipped-white ground fell from 99.8% to 0%.
- **Attack before fixing, then re-attack.** Exploits were reproduced on the unfixed code and the same attacks re-run afterwards, including under latency.
- **Verify real DataStore behavior, including failure injection without code changes.** Save and load round trips, shutdown saves, `UpdateAsync` merging (proved with a planted marker field) and a forced load failure. The failure was produced by setting the test server's StandardRead rate limit to 0 and filling the request queue.
- **Keep project memory** in `.apex/` (`project.md`, `decisions.md`, `debt.md`).

## Bugs found and fixed (verified live after the fix)

| Bug | Fix | Evidence after fix |
|---|---|---|
| Server crashed at boot: `GetDataStore` throws in an unpublished place | Saving disables itself; play continues | Server runs; only a "saving disabled" warning |
| HUD crashed before the character existed; would vanish on respawn | Waits for the character; `ResetOnSpawn = false` | HUD present after respawns |
| Refuel remote trusted a client-sent amount | Client sends no arguments; server checks range, alive, data, cooldown | 14 malicious payloads and 50-request spam rejected or capped |
| Refuel burned oil above the lamp's capacity | Uses only the room left | 200 oil at fuel ~30: 70 used, 130 kept |
| Lamp's Neon block stayed bright at 0 fuel | Switches to SmoothPlastic at 0 | Screenshot at 0 fuel |
| No SpawnLocation (players spawned on the lamp), later players spawned stacked | SpawnLocation added, then enlarged to 12×12 | 7 spawn samples, none stacked, 25–34 studs out |
| Hidden cans stayed solid | `CanCollide` toggled with visibility | Character stood inside a hidden can |
| HUD health only refreshed once per second | Listens to `HealthChanged` | 5 health changes shown within 0.5 s |
| Lamp floated with nothing under it | One anchored tower part | Screenshots; tower stops but doesn't launch players |
| Ground blown out to white by the lamp light | Max brightness 3 → 1 (measured) | Ground brightness 205/171/148/132 at fuel 100/50/20/0 |
| HUD overlapped legacy chat | Bottom-center (top-center was tried and still overlapped) | 0 px overlap on desktop and iPhone 7 |
| Rojo reset the Lamp to (0,0,0) when its child `Light` changed | Explicit `CFrame` instead of the `Position` shortcut | Reproduced, then the same change left the Lamp in place |
| Refuel touch button sat inside the Jump button on iPhone 7 | `SetPosition` once the button exists | 0 px overlap; survives respawn; emulated tap refuels |

## Exploits tested

| Attack (modified client) | Before fix | After fix |
|---|---|---|
| Touch spoof: detached hand in a can 77 studs away | Got oil | Blocked, at zero latency and under Bad 3G |
| Corpse limb lands in a can | Got oil | Blocked (alive check) |
| Blink teleport (0.15 s) into a can | Got oil | Blocked at zero latency; **got oil under Bad 3G** (2nd try) |
| Teleport into a can and stay | Got oil | **Still gets oil** (~2.9 s later) |
| Client moves its own corpse into a can | No oil (no touch reached the server) | Not re-run |
| Malicious refuel arguments (negative, NaN, ±inf, strings, tables, Instances, extra args) | Not testable live: the server never started | All rejected |

## Real DataStore pass (published private experience)

| Check | Result |
|---|---|
| "Saving disabled" warning gone | Yes; Output empty at session start |
| Save → load round trip (solo, real account key) | No record → saved `{"Oil":20}` on stop → reloaded **20** → saved `{"Oil":30}` (v2) |
| Failed load doesn't overwrite real data | 3 forced load failures; player saw 0 instead of 77, earned 10, left; record unchanged **at the same version** |
| Save uses `UpdateAsync` (merge) | Planted marker field survived the game's save: `{"Oil":31,"_probe":"keep"}` |
| Saves land on shutdown | Solo stop and `EndTest` with 2 players both wrote final values ~0.5 s after shutdown began |
| Which handler starts the shutdown save | `PlayerRemoving` fired 2–3 ms before `BindToClose` every time, so `BindToClose` only waited. Its own save path never ran |
| DataStore errors or budget warnings in normal play | None. All throttle/queue warnings came from the deliberate fault injection |

Test-only keys (`player_-1/-2/-3`, the `LKTestProbe` store) were removed afterwards. The real account's record (`{"Oil":30}`) was kept.

## Limits hit

- **Teleport exploits.** The client owns its character's physics, so a distance check can't stop "move my character to the can". It would need movement validation or Server Authority mode, which is out of scope for this fixture.
- **No real devices.** Touch was checked only through Device Simulator layout, emulated touch and one emulated tap. Gamepad ButtonX was never pressed.
- **Shutdown-initiated save not reproducible in Studio.** Studio removes players before `BindToClose` runs, so the path where `BindToClose` itself saves a still-present player never executed. Its "wait for in-flight saves" role fits the timing but wasn't isolated.
- **DataStore rate-limit surprise.** Setting the legacy `GetAsync` request type's limit to 0 showed a 0 budget but didn't throttle anything (40/40 reads succeeded). Only the `StandardRead` category actually throttled.
- **Rojo lamp-reset bug.** A child-property change reset a parent part placed via `Position`. Found only because a playtest screenshot looked wrong; fixed with an explicit `CFrame`.
- **Tool and environment quirks hit during testing:**
  - `firetouchinterest` isn't available in Studio; a detached-limb spoof stood in.
  - A server-side probe's `require` returns a separate module instance, so live game state (e.g. lamp fuel) can't be set from a probe.
  - Tool calls in one batch run sequentially, not in parallel.
  - `character_navigation` was slow (~20 s for one call) and once auto-jumped to 19 studs at 2× speed.
  - Test client windows inherit the last-active device preset.
  - Roblox CoreGui errors appeared in some test client windows (`CreatorType`, legacy `ChatScript`).
- **Corrections the workflow made to itself:**
  - The first visual screenshots were invalid (the lamp had been reset) and were retaken.
  - The first top-center HUD fix still overlapped chat.
  - The first touch-button fix didn't stick.
  - A short 10-stud approach capped the first latency measurements, so they were redone from 25 studs.
  - "Blink teleport blocked" was later shown to fail under latency.

## Still unverified

- Session locking and autosave (neither implemented); `BindToClose` initiating a save itself; behavior under real production load and server hops.
- Glancing high-speed pickups (one short contact) against `PickupRange`.
- Refuel button layout on tablets; whether the HUD label blocks the dynamic thumbstick zone on phones.
- Real touch, gamepad and real-device performance.
- The 0.5 s refuel cooldown (not observable: the 100-fuel cap makes spam harmless); NaN-position rejection (code only).
- Multiplayer latency runs used phone-emulated clients. The final desktop-mode multiplayer run was at zero added latency.
