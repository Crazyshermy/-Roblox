---
name: roblox-assets
description: "Roblox asset pipeline: mesh import, scale and pivots, collision fidelity, LOD, textures and PBR, MaterialVariants, audio assets, packages, Creator Store sourcing and licensing, AI-generated assets, permissions, asset budgets."
---

# Asset pipeline

## Import and setup
- Model at Roblox scale (1 stud is about 0.28 m in the avatar convention; check the project's character scale). Set pivots deliberately (`PivotTo` and `WorldPivot` are the modern API). Name meshes meaningfully before import.
- **Collision:** set `CollisionFidelity` per use. `Box` or `Hull` for most props, `PreciseConvexDecomposition` only where needed. Decor gets `CanCollide=false`, `CanQuery=false`, `CanTouch=false`.
- `RenderFidelity = Automatic` allows LOD. Provide sensible triangle counts for the on-screen size and reuse identical meshes, because identical mesh plus material instances render efficiently.
- **Textures:** size to on-screen importance (don't put 1024² on a pebble). Use `SurfaceAppearance` for PBR on hero assets. `MaterialVariant`s give a consistent material language across parts and terrain. Texture memory is the main mobile memory cost.
- **Audio:** normalize loudness, trim silence, and use variants for repeated sounds. Organize with `SoundGroup`s. Confirm the newer Audio API vs `Sound` usage matches the project.

## Organization
- Templates in `ServerStorage` (server-spawned) or `ReplicatedStorage` (client-cloned cosmetics). Use **Packages** for assets reused across places, and update them deliberately (auto-update can surprise you).
- Tag assets for systems (CollectionService) instead of relying on names deep in hierarchies.

## Sourcing
- **Creator Store and free models:** check the license and creator, and **scan for scripts and backdoors before insertion**. The procedure is in `roblox-security` (supply chain). Prefer mesh-only assets. Strip scripts you don't need.
- **AI generation** (Studio's mesh, material and procedural-model generation, available via Studio MCP `generate_*`): good for blockouts, props and variation. Review topology, scale, collision and art-direction fit. Generated assets still need the visual pillars (see `roblox-visual-direction`).
- Animations, audio and some assets must be owned or permitted by the experience owner (user vs group) to load. Check permissions when assets "don't load" in a group game.

## Budgets
Track per scene: unique meshes, triangles in view, texture memory, sound memory, and particle emitters. Set budgets with `roblox-performance` and check new asset packs against them before committing.
