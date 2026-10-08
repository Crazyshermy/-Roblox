# Lighthouse Keeper: reference solution (answer key, do not copy into a test project)

This is the Lighthouse fixture after a day of live Roblox Studio testing on 2026-10-07 (Roblox Apex 1.2.0, Claude Code v2.1.293, Opus 5.5 at xhigh effort, Rojo 7.7.1, Windows; Studio version not recorded). Every fix here was checked in live Studio playtests. The evidence is in `tests/results-latest/studio/lighthouse-2026-10-07.md`.

Like `../lighthouse.FLAWS.md`, it is kept **outside** `tests/fixtures/lighthouse/` so a model under test can't read it. The benchmark harnesses copy only `tests/fixtures/lighthouse/`. Never copy this folder into a project you're testing Apex in, and never put it in the same folder tree as one.

**It is a verified partial fix, not a complete answer key.** During testing, the tester decided the fixture stays a small test game (`.apex/decisions.md` D-005), so some planted flaws were deliberately left in place:

| Planted flaw (`lighthouse.FLAWS.md`) | State here |
|---|---|
| F1 HUD nil on first load, stale after respawn, health only refreshes on LampChanged | Fixed (waits for the character, `ResetOnSpawn = false`, `HealthChanged`) |
| F2 refuel trusts the client's `amount` | Fixed (the client sends no arguments) |
| F3 no balance, range or rate check on refuel | Fixed (oil > 0, 20-stud horizontal range, 0.5 s cooldown, living character) |
| F4 `leaderstats` is the source of truth | **Not fixed** (still the value store) |
| F5 data | **Partly fixed**: `pcall` and retries on load, a failed load never saves over real data, `UpdateAsync` merge, `BindToClose`. **No session locking, no autosave** |
| F6 `leaderstats` may not exist yet on touch | Fixed |
| F7 `FireAllClients` every second | **Not fixed** |
| F8 design (darkness has no consequence, co-op isn't interdependent, flat refuel) | **Not addressed** (out of scope under D-005) |

Testing also found ten real bugs that aren't in the planted list. They're recorded as L1–L10 in `../lighthouse.FLAWS.md` → "Found live, not planted". All are fixed here except one part of L3: **teleporting into a can still collects it**, because the client owns its character's physics (see `.apex/debt.md`).

## What's here
- `src/`, `default.project.json`: the fixed game. `Main.server.luau` is unchanged.
- `.apex/`: the project memory Claude kept during the session (`project.md`, `decisions.md`, `debt.md`). It's a real example of Apex memory in use: decisions with rejected alternatives and reopen conditions, debt with "fix when" triggers. Account-specific IDs were removed from this public copy.

## Use
- Compare with the flawed original: `git diff --no-index tests/fixtures/lighthouse tests/fixtures/lighthouse-reference`
- Build a place file: `rojo build tests/fixtures/lighthouse-reference/default.project.json -o LighthouseReference.rbxl`
- Every script compiles with `luau-compile` 0.650, and Rojo 7.7.1 builds the project (checked 2026-10-08).
