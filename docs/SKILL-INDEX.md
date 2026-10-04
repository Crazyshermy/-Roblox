# Skill index

| Skill | Invocation | Owns | References |
|---|---|---|---|
| `roblox` | `/roblox`, auto | routing, standards, working loop, definition of done, project memory | `currency.md` (version-sensitive facts), `studio-mcp.md` (tool use) |
| `roblox-luau` | auto / router | modern Luau, types, task lib, buffer, Parallel Luau, footguns | none |
| `roblox-architecture` | auto / router | placement, services/controllers, state ownership, lifecycle, components, toolchain | none |
| `roblox-networking` | auto / router | channel choice, Server Authority, ownership, latency, multiplayer edge cases, streaming | none |
| `roblox-data` | auto / router | DataStore, session locking, receipts, MemoryStore, Messaging, Teleport | none |
| `roblox-security` | auto / router | threat model, remote contract, value integrity, dupes, movement, supply chain, text | `fuzz-checklist.md`, `secure-remote-pattern.md` |
| `roblox-performance` | auto / router | measure-first method, bottleneck map, budgets, regression detection | none |
| `roblox-testing` | auto / router | test selection, edge-case catalog, testable code, verification report | none |
| `roblox-debugging` | auto / router | hypothesis-driven debugging, Roblox bug-class table | none |
| `roblox-game-design` | auto / router | fantasy/pillars, mechanic evaluation, progression, onboarding, anti-slop gate, fun as evidence | `anti-slop.md`, `player-model.md`, `experiments.md`, `economy.md` |
| `roblox-genres` | auto / router | genre contracts and hybrids | `horror.md`, `action.md`, `systems.md`, `adventure.md`, `social.md` |
| `roblox-game-feel` | auto / router | action timeline, channel coverage, networked latency hiding, camera, sound, movement | none |
| `roblox-visual-direction` | auto / router | identity, lighting (LightingStyle), palette roles, readability, storytelling | none |
| `roblox-level-design` | auto / router | metrics, navigation, encounters, exploration, multiplayer spaces, streaming layout | none |
| `roblox-ui-ux` | auto / router | hierarchy, mobile, input (IAS), controller, accessibility, implementation | none |
| `roblox-physics-animation` | auto / router | assemblies, movers, ownership, controllers, cameras, Animator, IK | none |
| `roblox-assets` | auto / router | import, collision, LOD, textures, packages, sourcing, AI generation, budgets | none |
| `roblox-boundary-breaker` | auto / router | experience vs mechanism, verified limits, technique families, scope honesty | none |
| `roblox-review` | auto / router | multi-lens, evidence-backed, severity-ranked critique | none |
| `roblox-status` | `/roblox-status` only | install, discovery and project-integration health | none |
| `roblox-route` | `/roblox-route <task>` only | dry-run routing explanation | none |
| `roblox-init` | `/roblox-init [desc]` only | create `.apex/` memory and the CLAUDE.md block | `templates/` |

Coverage map for the requested areas:
- **Engineering:** luau, architecture, networking, data, physics-animation, assets, debugging, ui-ux. Streaming is covered in networking, performance and level design. MemoryStore, Messaging and Teleport are in data.
- **Security:** security (plus data for dupes and receipts).
- **Performance:** performance.
- **Testing:** testing.
- **Game design:** game-design and genres.
- **Feel:** game-feel.
- **Art:** visual-direction.
- **Levels:** level-design.
- **UX/UI:** ui-ux.
- **Multiplayer:** networking.
- **Self-review:** review.
- **Ambition:** boundary-breaker.
