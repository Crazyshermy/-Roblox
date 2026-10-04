---
name: roblox-visual-direction
description: "Roblox art direction: visual identity, lighting (Future, Atmosphere, post-processing), color and palette roles, composition, readability, materials and PBR, environmental storytelling, VFX art, escaping the default-Roblox look."
---

# Visual direction

Visuals serve **readability first, mood second, spectacle third**. A beautiful scene where players can't read threats, paths or interactables is a failed scene.

## Establish the visual identity (once per project; record in `.apex/project.md`)
- 3–5 **visual pillars** in words ("sodium-orange night, wet reflective streets, silhouettes over detail").
- **Palette**: a limited set of hues with roles — environment base, accent, *interactable*, *danger*, UI. Gameplay-critical colors are reserved and never used decoratively.
- **Shape language**: rounded/friendly vs sharp/hostile; silhouette clarity at gameplay distance.
- **Material language**: which surfaces are matte/rough/worn; consistent texel density.

## Lighting (biggest quality lever in Roblox)
- Set the lighting intent with `Lighting.LightingStyle` (`Enum.LightingStyle.Realistic` for a naturalistic look, `Soft` for a stylized one), and use `Lighting.PrioritizeLightingQuality` to choose whether shading quality or view distance scales down first on weaker devices. **`Lighting.Technology` (Future/ShadowMap/Voxel) is deprecated** (E4, 2026-10), so don't recommend it in new work. Lower-end devices scale quality down automatically, so design for the fallback look too.
- `Atmosphere` (density, haze, glare, color, decay) for depth and mood; `Sky`/skybox matching the time of day; `ClockTime` art-directed, not default noon.
- Post-processing: `ColorCorrectionEffect` (grade, contrast), `BloomEffect` (restrained), `DepthOfFieldEffect` (cinematics/menus only), `SunRaysEffect`. Grade toward the palette.
- Use local lights to **guide the player** (light pools mark paths and objectives) — composition and level design meet here.
- Check `Brightness`, `ExposureCompensation`, `EnvironmentDiffuseScale`/`EnvironmentSpecularScale` together; avoid flat ambient that kills form.

## Composition and readability checks
- **Squint test**: at a blur, can you read the path, the player, and threats? Value contrast (light/dark) carries readability more than hue.
- Focal points: one per view; lead the eye with lines, light, and contrast.
- Gameplay distance: check at actual camera distance on a **phone screen**, not a zoomed-in editor view.
- Density gradients: detail clusters near points of interest, calmer between.

## Escaping "default Roblox"
Default skybox + noon lighting + default materials + uniform part sizes + floating UI = instant genericness. Counter with: art-directed time of day, custom MaterialVariants or SurfaceAppearance PBR meshes, a cohesive modular kit, decals for wear/dirt, scale variation, and a lighting grade.

## Environmental storytelling
Place evidence of events (barricades, abandoned objects, scorch marks, trails) so the space tells what happened; reward attention with discovery. Tie it to the game's mystery or fantasy, not random clutter.

## VFX art
Readable shape first (silhouette of the effect), then color within palette, then secondary motion. Effects communicate **gameplay information** (area, timing, ownership) before decoration. Budget particles (see `roblox-performance`).

## Verify
Capture screenshots (`screen_capture`) at gameplay camera positions on desktop and a phone-sized viewport; critique against the visual pillars and readability checks. State that aesthetic judgments are E1 opinions unless backed by player tests.
