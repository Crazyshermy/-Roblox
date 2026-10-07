# Smoke test 20261004-203318 (model: sonnet, runs per case: 3, pass if >= 2)

| case | mode | pass rate | skills (per run) | cost |
|---|---|---|---|---|
| status | apex | 3/3 | — · — · — | $0.26 |
| router-entry | apex | 3/3 | roblox-architecture,roblox-networking · roblox-architecture,roblox-networking · roblox-architecture,roblox-networking | $0.29 |
| security-auto | apex | 3/3 | roblox,roblox-security,roblox-data,roblox-networking · roblox-security,roblox,roblox-data · roblox-security | $0.39 |
| design-auto | apex | 2/3 | roblox,roblox-game-design,roblox-genres · roblox,roblox-game-design,roblox-genres · roblox,roblox-game-design,roblox-genres | $0.33 |
| debug-auto | apex | 3/3 | roblox,roblox-debugging · roblox,roblox-debugging · roblox,roblox-debugging | $0.27 |
| currency | apex | 1/3 | — · — · — | $0.26 |
| trivial | apex | 3/3 | roblox · roblox · roblox | $0.22 |
| ambition | apex | 2/3 | roblox,roblox-boundary-breaker,roblox-game-design · roblox,roblox-boundary-breaker,roblox-game-design · roblox,roblox-boundary-breaker,roblox-game-design | $0.30 |
| security-nomd | apex-nomd | 2/3 | — · roblox-security · roblox-security | $0.22 |
| pet-request | apex | 3/3 | roblox,roblox-security,roblox-data,roblox-networking · roblox,roblox-security,roblox-data,roblox-networking · roblox,roblox-security,roblox-data,roblox-networking | $0.58 |
| npc-ai | apex | 3/3 | roblox,roblox-physics-animation · roblox,roblox-physics-animation · roblox,roblox-physics-animation,roblox-debugging | $0.37 |
| prompt-security | apex | 3/3 | roblox,roblox-security · roblox,roblox-security · roblox,roblox-security | $0.28 |
| route-inspect | apex | 3/3 | — · — · — | $0.25 |

Total cost: $4.02
Failed: currency

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
