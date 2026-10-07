# Evidence policy

| Grade | Meaning | Example |
|---|---|---|
| **E5** | Verified in live Roblox Studio or runtime | an `execute_luau` probe, a playtest with console output, a measured profile |
| **E4** | Matches current official documentation | `creator-docs` API reference or guides, with the snapshot date |
| **E3** | Strong real-world Roblox practice | session locking via a profile library, CollectionService components |
| **E2** | Engineering inference | "this yield creates a duplication window" |
| **E1** | Recommendation or opinion | art direction, tuning values |
| **E0** | Unverified | anything recalled without a source |

## Rules
1. Grades are an **internal discipline**. In answers, express them in plain words ("per current Roblox docs (Oct 2026)", "verified in Studio", "untested", "my recommendation"). Don't attach labels to every line.
2. Never present E0–E2 as fact. If an E0 claim is load-bearing, verify it first (docs, `execute_luau`) or say it's unverified.
3. **Simulation, AI personas and model reasoning about players are never real-player evidence.** Player claims rank: A/B experiment > analytics or observation > moderated playtest > designer reasoning > simulated players.
4. Version-sensitive facts live in one file, `.claude/skills/roblox/references/currency.md`, each with a source path and a snapshot date. `/roblox-status` warns when the snapshot is more than 90 days old.
5. Every engine API named in the skills must exist in the current reference: `tests/check_api.py` enforces this.
6. When docs and community practice disagree, docs win for *what the engine does*, and practice can win for *how to structure code*. Record the disagreement.
7. Benchmark judges are models too. A judge's "stale/incorrect" flag must be checked against the docs before the skills are changed (one judge flagged the correct current remote throttle as invented).
