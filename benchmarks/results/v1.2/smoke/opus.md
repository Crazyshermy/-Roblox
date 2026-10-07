# Smoke test 20261004-203440 (model: opus, runs per case: 1, pass if >= 1)

| case | mode | pass rate | skills (per run) | cost |
|---|---|---|---|---|
| status | apex | 1/1 | — | $0.18 |
| router-entry | apex | 1/1 | roblox-architecture,roblox-networking | $0.19 |
| security-auto | apex | 1/1 | roblox,roblox-security | $0.24 |
| design-auto | apex | 0/1 | roblox,roblox-game-design,roblox-genres | $0.39 |
| debug-auto | apex | 1/1 | roblox,roblox-debugging | $0.18 |
| currency | apex | 0/1 | — | $0.32 |
| trivial | apex | 1/1 | roblox | $0.33 |
| ambition | apex | 0/1 | roblox,roblox-boundary-breaker | $0.18 |
| security-nomd | apex-nomd | 1/1 | roblox-security | $0.15 |
| pet-request | apex | 1/1 | roblox,roblox-security,roblox-data,roblox-game-design | $0.36 |
| npc-ai | apex | 1/1 | roblox,roblox-physics-animation | $0.34 |
| prompt-security | apex | 1/1 | roblox-security | $0.16 |
| route-inspect | apex | 1/1 | — | $0.17 |

Total cost: $3.19
Failed: design-auto, currency, ambition

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
- **pet-request**: Anti-slop must not fight an explicit request: build the pet system well, don't refuse or lecture
- **npc-ai**: NPC/enemy AI routes to physics-animation and uses doc-verified pathfinding handling
- **prompt-security**: Client-initiated ProximityPrompt grants must get the server-side contract
- **route-inspect**: /roblox-route explains routing for a trading system without executing it
