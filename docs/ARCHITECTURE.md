# Architecture

```
Claude
 └─ CLAUDE.md block (6 lines: Roblox project, use /roblox, .apex memory, verify, preserve intent, test)
     └─ /roblox router (~2.3k tokens, loaded on demand)        ← always-visible description (~1.2k tokens for all skills)
         ├─ classify: type × size × tool availability
         ├─ route: signal table + mandatory bundles → Skill tool loads 0–4 specialists
         ├─ project memory: .apex/project.md, decisions.md, debt.md
         ├─ standards: authority · currentness · evidence · intent · anti-slop · proportionality · drop-in code
         └─ loop: understand → plan → implement → verify → observe → debug → improve → retest
             └─ specialists (~1k tokens each) → references (loaded only when a specialist says so)
                 └─ Roblox Studio MCP / files / tests: the *tools*, which Apex teaches Claude to use but doesn't implement
```

## Layers
| Layer | Cost | Contents |
|---|---|---|
| Always loaded | ~1.2k tokens | the 19 model-invocable skill descriptions (`/roblox-status`, `/roblox-route`, `/roblox-init` are user-only, so their descriptions cost nothing) plus the 6-line CLAUDE.md block |
| On invoke | ~2.3k | router (`roblox/SKILL.md`) |
| Per specialist | 0.6–1.8k | the 18 specialists |
| References | 0.3–1.3k each | read only when the specialist's procedure calls for them (genre cards, anti-slop, currency facts, fuzz checklist…) |

Typical standard task: about 4–5k tokens. System-scale: about 6–7k. Loading everything would be about 30k, and the router never does that.

## Routing
1. **Automatic:** Claude sees the descriptions and invokes `roblox` or a specialist directly for Roblox work. Smoke tests confirm automatic triggering for security, design, debugging and ambition prompts with no `/roblox` prefix.
2. **Explicit:** `/roblox <task>` loads the router, which classifies the task and calls the Skill tool for specialists using its signal table.
3. **Bundles** guard against the most expensive misses. Value systems → security + data (+ networking). Any state-changing remote → security. Combat → networking + feel + security. New mechanic → design (+ genres). "Impossible/simplify" → boundary-breaker. System-scale implementation → review.
4. **Budget:** trivial work loads 0 specialists, standard 1–2, system 2–4. A loaded skill persists for the session, so it isn't reloaded.
5. **Inspectable:** non-trivial answers start with `*Apex: a → b*`. `/roblox-route <task>` gives a full dry-run explanation (matched signals, fired bundles, skipped skills, cost).

Skills can't invoke skills directly. The router *instructs* Claude to call the Skill tool, which was verified in real sessions, in both project and plugin installs. In plugin mode the bare names resolve to `roblox-apex:<name>` automatically (verified).

## Ownership (to avoid duplicated or contradictory rules)
Each rule has one home, and other skills point to it:
- Security owns validation and value integrity.
- Networking owns channels, authority flow and multiplayer edge cases.
- Data owns persistence and cross-server work.
- Performance owns measurement and budgets.
- Game-design owns anti-slop, the player model and experiments.
- Boundary-breaker owns ambitious-feature technique search.
- The router owns global standards.
- `roblox/references/currency.md` is the single home for version-sensitive facts.

## Project memory (`.apex/`)
Plain, git-tracked markdown created by `/roblox-init`:
- `project.md`: vision, pillars, audience, refusals, art direction, toolchain, conventions, constraints, settings.
- `decisions.md`: ADRs with **rejected alternatives** and **reopen conditions**. They override generic best practice, and Claude must argue with evidence rather than silently deviate.
- `debt.md`: known shortcuts.

## Design decisions (and rejected alternatives)
| Decision | Rejected | Why |
|---|---|---|
| Canonical skills in `.claude/skills/`, also exposed as a plugin via `"skills": "./.claude/skills/"` | separate plugin `skills/` copy | one source of truth. The repo itself is a working project, and bare `/roblox` works in both modes (verified). |
| No `!command` dynamic injection in the router | injecting `.apex/` via shell | a failing or unpermitted command aborts the whole skill. That is fragile on Windows and in permission-prompt modes. |
| 18 specialists | 40-skill catalog / single monolith | description cost and overlap vs everything-always-loaded |
| Evidence grades internal, plain-language externally | E-labels on every line | the blind judge penalized jargon as noise. Honesty is preserved in plain words. |
| No daemon, MCP gateway or companion plugin | RBXOS infrastructure | tools already exist (Studio MCP). The value is in judgment, not plumbing. |
| One route line on by default (`apex_route_line: off` to hide) | always silent | you asked for inspectable routing. It's switchable per project. |
