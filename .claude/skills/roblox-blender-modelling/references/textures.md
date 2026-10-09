# Real textures: baked procedurals, wood grain, worn stone, PBR

Read this when a model needs more than flat colors (SKILL.md §2). Tags are the same as in SKILL.md. Evidence: Oct 2026 tests with a 3 × 2 × 2 stone block, a 6 × 0.3 × 1 plank and a 2.2 × 3.2 × 2.2 PBR barrel, all imported with the SKILL.md §3–§4 settings.

## Size and density
- **Maximum:** the docs disagree (4096 vs 1024; details in `${CLAUDE_SKILL_DIR}/../roblox/references/currency.md` → Assets). Stay at or under 1024 until a bigger upload has been checked [untested above 1024].
- **512×512 and 512×256 uploaded at full size with exact pixels** [verified]. Non-square textures are fine.
- **Density:** about 70–80 px/stud for props seen up close (512² on a 3 × 2 × 2 block gave 74–79 px/stud). Roblox's own Part materials are 1024 px per 8 studs = 128 px/stud. For the docs' map-size budget by asset size, see `currency.md`.

## Bake a procedural material to an image [verified]
1. Build the material from **object-space** procedurals (Texture Coordinate → Object), so the pattern runs continuously across UV seams.
2. Give the mesh **uniform texel density**. Smart UV Project at a 66° angle limit merged 45° chamfers into their faces and stretched them ×1.41; 30–50° gave every face its own island at one density. Check per face: `sqrt(uv_area / area) × texture_size` = px/stud [file-checked].
3. **Bake in Cycles:** `type='DIFFUSE'`, pass filter Color only (direct and indirect off), into a byte sRGB image. Pre-fill the image with the material's mean color, then bake with margin 16, margin type Extend, `use_clear=False`. A cleared (black) background bleeds into lower mip levels [file-checked].
4. Save the PNG and build the final material: Image Texture (Linear) → Base Color, fallback white (SKILL.md §2). Keep the procedural material in the .blend with a fake user for re-baking.
5. **Check the bake:** render the procedural and the baked material from the same camera. The mean difference was 0.12–0.32 levels in every test.

- An Ambient Occlusion node mixed into the color bakes into the albedo [file-checked]. It helps chips and cracks read on a TextureID-only mesh.
- The diffuse color pass is black on metallic areas (diffuse = base × (1 − metallic)). Bake color, roughness and metalness through an Emission shader with `type='EMIT'` instead [file-checked].
- Studio rendered baked textures slightly brighter and cooler than a Blender EEVEE render from the same camera and sun direction (stone front face 106,109,110 vs 98,98,94) [verified].

## Wood grain that runs along the plank [verified]
- **UVs by hand:** on every long face, +U runs along the plank's length at one density. Check each face isn't mirrored (`(T × B) · n > 0`). The end faces can go in a spare column, rotated.
- **Grain in 3D:** rings around the length axis, with the log's axis outside the board. Long faces then show lines along the length and the ends show end-grain arcs.
- **Check the baked image:** the brightness change across the grain (V) was 10–17× the change along it (U) on all four long faces. In Studio the grain ran along the plank.
- **Natural, not stylized** [user verdict, seen in Studio]: equal spacing with uniform waves read as stylized. What read as natural:
  - remap the radial coordinate with low-frequency noise so line spacing varies ±20–30%;
  - drift the lines slowly along the length;
  - add waviness only in some stretches (noise-masked);
  - vary each line's darkness.
- **Visible from play distance:** see SKILL.md §6. On a 1366 × 766 viewport at 70° and 15 studs, 1 stud ≈ 36 px.
  - Lines ~0.09 studs apart averaged into flat tan.
  - Lines ~0.14 studs apart with dark latewood (sRGB ~104,63,32 against ~210,163,108 earlywood, fading little from line to line) kept a local contrast of 10.1 in Studio (3×3 high-pass stdev, 1:1 capture). Faint versions measured 5–6.7 [verified].
  - Raising contrast doesn't rescue lines that are too fine; make them bigger.

## Worn stone [verified on one 560-triangle block]
**Geometry:**
- Build a dense grid box: `subdivide_edges(cuts=59, use_grid_fill=True)` gave ~43k triangles on a 3 × 2 × 2 block.
- Round the edges with a radius that varies by noise (0.02–0.1 studs).
- Push faces ±0.012 studs; keep the bottom flat so the block sits flush.
- **Chips as planar fractures:** one plane cuts a corner; two planes meeting in a ridge cut an edge. Project points outside both planes onto the nearer one. Noise-scooped craters read as dents, not chips.
- **Decimate** (Collapse) and measure the deviation from the dense mesh: 560 triangles stayed within 0.008 studs. 400 stayed within 0.009 but showed triangle-shaped shading patches up close. Shade smooth with sharp edges by angle (~38°). Studio's triangle count matched (560 = 560).

**Texture:**
- Don't make cracks with Voronoi distance-to-edge: it read as tile grout or paving.
- Build it from:
  - broad color variation and fine grain speckle;
  - faint bedding bands;
  - edge wear from the distance to the original box's edges (patchy, not a uniform light outline);
  - slightly lighter, fresher stone on the chips (depth below the original box surface);
  - grime toward the base;
  - one or two cracks as a noise-distorted plane with a fading mask;
  - baked AO.
- Horizontal bands crossed with vertical streaks made a plaid; use one or the other.
- At 15 studs, in Studio's bright light, the mottling mostly washes out and the chips carry the "weathered" read.

## PBR set for a SurfaceAppearance [verified on one barrel]
**Blender:**
- **Material wiring** (the wiring Roblox's Blender texture-settings page describes): a Principled BSDF with four Image Textures:
  - color (sRGB) → Base Color;
  - metalness (Non-Color) → Metallic;
  - roughness (Non-Color) → Roughness;
  - normal (Non-Color) → Normal Map node (Tangent space, the mesh's UV map) → Normal.
- **Normal map:** bake it from the procedural bump: `type='NORMAL'`, `normal_space='TANGENT'`, swizzle `POS_X POS_Y POS_Z` (OpenGL, which Roblox expects).
- **PNG formats:** color and normal as 8-bit RGB, roughness and metalness as 8-bit single-channel grayscale, as Roblox's texture spec asks. `image.save()` writes RGB, so write the PNG bytes yourself (code below) and load that file back into the material.
- **Export:** the SKILL.md §3 call plus `use_tspace=True`, which adds tangent and binormal layers; the SurfaceAppearance docs say imported meshes need tangents. Whether Studio actually needs them is [untested]: no export without them was tried.
- **FBX slots Blender writes:** color → DiffuseColor, normal → NormalMap, roughness → ShininessExponent, metalness → ReflectionFactor [file-checked].

**Studio** (SKILL.md §4 settings):
- The importer made a `SurfaceAppearance` with ColorMap, NormalMap, RoughnessMap and MetalnessMap. `TextureID` stayed empty, AlphaMode was Overlay, `Color` white [verified].
- All four maps read back byte-identical, and roughness wasn't inverted [verified].
- **The maps work** [verified by A/B]:
  - A copy with `NormalMap` cleared lost the hoop relief: painted-surface row-to-row luminance stdev 3.07 → 0.46.
  - A copy with `MetalnessMap` cleared turned bare-steel areas from reflective to flat grey: luminance 89 → 145.
- Studio rendered the paint brighter and bluer than Blender (lit front 36,81,166 vs 21,71,124). That's lighting, not the maps.
- A mostly painted object (7% metal pixels) reads as painted metal; don't expect chrome. Metalness needs `Lighting.EnvironmentSpecularScale` > 0 (docs); it was 1 in the test place.

```python
import zlib, struct
def write_png(path, w, h, rows, ctype):  # rows: one bytes object per row, top row first; ctype 0 = gray, 2 = RGB
    raw = b"".join(b"\x00" + r for r in rows)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
# From a Blender image: pixels are RGBA floats, bottom row first. Round each to 0-255, flip the rows,
# keep R for gray (ctype 0) or RGB (ctype 2). Reload the file and compare every channel with the bake.
```

## UVs in Studio [verified]
Studio's `EditableMesh` reports V as 1 − Blender's V (image origin at the top left). It's the same image, not flipped on the model. For the axis mapping, see SKILL.md §1.
