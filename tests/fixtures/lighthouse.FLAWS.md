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
