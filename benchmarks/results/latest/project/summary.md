# Project benchmark (Lighthouse fixture + Studio simulator), subject sonnet, judge opus

| task | arm | skills | rubric | inspect→edit | playtest after edit | console after edit | syntax errs | sim errors after | winner |
|---|---|---|---|---|---|---|---|---|---|
| P1-respawn-hud | baseline | — | 0.8 | yes | no | no | 0 | 0 |  |
| P1-respawn-hud | apex | roblox, roblox-debugging | 1.0 | yes | yes | yes | 0 | 0 | apex |
| P2-refuel-exploit | baseline | — | 0.917 | yes | no | no | 0 | 2 |  |
| P2-refuel-exploit | apex | roblox, roblox-security | 0.917 | yes | yes | yes | 0 | 2 | baseline |
| P3-data-loss | baseline | — | 0.667 | yes | no | no | 0 | 2 |  |
| P3-data-loss | apex | roblox, roblox-data | 0.917 | yes | yes | yes | 0 | 2 | apex |
| P4-lamp-sync | baseline | — | 0.8 | yes | no | no | 0 | 0 |  |
| P4-lamp-sync | apex | roblox, roblox-networking | 0.9 | yes | yes | yes | 0 | 0 | apex |
| P5-dark-design | baseline | — | 0.75 | — | — | — | 0 | 2 |  |
| P5-dark-design | apex | roblox, roblox-game-design, roblox-genres | 0.917 | — | — | — | 0 | 2 | apex |
| P6-refuel-feel | baseline | — | 0.417 | yes | no | no | 0 | 2 |  |
| P6-refuel-feel | apex | roblox, roblox-game-feel | 0.917 | yes | yes | yes | 0 | 0 | apex |
| P7-creeping-dark | baseline | — | 0.5 | — | — | — | 0 | 2 |  |
| P7-creeping-dark | apex | roblox, roblox-boundary-breaker, roblox-visual-direction | 1.0 | — | — | — | 0 | 2 | apex |

**Wins:** apex 6 · baseline 1 · tie 0 · total cost $2.88

## Judge reasons
- **P1-respawn-hud** (apex): Both answers fix the ResetOnSpawn and stale-humanoid problems, but A also names the nil-character-on-load cause, binds cleanly to each character including one that already exists, actually ran a playtest and checked the console while saying what it couldn't verify, and pointed out related risks without changing them; B is more minimal but never playtested and only partly explains the error on load.
- **P2-refuel-exploit** (baseline): Both cover the same core hardening, but B computes the amount server-side with ceil and clamp so it never undercharges, while A's math.floor deduction leaks free fuel; A's notes on remaining risks (leaderstats as truth, the save session lock) are better but don't outweigh the correctness gap.
- **P3-data-loss** (apex): A's save path re-checks the lock and stops writing once it loses it, it adds an autosave, its BindToClose waits for saves that are still running, and it guards OilService's use of leaderstats before data loads; B's save never checks who owns the lock and has no autosave, and B's BindToClose can return while a PlayerRemoving save is still running because of the early return on the saving flag.
- **P4-lamp-sync** (apex): Both correctly move fuel to a replicated Lamp attribute with a working HUD and correct late-join handling. A adds an explicit only-on-change guard, disconnects old health connections cleanly, and fixes the trusted-client refuel exploit in the same fuel path. B relies on SetAttribute deduping same-value writes (the engine does skip unchanged values) and leaves the exploit as a recommendation.
- **P5-dark-design** (apex): A ties the threat more closely to the lighthouse fantasy and builds dread with cues before the danger (the flicker, the drone, the 25% warning). It also plans how to judge the result from real player behavior, while B leans on a generic enemy-wave loop and only checks that the code works, though B handles server-authority fixes in more detail.
- **P6-refuel-feel** (apex): B starts its orbs on the client right away to cover latency and only plays the flare once the server confirms; it also adds touch and gamepad input, fixes the existing HUD crash and ships a complete, coherent diff. A's effects all wait for the server round trip, it has no mobile input, and its diff leaves out the OilService handler and the Config changes it relies on (Config.Sounds, LampFlarePeakBrightness, LampBaseBrightness).
- **P7-creeping-dark** (apex): A pushes back on the downgrade, describes fog's camera-wide limit correctly, keeps gameplay authority on the server and covers mobile performance; B gets fog wrong and leaves out server authority.
