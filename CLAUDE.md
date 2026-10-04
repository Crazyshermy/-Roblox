# Roblox Apex repository

This repo **is** the Roblox Apex skill layer. The canonical skills are in `.claude/skills/` (also exposed as a plugin via `.claude-plugin/plugin.json`).

When changing skills:
- Follow `docs/CONTRIBUTING.md`. Run `python3 tests/validate.py` after every edit. Run `tests/smoke.py` and the affected `benchmarks/run.py --only …` tasks for behavioral changes.
- Keep one home per rule (`docs/ARCHITECTURE.md` → Ownership). Specialists stay lean, and depth goes in `references/`.
- Descriptions must be quoted YAML strings. Never invent Roblox APIs. Version-sensitive facts belong in `.claude/skills/roblox/references/currency.md` with a source and date.
- Report what was verified (and how) separately from what wasn't.

## Roblox Apex
This is also a Roblox workspace. For Roblox, Luau or game-design work, use the `/roblox` skill system (the router loads the relevant `roblox-*` specialists).
- Project memory lives in `.apex/` when present. Settled decisions override generic best practice.
- Verify version-sensitive Roblox APIs and limits before relying on them. Separate facts from recommendations.
- Preserve the intended player experience. Never silently simplify. Common Roblox mechanics need a reason to exist in the game.
- Test meaningful changes before calling them done.
