# Project: Lighthouse Keeper

> **Status: permanent test fixture, never shipped** (confirmed 2026-10-07). It exists to validate Roblox Apex, Claude Code, Rojo and Studio MCP against real code. Keep it intentionally small. Don't expand its scope unless that's specifically requested. See D-005.

## Experience
- **Core fantasy (player language):** "Keep the lighthouse lamp burning through a storm night, together." (from README)
- **Core loop:** collect oil cans → bring oil to the lamp → refuel it before it drains (1 fuel/s, 100 max). The README's "dangerous night when the lamp goes dark" is **out of scope unless specifically requested**.
- **Pillars:** (confirmed 2026-10-07)
  1. Clear cooperative teamwork.
  2. Simple, satisfying gameplay feedback.
  3. Urgency and tension from keeping the lamp alive.
- **Audience and devices:** test on desktop first. Keep the existing gamepad (ButtonX) and touch refuel support where practical. (confirmed 2026-10-07)
- **Refusals / hard constraints:** (confirmed 2026-10-07)
  - Keep the fixture small, easy to understand and easy to reset.
  - It must stay useful for testing networking, security, UI, data handling and Studio playtesting.
  - No major new gameplay systems (e.g. the dangerous-night system) unless specifically requested.

## Visual / audio direction
- Visual pillars: ? (README implies storm, night, lighthouse; the place currently uses default daytime Lighting)
- Palette roles (environment / accent / interactable / danger / UI): ?

## Technical
- Toolchain: Rojo 7.7.1, `default.project.json` defines both scripts and the test world. No Wally/pesde/rokit/aftman, selene, StyLua or luau-lsp config. (inferred, confirm)
- Structure (inferred, confirm):
  - `src/server` → `ServerScriptService.Server`: `Main.server.luau` bootstraps service modules (`DataService`, `OilService`, `LampService`), each exposing `.start()`.
  - `src/shared` → `ReplicatedStorage.Shared`: `Config` (all tunables).
  - `src/client` → `StarterPlayerScripts.Client`: `HUD`, `Refuel` LocalScripts.
  - Remotes (`RefuelLamp`, `LampChanged`) and world parts (`Baseplate`, `SpawnLocation`, `Tower`, `Lamp`, `OilCans`) are declared in `default.project.json`.
- Networking model: classic remotes. Client sends intent only; server validates and decides. Lamp fuel is broadcast to all clients every second via `LampChanged`. (inferred)
- Player data: raw `DataStoreService`, store `PlayerData`, key `player_<UserId>`, value `{ Oil = n }`. `UpdateAsync` once on leave/shutdown. **No session locking, no autosave.** Saving disables itself when DataStores are unavailable. (inferred)
- Conventions (inferred, confirm): non-strict Luau (no `--!strict`, no type annotations); tab indentation; PascalCase service modules with `Service.start()`; camelCase locals; module-table pattern; tunables live in `Shared.Config`; sparse comments.

## Constraints
- Performance targets: ?
- Known platform constraints affecting design:
  - **Published 2026-10-07 as a private experience** (PlaceId and GameId omitted from this public copy) with Studio API access on. **Studio playtests read and write the real `PlayerData` DataStore.** Solo playtests use the tester's own account key (`player_<UserId>`); `StudioTestService` clients use `player_-1`, `player_-2`, …. (Before publishing, PlaceId was 0 and saving was disabled.)
  - `StreamingEnabled` is off. (observed 2026-10-07)
  - Players spawn on `Workspace.SpawnLocation`, 12×1×12 centered at (0, 0.5, 30): 24–36 studs from the lamp, outside refuel range (D-006, verified 2026-10-07).

## Current priorities
- No open priorities. Playtest bug fixes (lamp unlit at 0, spawn, hidden cans, HUD health) were done and verified 2026-10-07. Remaining shortcuts are in `debt.md`.

## Apex settings
- apex_route_line: on   # set to off to hide the one-line route header
