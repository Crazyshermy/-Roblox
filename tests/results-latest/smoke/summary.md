# Smoke test 20261004-145434 (model: sonnet)

| case | mode | skills invoked | skills ok | markers ok | cost |
|---|---|---|---|---|---|
| status | apex | — | True | True | $0.09 |
| router-entry | apex | roblox-architecture, roblox-networking | True | True | $0.10 |
| security-auto | apex | roblox-security | True | True | $0.10 |
| design-auto | apex | roblox, roblox-game-design, roblox-genres | True | True (re-run after negation-aware check fix) | $0.11 |
| debug-auto | apex | roblox, roblox-debugging | True | True | $0.09 |
| currency | apex | — | True | True | $0.08 |
| trivial | apex | roblox | True | True | $0.07 |
| ambition | apex | roblox, roblox-boundary-breaker, roblox-game-design | True | True | $0.10 |
| security-nomd | apex-nomd | roblox-security | True | True | $0.07 |
| route-inspect | apex | — | True | True | $0.08 |

Total cost: $0.90

Case intents:
- **status**: /roblox-status works and the session really discovers the skills
- **router-entry**: /roblox routes an architecture task to the right specialists and prints the route
- **security-auto**: No /roblox prefix: security review must auto-route and apply the handler contract
- **design-auto**: No /roblox prefix: design request must trigger anti-slop reasoning and fantasy-first design
- **debug-auto**: No /roblox prefix: debugging should identify the respawn stale-reference class and use hypotheses
- **currency**: Currentness: DataStore budgets changed in 2026; stale answer is 60 + players x 10
- **trivial**: Proportionality: a trivial script must not trigger a heavy multi-skill process or essay
- **ambition**: Creative ambition: 'Roblox can't do X, let's simplify' must trigger boundary-breaker, not agreement
- **security-nomd**: Plugin users who never ran /roblox-init: no CLAUDE.md block, security must still auto-route
- **route-inspect**: /roblox-route explains routing for a trading system without executing it
