# Ecosystem audit and gap analysis (2026-10)

This is a focused audit to decide what Roblox Apex should be, not a survey. Sources: the Claude Code skills docs; the Roblox `creator-docs` repository (snapshot 2026-10-02); DevForum announcements; and the public skill packs listed below. All packs were read as research material. **No code or prose was copied.** Apex's text is written independently.

## Projects examined
| Project | What it is | Take-away |
|---|---|---|
| Roblox **built-in Studio MCP** (26 tools: script read/edit/grep, `execute_luau`, playtest control, console, screenshots, input, docs, assets) | Official "hands" for agents | **Integrate, never rebuild.** Apex teaches *when* to use each tool (`roblox/references/studio-mcp.md`). |
| AshExplained/roblox-skills (MIT, ~40 skills) | Broad lifecycle playbooks (growth, live ops, monetization) | Wide coverage, but many generic playbooks. A setup step injects routing into CLAUDE.md. Its retention and monetization framing tends toward the template mechanics Apex challenges. Kept: the vertical-slice idea and the Creator Store vetting topic. |
| ivar-anon/roblox-dev (MIT plugin: 7 skills, 3 commands, a reviewer agent) | Engineering-focused: security, datastores, typing | Solid "server owns truth" stance. Kept: the dedicated review capability. No design, feel or currency handling. |
| gogolumo/rbsmithy (MIT, one large skill) | Production workflow plus a Blender asset pipeline | One monolithic skill loads everything. Kept: the asset-pipeline topic, and pushing back on client trust. |
| ShiroKSH/skills (MIT) | A Studio bridge (MCP plus plugin) more than knowledge | A tool, not expertise. Out of scope, since Apex keeps knowledge separate from tools. |
| brockmartin/roblox-game-skill (no license stated) | Router plus references plus genre templates with full code | Kept: router-plus-lazy-references as an idea. Genre templates bundled as code are the "copycat progression" pattern Apex avoids. |
| BloxForge and other community MCPs | Studio bridges | Not needed now that the official MCP exists. |
| Local RBXOS design (this repo's prior work) | 3,262-line architecture with no code | Concepts were extracted (below). The infrastructure (Rust daemon, MCP gateway, companion plugin) was dropped as out of scope for a skill layer. |

## Answers
**Keep (from the ecosystem):** a router entry point; lazy-loaded references; server-authoritative security stance; a dedicated review step; vetting Creator Store assets.

**Change:** no monolithic skill (it loads everything) and no 40-skill sprawl (description cost and overlap). Use 18 focused specialists, each about 1k tokens, plus mandatory *bundles* so cross-cutting risks (value systems → security plus data) aren't missed.

**Remove:** genre code templates; retention and monetization playbooks that default to pets, eggs, rebirths and dailies; generic "best practice" lists with no Roblox-specific failure modes.

**Missing everywhere, so Apex built it:**
- **Currentness.** No pack covered 2026 platform changes: Server Authority (announced for all creators July 2026; one docs page still says beta), restructured DataStore limits, IAS full release, the new type solver GA, Script Sync GA, and `Lighting.Technology` being deprecated in favor of `LightingStyle`.
- **An evidence model** (E0–E5), plus an API-existence checker (`tests/check_api.py`) run against the official reference.
- **Anti-slop as a gate** with justified/transform/remove verdicts, and creative-ambition preservation (`roblox-boundary-breaker`).
- **Game feel** as a timeline and channel model with *networked* latency hiding.
- **Honest player modeling** (hypotheses, not psychology) and a hypothesis-first experiment loop.
- **Project memory** (`.apex/` decisions with rejected alternatives and reopen conditions) that overrides generic advice.
- **Real verification** of the skill layer itself: headless smoke tests and a blind baseline-vs-Apex benchmark.

**Outdated in common knowledge (and in models' training data):**
- DataStore budget "60 + players×10". The current model has experience-level limits (300 + CCU×40 read, ×20 write) plus configurable per-server limits (default 60 + players×40).
- "Roblox has no netcode or anti-speedhack." Server Authority with prediction and rollback exists and was announced for all creators.
- `wait`/`spawn`/`delay`, `BodyVelocity`-family movers, legacy chat, and `Lighting.Technology`.

**Contradictions found:**
- Pack advice to "play the animation on the server for everyone" contradicts the engine. Client-played animations on a player's own character already replicate.
- The remote throttle is commonly described as "per remote". The docs say ~500/s **per client, shared across all remotes of a type**.
- Our own benchmark judge (Opus) flagged the correct current throttle figure as "invented". That is evidence that model knowledge lags the docs, and it is why currency is a first-class concern.

**Extracted from RBXOS:** evidence grades; Reality Check → `roblox` loop and definition of done; Boundary Breaker and its technique catalog; the barrier catalog → visual direction and feel; anti-slop verdicts; the feel timeline and channel coverage; the fuzz strategy list; differential diagnosis; ADR decisions with reopen conditions; the "simulation is never real-player evidence" rule.
