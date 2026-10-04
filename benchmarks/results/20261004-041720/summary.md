# Benchmark 20261004-041720
Subject model: sonnet · judge: opus · blind pairwise, randomized order

| task | Apex skills used | rubric baseline | rubric apex | winner | apex stale/wrong flags | baseline stale/wrong flags |
|---|---|---|---|---|---|---|
| B07-remote-review | roblox, roblox-security, roblox-networking | 1.00 | 0.92 | baseline | 1 | 1 |
| B10-combat-feel | roblox, roblox-networking, roblox-game-feel, roblox-security | 0.75 | 1.00 | apex | 0 | 0 |

**Wins:** apex 1 · baseline 1 · tie 0
**Mean rubric coverage:** baseline 0.88 · apex 0.96
**Total cost:** $0.51

## Judge reasons
- **B07-remote-review** (baseline): Both cover the critical issues with sound hardened code, but B explicitly flags the missing ability ownership/unlock check and avoids A's dubious per-remote throttle claim; its MaxHealth mistake is minor.
- **B10-combat-feel** (apex): B covers every rubric item: it fades rejected hits quietly, puts latency into the wind-up, and offers Server Authority as an option. A's code also contradicts its own advice on marker timing and on skipping the attacker.
