# Project benchmark (Lighthouse fixture + Studio simulator), subject sonnet, judge opus

| task | arm | skills | rubric | inspect→edit | playtest after edit | console after edit | syntax errs | sim errors after | winner |
|---|---|---|---|---|---|---|---|---|---|
| P2-refuel-exploit | baseline | — | 0.833 | yes | no | no | 0 | 2 |  |
| P2-refuel-exploit | apex | roblox, roblox-security | 1.0 | yes | yes | yes | 0 | 2 | apex |

**Wins:** apex 1 · baseline 0 · tie 0 · total cost $0.43

## Judge reasons
- **P2-refuel-exploit** (apex): Both remove the client-sent amount and add balance, range and cooldown checks. B checks against the actual map with a horizontal range that suits a high lamp, adds an alive check, states that the check and deduction are atomic, names leaderstats-as-truth and the session-lock and duplication risks, and reports honestly on the playtest and what it couldn't verify. A's 3D 20-stud check may block honest players from refueling.
