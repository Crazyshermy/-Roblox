# Answer key: seeded flaws in the Lighthouse fixture

Kept OUTSIDE `tests/fixtures/lighthouse/` so a model under test can't read it.

| # | Where | Flaw | Class |
|---|---|---|---|
| F1 | client/HUD | `player.Character.Humanoid` at top level: nil on first load, and stale after respawn; health only refreshes on LampChanged | debugging / lifecycle |
| F2 | server/OilService RefuelLamp | trusts client `amount`: negative amount mints oil, huge or NaN amount gives free fuel, no type check | security |
| F3 | server/OilService RefuelLamp | no check that the player has that much oil (Oil goes negative), no range check to the lamp, no rate limit | security |
| F4 | server/* | `leaderstats` is the source of truth for value | security / architecture |
| F5 | server/DataService | defaults to 0 on a failed load (wipes data on the next save); SetAsync blind overwrite; no BindToClose; no session lock; `data.Oil` may be nil | data |
| F6 | server/OilService Touched | `player.leaderstats` may not exist yet (data not loaded), so it errors | data / lifecycle |
| F7 | server/LampService | FireAllClients every second instead of replicated state (attribute); late joiners wait for the tick | networking |
| F8 | design | darkness has no consequence; co-op isn't interdependent; refuel is a single keypress with no feel | design / feel |

## Found live, not planted (live Roblox Studio, 2026-10-07)

These flaws were already in the fixture but weren't planted on purpose. Live Studio testing found them (`tests/results-latest/studio/lighthouse-2026-10-07.md`). The answer key above sat one folder above that test project, but it doesn't mention any of these, so they aren't affected by possible answer-key contamination. Project-benchmark rubrics don't score them yet. The fixes are in `lighthouse-reference/`.

| # | Where | Flaw | Class |
|---|---|---|---|
| L1 | server/DataService | `GetDataStore` runs at module load, and it throws in an unpublished place (or with Studio API access off). The whole server boot fails, so nothing server-side can be tested until it's handled | data / lifecycle |
| L2 | server/OilService RefuelLamp + LampService.addFuel | the player loses the full amount even when the lamp is nearly full; `addFuel` caps the fuel, so the oil above capacity is burned | value / design |
| L3 | server/OilService Touched | trusts touches the client reports for its own character: a detached limb 77 studs away, a corpse limb, or a teleport into a can all collect oil. No living-character or server-side distance check. (Teleporting in still works after the reference fix; closing it needs movement validation) | security |
| L4 | world (`default.project.json`) | no `SpawnLocation`: players spawn on the lamp, already inside refuel range | level design |
| L5 | server/OilService | a collected (invisible) can stays solid (`CanCollide` stays true) | gameplay |
| L6 | server/LampService | the lamp's `Neon` material keeps it glowing at 0 fuel, so a dark lamp never looks dark | visual / feel |
| L7 | world | the lamp floats in mid-air with nothing under it | visual / level design |
| L8 | world + LampService | `PointLight.Brightness` 3 blows the lit ground out to white, so the dimming can't be seen | visual |
| L9 | client/HUD | the top-left HUD label overlaps the legacy chat window | UI |
| L10 | `default.project.json` | `Lamp` uses the `Position` shortcut while it has a child (`Light`). In Rojo 7.7.1, a project-file change to the child reset the Lamp to (0, 0, 0). Use an explicit `CFrame` on any part that has children | tooling |
