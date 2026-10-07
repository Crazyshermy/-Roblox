---
name: roblox-boundary-breaker
description: "Keeps ambitious Roblox ideas alive. Use when something seems impossible or too hard on Roblox, or when someone proposes simplifying it. Verifies the real limitation, then searches client illusion, simulation splits, precomputation, procedural, custom systems, Parallel Luau and hybrids."
---

# Boundary breaker

**Roblox is the medium, not the ceiling.** The goal is to keep the *intended player experience* and find the mechanism that delivers it.

## Procedure
1. **Experience.** In one or two sentences, what must the player *perceive and feel*? Separate perception from mechanism. ("Time rewinds around me" needs the world to visibly move backward for that player and stay consistent for others. It doesn't need the engine to literally reverse physics.)
2. **Limitation.** Name the exact constraint and its type: engine feature, API, performance, networking, asset, platform policy, or development cost. **Verify it** with current docs (`${CLAUDE_SKILL_DIR}/../roblox/references/currency.md`, Studio MCP `http_get`) or an `execute_luau` probe. An unverified "Roblox can't" is rejected, and old limitations are often gone (EditableMesh/EditableImage, Server Authority, Parallel Luau, Audio API, IAS).
3. **Search the technique space.** Consider each family before choosing:
| Family | Examples |
|---|---|
| Client-side illusion | per-player local parts and effects (different realities per player), camera tricks, `ViewportFrame` portals and mirrors, fake reflections, screen-space effects, local-only lighting changes |
| Simulation split | coarse server simulation + rich client presentation; server-authoritative state + client interpolation; Server Authority prediction |
| Precomputation | baked paths and navigation, recorded state ring buffers (`buffer`) for rewind and replay, precomputed destruction pieces |
| Procedural | `EditableMesh`/`EditableImage` runtime geometry and textures, procedural animation (IK, `Motor6D.Transform`), generated layouts, procedural audio layering |
| Custom systems | custom character controller, custom lightweight physics for many entities (CFrame integration without Humanoids), custom camera |
| Parallelism | Parallel Luau Actors for AI, perception, pathing, generation |
| Perception tricks | audio carrying the illusion, hitstop and frame pacing, post-processing, cutting away at the expensive moment |
| Streaming and LOD | streaming regions, impostors (billboards or low-poly stand-ins), model LOD swaps, loading behind occluders |
| Design reframing | change the *rules* so the hard part isn't needed while the feeling remains (only after the technical options, and stated explicitly) |
4. **Options.** Present 2–4 options. For each, give which parts of the experience survive and which are lost (named, not scored), the complexity, the risk, the performance impact **on a mid-range phone**, the security impact, and the upgrade path.
5. **Spike first.** Prototype the riskiest assumption before committing the architecture, and record the result (E5 if run in Studio).
6. **Never simplify silently.** If the chosen option loses part of the experience, tell the user exactly what and why, and keep the fuller option on record (`.apex/decisions.md` → rejected or deferred).

## Example (compressed)
*"Players rewind time for 5 seconds; enemies and projectiles reverse."* The engine can't reverse physics. So the server records snapshots (positions, states) of rewindable entities in a ring buffer at 10–20 Hz. On rewind, the server restores state along the buffer, and clients render it smoothly with interpolation plus a rewind post-effect and reversed audio. Per-player "time bubbles" become client-local presentations with server arbitration. Kept: visible reversal, consistency across players, the core fantasy. Cost: memory per entity and authority rules for overlapping rewinds. Spike: buffer 200 entities × 5 s and measure server memory and frame time.
