# Smoke test 20261004-041025 (model: sonnet)

| case | mode | skills invoked | skills ok | markers ok | cost |
|---|---|---|---|---|---|
| status | apex | — | True | True | $0.09 |
| router-entry | apex | roblox-architecture, roblox-networking | True | True | $0.10 |
| security-auto | apex | roblox-security | True | True | $0.08 |
| design-auto | apex | roblox, roblox-game-design, roblox-genres | True | True | $0.11 |
| debug-auto | apex | — | False | True | $0.06 |
| currency | apex | — | False | False | $0.09 |
| route-inspect | apex | — | True | True | $0.08 |

Total cost: $0.59

Case intents:
- **status**: /roblox-status works and the session really discovers the skills
- **router-entry**: /roblox routes an architecture task to the right specialists and prints the route
- **security-auto**: No /roblox prefix: security review must auto-route and apply the handler contract
- **design-auto**: No /roblox prefix: design request must trigger anti-slop reasoning and fantasy-first design
- **debug-auto**: No /roblox prefix: debugging should identify the respawn stale-reference class and use hypotheses
- **currency**: Currentness: DataStore budgets changed in 2026; stale answer is 60 + players x 10
- **route-inspect**: /roblox-route explains routing for a trading system without executing it
