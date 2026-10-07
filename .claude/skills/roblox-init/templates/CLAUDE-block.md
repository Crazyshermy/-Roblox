
## Roblox Apex
This is a Roblox project. For any Roblox, Luau or game-design task (questions included), **first load the `roblox` skill** (or the matching `roblox-*` specialist). The router loads the relevant specialists.
- Project memory lives in `.apex/`: `project.md` (vision, pillars, constraints, conventions), `decisions.md` (settled decisions; they override generic best practice), `debt.md`. Read the relevant parts before significant work.
- Verify version-sensitive Roblox APIs and limits before relying on them. Never invent APIs.
- Separate verified facts from recommendations, and say what was and wasn't tested.
- Preserve the intended player experience. Never silently simplify. Common Roblox mechanics need a reason to exist in this game.
- Test meaningful changes (Studio playtest/console via MCP when available) before calling them done.
