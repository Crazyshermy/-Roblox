---
name: roblox-status
description: "Reports Roblox Apex installation and health, covering the installed version, which roblox-* skills exist on disk vs which are actually discovered in this session, router status, key references, project integration (.apex/ memory, CLAUDE.md block), and Roblox Studio MCP connectivity."
disable-model-invocation: true
---

# /roblox-status

Produce a compact status report. Use only real observations. Don't assume anything is installed because it should be.

1. **Version:** read the `metadata.version` field / heading of `${CLAUDE_SKILL_DIR}/../roblox/SKILL.md`.
2. **On disk:** Glob `${CLAUDE_SKILL_DIR}/../roblox*/SKILL.md`. Also check the other install location: project `.claude/skills/roblox*/SKILL.md` and user `~/.claude/skills/roblox*/SKILL.md`. Flag duplicates across locations (a version-skew risk).
3. **Discovered:** list the `roblox*` skills that appear in *your own available-skills list* for this session (the skill descriptions you were given). Compare them with the on-disk list. Note that the `disable-model-invocation` skills (`roblox-status`, `roblox-route`, `roblox-init`) are user-only and don't appear in the model's list. Any other mismatch means a discovery problem: suggest `/reload-skills` or checking the frontmatter.
4. **Router:** confirm `roblox/SKILL.md` exists, has frontmatter `name: roblox`, and has its `roblox/references/currency.md` and `roblox/references/studio-mcp.md` files. Report the "Verified … snapshot" date from `roblox/references/currency.md` and warn if it is more than 90 days before today (re-verify).
5. **Project integration:** does `.apex/project.md` exist, and is it filled in or still a template? Do `.apex/decisions.md` and `.apex/debt.md` exist? Does `CLAUDE.md` contain the `Roblox Apex` block?
6. **Studio:** do any Roblox Studio MCP tools appear in your toolset (`list_roblox_studios`, `execute_luau`, …)? If yes, say "connected (tools present)". Don't call them unless the user asks. If no, say "not connected" and give the setup pointer from `${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`.

**Expected inventory:** 22 skills in total, made up of the router `roblox`, 18 specialists and 3 user-only commands. That is 19 model-invocable. Build each count by **listing the names first**, then counting the list. Plugin installs show names prefixed with `roblox-apex:`, which is normal. Any difference from the expected inventory is an issue to report.

Output format:
```
Roblox Apex <version>
Skills: <n> on disk · <n> model-invocable discovered · user-only: roblox-status, roblox-route, roblox-init
  <list, with ✓ discovered / ✗ missing>
Router: ok | problem: …
Knowledge snapshot: <date> (<fresh|stale>)
Project memory: .apex/ <present/filled | template | absent → run /roblox-init>
CLAUDE.md block: <present | absent>
Studio MCP: <connected | not connected>
Issues: <bullets, or "none">
```
