# Smoke test 20261004-041113 (model: sonnet)

| case | mode | skills invoked | skills ok | markers ok | cost |
|---|---|---|---|---|---|
| debug-auto | apex | roblox-debugging | True | True | $0.07 |
| currency | apex | — | True | True | $0.09 |

Total cost: $0.16

Case intents:
- **debug-auto**: No /roblox prefix: debugging should identify the respawn stale-reference class and use hypotheses
- **currency**: Currentness: DataStore budgets changed in 2026; stale answer is 60 + players x 10
