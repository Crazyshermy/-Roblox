---
name: roblox-init
description: "Sets up Roblox Apex project integration. It creates .apex/ project memory (project.md, decisions.md, debt.md) and adds the Roblox Apex block to CLAUDE.md, filling in what can be inferred from the codebase."
argument-hint: "[optional: one-line game description]"
disable-model-invocation: true
---

# /roblox-init

Game description (optional): $ARGUMENTS

1. **Inspect** the project. Is it Rojo (`*.project.json`), Script Sync, or Studio-only? What package manager (`wally.toml`, `pesde.toml`, `rokit.toml`/`aftman.toml`) and tooling (`selene.toml`, `stylua.toml`, luau-lsp) does it use? What is the source layout, and which frameworks or libraries show up in requires? If Studio MCP is connected, use `search_game_tree` for the top-level services only.
2. **Create `.apex/`** from the templates in `${CLAUDE_SKILL_DIR}/templates/`. Never overwrite existing files; if `.apex/` files exist, only report them.
   - `project.md`: fill in what you could **infer** (tooling, structure, conventions) and mark it `(inferred, confirm)`. Leave vision, fantasy and pillars as questions for the user unless `$ARGUMENTS` or the README answers them. **Don't invent the creative vision.**
   - `decisions.md` and `debt.md`: copy the templates. Add decisions that are evident from the code (e.g. "uses ProfileStore for player data"), marked `(inferred)`.
3. **CLAUDE.md:** if there's no `Roblox Apex` block, append the contents of `${CLAUDE_SKILL_DIR}/templates/CLAUDE-block.md`. Create `CLAUDE.md` if it's missing. Don't rewrite the user's existing content.
4. **Report** what you created and what you inferred, then ask the 3–5 most valuable questions (fantasy, pillars, target devices, monetization stance, hard constraints).
