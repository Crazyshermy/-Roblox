---
name: roblox-level-design
description: "Level and world design: metrics, navigation, landmarks, sightlines, critical vs optional paths, encounters, exploration, verticality, secrets, risk/reward, tension and release, multiplayer spaces, streaming-aware layout."
---

# Level design

A level is a **sequence of player decisions and feelings arranged in space**. Design the experience beat-by-beat, then the geometry.

## Start from metrics (get them from the project; defaults below are E4 engine defaults)
Character: `WalkSpeed` 16 studs/s, `JumpHeight` 7.2 studs (verify the project's values and any custom controller). Derive: max jumpable gap and height, comfortable corridor width (multiplayer: ≥ 3 characters side by side for main routes), door/ceiling clearance, time-to-cross for key spaces. Build a **metrics gym** (test strip of gaps/heights) before production geometry.

## Navigation and orientation
- **Landmarks**: unique, visible-from-afar shapes/lights for orientation; one per region.
- **Weenies/attractors**: a visible goal pulls the player forward (a tower, a light, a sound).
- **Critical path** clear through light, contrast, shape and affordance; optional paths discoverable but secondary.
- **Gating**: show the locked area before giving the key (anticipation + goal).
- Avoid dead ends without reward; loop back to known spaces (shortcuts that open from the far side).

## Sightlines and composition
Frame reveals (approach a vista through a narrow space, then open). Control what is visible from spawn: the first view sets the promise. In shooters, sightline length defines weapon balance — map lanes by range band and give cover rhythm.

## Encounters
Define per encounter: player goal, threat, space shape (open/cluttered/vertical), approach options (≥ 2 for agency), retreat options, and the escalation beat. Telegraph threats before they engage. Alternate high-intensity with recovery spaces (tension/release curve across the level).

## Exploration and secrets
Reward curiosity with things that matter (lore, shortcuts, cosmetics, meaningful items) — not filler coins. Use partial visibility (glimpse through a grate), sound cues, and "this seems climbable" affordances. Verticality creates exploration and tactical depth; ensure fall/return paths aren't punishing.

## Multiplayer spaces
Spaces must work for 1 player and for a full server: chokepoints become griefing points; spawns need protection and dispersal; social spaces need sit/gather spots and sightlines to activity. In horror/co-op, use space to separate players deliberately.

## Roblox technical layout
- Streaming: cluster detail into regions; keep required gameplay objects as `Persistent`/`Atomic` models where clients need them whole; don't rely on far instances existing client-side.
- Performance: occlusion-friendly layouts (walls and turns limit what's drawn); avoid huge open vistas full of unique high-poly assets on mobile.
- Pathfinding: if NPCs navigate, validate with `PathfindingService` (agent radius/height matching the NPC, `PathfindingModifier` for costs) and test NPC paths explicitly.

## Verify
Walk the critical path (playtest or `character_navigation`) and record: time-to-objective, places where the next goal isn't visible, unreachable or softlocking spots, out-of-bounds escapes. Screenshot from spawn and from each decision point.
