# Project benchmark (Lighthouse fixture + Studio simulator), subject sonnet, judge opus

| task | arm | skills | rubric | inspect→edit | playtest after edit | console after edit | syntax errs | sim errors after | winner |
|---|---|---|---|---|---|---|---|---|---|
| P1-respawn-hud | baseline | — | 0.8 | yes | no | no | 0 | 0 |  |
| P1-respawn-hud | apex | roblox, roblox-debugging | 1.0 | yes | yes | yes | 0 | 0 | apex |
| P2-refuel-exploit | baseline | — | 0.833 | yes | no | no | 0 | 2 |  |
| P2-refuel-exploit | apex | roblox, roblox-security | 1.0 | yes | yes | yes | 0 | 2 | apex |
| P8-npc-chase | baseline | — | 0.667 | yes | yes | yes | 0 | 2 |  |
| P8-npc-chase | apex | roblox, roblox-physics-animation, roblox-architecture | 0.5 | yes | yes | yes | 0 | 2 | apex |
| P9-dev-product | baseline | — | 0.75 | yes | no | no | 0 | 2 |  |
| P9-dev-product | apex | roblox, roblox-data, roblox-security | 1.0 | yes | yes | yes | 0 | 2 | apex |
| P10-mobile-controls | baseline | — | 0.917 | yes | yes | yes | 0 | 0 |  |
| P10-mobile-controls | apex | roblox, roblox-ui-ux, roblox-security | 0.917 | yes | yes | yes | 0 | 0 | apex |

**Wins:** apex 5 · baseline 0 · tie 0 · total cost $2.54

## Judge reasons
- **P1-respawn-hud** (apex): Both fixes are correct and nearly the same, but B keeps the change limited to the HUD, playtests and checks the console, and states that the respawn itself wasn't tested and how to test it; A edits an unrelated file and runs no playtest.
- **P2-refuel-exploit** (apex): Both close the refuel hole correctly, but A also adds a distance check to the forgeable can pickup, honestly flags that oil lives in leaderstats as a remaining risk, and gives concrete exploit-test steps, while B wrongly says the can pickup is safe and names no remaining risks.
- **P8-npc-chase** (apex): Neither answer uses pathfinding, but B's anchored, server-driven monster is fairer (12 studs/s versus the 16 player WalkSpeed), its range-based attack is more reliable, it handles a lamp that is already out at startup, and it states its limits clearly; A has explicit network ownership but a monster players can't outrun.
- **P9-dev-product** (apex): B waits for the data to finish loading, saves with UpdateAsync, retries, and avoids overwriting saves after a failed load, so the purchase is durable and idempotent. A's leaderstats-as-loaded check lets a receipt that arrives while data is loading overwrite the player's saved data, and it does not flag the existing DataService flaws.
- **P10-mobile-controls** (apex): A has stronger server validation (it only takes the oil that fits in the lamp, has nil checks and a cooldown), a larger repositioned touch button, and a binding that only exists when refueling can do something. B's HUD sizing is more responsive, but its server handler throws away oil that doesn't fit, has no nil checks, and leaves a dead button when the lamp is full.
