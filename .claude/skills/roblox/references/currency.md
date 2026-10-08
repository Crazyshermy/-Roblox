# Version-sensitive Roblox facts

Verified against `Roblox/creator-docs` (snapshot 2026-10-02) unless marked otherwise. **E4** means it matches current official docs. These facts drift, so re-verify any of them before it becomes load-bearing in a design. Re-verification paths are given as `creator-docs:<path>` (GitHub `Roblox/creator-docs`, `content/en-us/...`) or as live docs via Studio MCP `http_get`.

**Most common stale-knowledge traps** (older tutorials, and most AI training data, get these wrong):
1. DataStore budgets are **not** "60 + players×10" anymore (§Data).
2. Server Authority with prediction and rollback exists and was announced as available to all creators (Roblox, July 2026; E3). One docs page (`scripting/security/network-ownership.md`, 2026-10) still says "beta", so treat it as young. "Roblox has no built-in anti-speedhack/netcode" is outdated (§Networking).
3. The Input Action System is fully released and default player scripts are migrating to it (§Input).
4. `wait()`, `spawn()` and `delay()` are legacy. Use the `task` library.
5. Legacy chat (`Chatted` and the Lua chat system) has been superseded by `TextChatService`.
6. `Lighting.Technology` (Future/ShadowMap/Voxel) is **deprecated**. Use `Lighting.LightingStyle` (Realistic/Soft) plus `Lighting.PrioritizeLightingQuality` (E4, `Lighting.yaml`).

## Networking and authority
- **Server Authority model** (E4, `projects/server-authority/index.md`): `Workspace.AuthorityMode = Enum.AuthorityMode.Server`. Setting it auto-sets `NextGenerationReplication`, `PlayerScriptsUseInputActionSystem`, `SignalBehavior = Deferred`, `UseFixedSimulation` and `StreamingEnabled`.
  - Shared simulation logic goes in `RunService:BindToSimulation(fn)` inside a ModuleScript required by **both** client and server. Only "Simulation Access" members can be used inside bound functions.
  - Custom simulated state lives in **attributes** on predicted instances, written only inside bound functions. To replicate in this mode, an attribute must be within the first 64 on its instance, with a name of ≤ 50 chars and a string value of ≤ 50 chars.
  - Use `time()` inside the simulation, because it is synced and rewinds. `tick()`, `os.time()` and `os.clock()` are not.
  - Core inputs must be `InputAction`s. Their `InputContext` must be parented under the `Player`. Don't use `UserInputService.InputBegan` in core simulation.
  - Effects go in `RenderStepped` and read simulated state, and they must be able to *undo* mispredicted effects. Don't cache `AnimationTrack`s. Use `Animator:GetTrackByAnimationId()` or `GetPlayingAnimationTracks()`.
  - `RunService:SetPredictionMode()` controls per-instance prediction. Instance "stitching" lets `Instance.new`, `Clone` and `fromExisting` run inside bound functions to create instances predictively.
  - Debugging: the Server Authority visualizer (Ctrl/⌘+Shift+F6) shows prediction success rate, input accept rate and input drop reasons.
  - It is a new system with active DevForum bug reports (2026-H2). Treat edge-case behavior as E2 until probed.
- **RemoteEvent throttle** (E4, `RemoteEvent.yaml`): about **500 requests/s per client**, shared across **all** remotes of the same type. It is not per remote. A throttled `RemoteEvent` delays (queues) excess calls in order.
- **UnreliableRemoteEvent** (E4): payloads over **1,000 bytes** are dropped. No delivery or ordering guarantee, and no ordering relative to RemoteEvents. Excess calls are dropped, not queued. Messages arriving with no handler connected are discarded.
- RemoteEvents queue messages when no handler is connected. The queue is bounded, and overflow logs a `Remote event invocation` error.
- Remote events are **not** guaranteed to be ordered against property and attribute replication.

## Data
- **DataStore** (E4, `cloud-services/data-stores/error-codes-and-limits.md`):
  - Value ≤ **4,194,304** characters per key. Store name, key and scope ≤ **50** chars each. Metadata ≤ 300 chars in total.
  - **Experience-level** limits per minute, shared with Open Cloud: Read **300 + CCU×40**, Write **300 + CCU×20**, List 300 + CCU×2, Remove 300 + CCU×40. `UpdateAsync` consumes both read and write.
  - **Server-level** limits default to Read and Write **60 + players×40**/min. They are creator-configurable via `DataStoreService:SetRateLimitForRequestType()`. Inspect them with `GetRequestBudgetForRequestType()`.
  - Request types: reads through a `DataStore` object (`GetDataStore`) count as `Enum.DataStoreRequestType.StandardRead`. The `GetAsync` type covers `GlobalDataStore` reads (E4, `DataStoreRequestType.yaml`, 2026-10-08). Live Studio 2026-10: limiting `GetAsync` to 0 didn't throttle `DataStore` reads, while limiting `StandardRead` did.
  - **Per key** (all servers): writes ≤ **4 MB/min**, reads ≤ **25 MB/min** (`KeyThrottled`). Each request rounds up to the next KB. **Storage** cap: 500 MB + 1 MB × lifetime users, measured compressed on latest versions. Don't pre-compress.
  - Throttled requests queue, with **30 per queue**. When a queue is full, requests fail with error codes 301–306.
  - Official docs recommend **session locking** for player data (`player-data-purchasing.md`), and `UpdateAsync` when a write depends on the current value.
- **MemoryStore** (E4): memory quota **64 KB + 1.2 KB × users** (experience-wide). Requests **1000 + 120 × CCU** units/min. A single **sorted map or queue** holds ≤ 1,000,000 items and ≤ 100 MB, and lives on one partition (a throughput hot spot). Hash maps spread across partitions, with a per-key limit of about 5k write and 15k read units/min, so they are better for server lists and counters. Max expiration is **3,888,000 s (45 days)**. When memory is full, writes fail until items expire.
- **MessagingService** (E4, `MessagingService.yaml`): message ≤ **1 kB**. Topics are 1–80 chars. Each server can send **600 + 240 × players**/min. Each topic can receive 40 + 80 × servers/min. **Delivery is best effort and not guaranteed.**

## Input and UI
- **Input Action System (IAS)**: full release in 2026 (E4/DevForum). `Workspace.PlayerScriptsUseInputActionSystem` switches default player scripts to IAS. Prefer `InputContext`/`InputAction`/`InputBinding` for new rebindable, cross-device input.
- `TextChatService` is the current chat system. User-authored text shown to *other* users that bypasses chat must go through `TextService:FilterStringAsync` (or equivalent filtering) (E4).

## Assets
- A single mesh can't exceed **20,000 triangles**. Avatar items have their own budgets (E4, `art/modeling/specifications.md`, 2026-10-08).

## Characters
- `CharacterWalkSpeed` defaults to **16**. Jump: `StarterPlayer.CharacterUseJumpPower` defaults to **true**, so the default jump comes from `JumpPower` 50 and `Workspace.Gravity` (about 6.4 studs), **not** `JumpHeight` 7.2. Measure the real jump in a metrics gym. (E4, `StarterPlayer.yaml`)

## Luau and tooling
- Luau's **new type solver** is generally released (2025–2026). Its diagnostics and inference differ from the old solver, so check type errors against current Studio or luau-lsp rather than old blog posts (E4/DevForum).
- **Studio Script Sync** syncs scripts to local files. It is full release (2026) and suits Studio-first projects. Rojo remains the choice when the filesystem should be the source of truth for the whole project (E4, `scripting/sync.md`).
- **Script capabilities** (`Workspace.SandboxedInstanceMode = Experimental`, `Instance.Sandboxed`, `Instance.Capabilities`) can sandbox untrusted models and libraries. It is an experimental client beta as of 2026-10 (E4, `scripting/capabilities.md`).

## Studio
- Multi-client testing: Test → **Server & Clients**, up to **8** clients. Party Simulator emulates `PartyId` (E4, `studio/testing-modes.md`).
- From code (e.g. Studio MCP `execute_luau`): `StudioTestService:ExecuteMultiplayerTestAsync`, `AddPlayers`, `LeaveTest` and `EndTest`; `StudioDeviceSimulatorService` for device presets (E4, `StudioTestService.yaml`, `StudioDeviceSimulatorService.yaml`, 2026-10-08; used in live Studio 2026-10).
- Studio MCP tool inventory: see `studio-mcp.md`.
