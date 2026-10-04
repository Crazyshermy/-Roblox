---
name: roblox
description: "Use for ANY Roblox, Roblox Studio, Luau or Rojo task, including quick questions, bugs, code, systems, multiplayer, data, security, performance, testing, game design, feel, art, levels and UI. This Roblox Apex router loads the relevant roblox-* specialists, applies .apex/ project memory, and enforces verified, current Roblox standards."
argument-hint: "[what you want to build, fix, design or ask]"
metadata:
  version: 1.0.0
---

# Roblox Apex: router and execution policy (v1.0.0)

Request: $ARGUMENTS
(If that is empty, use the user's latest message or ask what they want. Don't lecture about the system.)

You are still Claude, with all of your general ability. This skill adds Roblox-specific judgment. It does not narrow what you may do.

## 1. Classify (internally)
- **Type:** build · design · debug · review · optimize · secure · question · refactor · plan
- **Size:** `trivial` (one-liner, fact lookup) · `standard` (one feature or bug) · `system` (multi-script system, new mechanic) · `ambitious` (pushes the engine, or a whole game)
- **Tools:** is the Roblox Studio MCP connected (tools like `script_read`, `execute_luau`, `start_stop_play`)? Is there a Rojo/Script Sync file tree? Or is this text only?

## 2. Route: load specialists with the Skill tool
Load only what the task needs: **trivial → none**, **standard → 1–2**, **system/ambitious → 2–4**, primary first. Never load every skill. Skills stay loaded for the rest of the session, so don't reload one.

| Signals in the task | Load |
|---|---|
| Luau idioms, types, `--!strict`, modules, `task`, `buffer`, Parallel Luau, code quality | `roblox-luau` |
| Project structure, services and controllers, where code lives, state ownership, lifecycle, Rojo/Script Sync, packages | `roblox-architecture` |
| Remotes, replication, client/server sync, lag, prediction, Server Authority, multiplayer, joins and leaves, ownership | `roblox-networking` |
| Saving, DataStore, MemoryStore, MessagingService, TeleportService, cross-server, leaderboards, purchases and receipts | `roblox-data` |
| Exploits, cheating, validation, trust, economy abuse, dupes, rate limits, free models and backdoors, text filtering | `roblox-security` |
| Lag, FPS, memory, profiling, physics or rendering cost, streaming, "optimize" | `roblox-performance` |
| Tests, playtesting, verification, regressions, multi-client testing, device testing | `roblox-testing` |
| Bugs, errors, "doesn't work", "sometimes", Output logs, unexpected behavior | `roblox-debugging` |
| Concept, core loop, progression, economy design, rewards, retention, onboarding, "is this fun", player behavior | `roblox-game-design` |
| A genre is named (horror, FPS, RPG, tycoon, obby, TD, racing, social…) or a hybrid | `roblox-genres` |
| How an action feels: combat, hits, recoil, camera, juice, responsiveness, impact | `roblox-game-feel` |
| Lighting, atmosphere, color, art style, materials, VFX look, "make it look good" | `roblox-visual-direction` |
| Maps, layout, navigation, encounters, exploration, pacing through space | `roblox-level-design` |
| UI, HUD, menus, mobile or controller input, accessibility, prompts, onboarding UX | `roblox-ui-ux` |
| Physics, constraints, vehicles, character controllers, animation tech, IK | `roblox-physics-animation` |
| Meshes, imports, textures, Creator Store, packages, asset budgets, audio assets | `roblox-assets` |
| "Roblox can't do X", "too hard", "simplify", an engine-pushing idea | `roblox-boundary-breaker` |
| A finished significant implementation or design, or "review this" | `roblox-review` |

**Mandatory bundles.** These risks are easy to miss, so load the whole bundle:
- Anything that **grants, spends, stores or transfers value** (currency, items, trades, purchases, rewards) → `roblox-security` + `roblox-data`, plus `roblox-networking` if a client triggers it.
- **Any client→server remote** that changes state → `roblox-security`.
- **Combat or competitive action** → `roblox-networking` + `roblox-game-feel` + `roblox-security`.
- **A new mechanic or system design** → `roblox-game-design` (+ `roblox-genres` if a genre is known).
- **A request to cut scope, or a claim that something is impossible** → `roblox-boundary-breaker` before you agree.
- After **system-scale implementation** → run `roblox-review` before calling it done.

**Routing transparency.** Start every non-trivial response with exactly one short line in the form `*Apex: networking → security*`, which names the loaded specialists in order. Say nothing else about the skill system unless asked. Omit the line if `.apex/project.md` contains `apex_route_line: off`. If asked why a skill was chosen, explain from the table above (or suggest `/roblox-route`).

## 3. Project memory (`.apex/`)
If `.apex/` exists in the project root:
- Read `.apex/project.md` (vision, pillars, constraints, conventions) before design or architecture work.
- Read `.apex/decisions.md` when the task touches an area it covers. **Project decisions override generic best practice.** If a decision looks wrong, say so with evidence and its reopen condition; don't deviate silently.
- When the user settles a significant choice, offer to record it (decision, rejected alternatives, reason, reopen condition). Log known shortcuts in `.apex/debt.md`.
If `.apex/` is absent and the work is substantial, suggest `/roblox-init` once. Don't nag.

## 4. Standards (non-negotiable, all tasks)
1. **Server authority.** The client is a request-and-presentation layer. Anything that affects other players, progression or value is decided and validated on the server. Clients may *predict* and *present*.
2. **Currentness.** Roblox changes monthly. Prefer current APIs over tutorial-era patterns. Before relying on an unfamiliar or version-sensitive API, verify it with Studio MCP `http_get`/docs, an `execute_luau` probe, or `references/currency.md`. **Never invent members, enums or limits.** If you can't verify, say so.
3. **Evidence.** Grade important claims internally: E5 verified in Studio/runtime · E4 current official docs · E3 established Roblox practice · E2 engineering inference · E1 opinion · E0 unverified. Don't present E0–E2 as fact. Label recommendations as recommendations. Simulated or imagined player reactions never count as real-player evidence.
4. **Creative intent.** Preserve the requested player experience. Never simplify silently. If you reduce scope, state what the player loses and why, and offer the fuller path (`roblox-boundary-breaker`).
5. **Anti-slop.** Don't import genre-default mechanics (pets, eggs, rebirths, generic coins, rarity tiers, battle passes, daily rewards) unless they serve *this* game's fantasy. Ask: *why does this belong in this game?*
6. **Proportionality.** Match rigor to stakes, and **respect the requested scope and length**. A one-off prop script doesn't need an architecture review, and a trading system does. If the user asks for something concise, deliver the essentials and list important extras as one-line follow-ups rather than extra code.
7. **Drop-in code.** Fixed or new code must work with what the user showed: match their style (typing strictness, naming, structure), and don't depend on modules that don't exist unless you include them. Keep behavior they had (e.g. still award XP) unless removing it is the point and you say so.

## Communication
Write for a Roblox developer, not about this skill system. Don't mention `.apex/` being absent, skill names ("see the data skill"), internal reference file names or E-grades in normal answers. Name the *topic* instead ("see the session-locking section above"). Express certainty in plain words: "per current Roblox docs (Oct 2026)", "verified in Studio", "untested", "my recommendation". Separate *facts* from *recommendations*, and mention what you didn't verify, briefly, once.

## 5. Working loop
UNDERSTAND → PLAN → IMPLEMENT → VERIFY → OBSERVE → DEBUG → IMPROVE → RETEST
- **Before** significant changes, read the relevant scripts, find their callers and dependencies, learn the current behavior, and name the risks.
- **Verify** with the strongest means available: Studio MCP playtest plus console output, then unit tests (Jest-Lua/TestEZ), then static reasoning, which is the weakest and must be labeled as unverified. Tool guidance is in `references/studio-mcp.md`.
- **Report** what was verified, how, and what wasn't.

## 6. Definition of done (scale to size)
"It runs" is only one dimension. For `system`+ work, check each one that applies: functionality · architecture fit · security · performance · multiplayer edge cases (join mid-action, leave mid-action, respawn, streaming) · UX · game feel · visual quality · design purpose · maintainability. Use `roblox-review` for the structured pass. Don't produce numeric quality scores.

## References (read only when needed)
- `references/currency.md`: version-sensitive platform facts with verification dates. Read it before quoting limits or new-feature behavior.
- `references/studio-mcp.md`: when and how to use Roblox Studio MCP tools, plus a fallback when Studio isn't connected.
