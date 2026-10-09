---
name: roblox-blender-modelling
description: "Use when a model is made in Blender for Roblox, or a Blender FBX imports at the wrong size, color, texture or orientation. Covers Blender MCP modelling at 1 unit = 1 stud, pivots, triangle budgets, palette and baked textures, PBR maps, the exact FBX export and 3D Importer settings, post-import checks, and Open Cloud uploads."
---

# Roblox modelling in Blender

You build and export the model with the Blender MCP. **The user runs Studio's 3D Importer.** It's a UI tool, so never try to drive it; give them exact settings instead. Only when the user asks, upload or update the asset with the Open Cloud Assets API instead (`${CLAUDE_SKILL_DIR}/references/open-cloud.md`). You then fix and check the result with the Studio MCP. General asset rules (collision choice, texture sizing, scene budgets, sourcing) belong to `roblox-assets`. This skill is the Blender-to-Studio procedure.

Every rule here is tagged:
- **[verified]**: confirmed after a real import. Setup: Blender 5.2.2 LTS, Blender MCP addon 1.8, Roblox Studio in Oct 2026. Test models: a 314-triangle 4 × 27 × 4 tower and a 208-triangle two-color crate (flat colors), a 560-triangle worn stone and a 12-triangle plank (baked textures; the plank also went through Open Cloud), and a 288-triangle barrel with four PBR maps. On other versions, assume it still holds, but confirm it in the post-import checks.
- **[file-checked]**: confirmed in Blender and in the exported FBX, but not yet after an import. What Studio does with it stays [untested] until an import confirms it.
- **[untested]**: a reasonable recommendation that hasn't been confirmed in Studio. Say so when you use it, and never report it as verified.

**[verified] means verified in earlier testing, not by you in this session.** When you pass on a tagged rule, say "these settings were verified in earlier testing". Never write "I verified" or "in my notes" for it. Claim your own verification only for checks you actually ran in this session, and list those in §7.

## Workflow
1. **Check tools.** Run the Blender MCP's `get_addon_status` and `get_scene_info`. You need the Studio MCP (`list_roblox_studios`) after the import. If no Studio is listed, ask the user to turn on *Assistant → … → Manage MCP Servers → Enable Studio as MCP server*.
2. **Build** the model (§1) and **color** it (§2).
3. **Look at it from player distance** in Blender before anyone sees it (§6). Technical checks alone aren't enough.
4. **Export** and check the file (§3). Save the .blend as well, so source and export match.
5. **Hand over** the import settings (§4), then wait for the user to import. If the user asked for an API upload, follow `open-cloud.md` instead.
6. **Fix and verify** in Studio (§5), including the player-distance check in Studio (§6). Before the user saves the place, follow "Before the user saves" in `${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`.
7. **Report** with the table (§7).

**Default paths**, unless the user gives others: `<project>/blender/<asset>.blend`, `<project>/blender/textures/<asset>_albedo.png`, `<project>/exports/<asset>.fbx`. Look at an existing file before overwriting it.

**Starting a new asset while another asset's .blend is open:** check that `bpy.data.is_dirty` is False (if it isn't, ask before discarding anything), delete the old object, run `bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)`, then `bpy.ops.wm.save_as_mainfile(filepath=<new .blend>)`. The old file stays untouched: the crate test left `tower.blend` byte-identical.

**Useful `.gitignore` lines:** `*.blend[0-9]*` (Blender backups), `*.lock` (Studio lock files), `*.fbm/` (textures Studio unpacks next to an imported FBX).

## 1. Build in Blender
- **Scale [verified].** Scene → Units: Unit System = None, Unit Scale = 1.0. Model in studs, so 1 Blender unit = 1 stud. With §3 and §4, a 4 × 26.907 × 4 object imported as `Size = 4, 26.907, 4`. In code: `bpy.context.scene.unit_settings.system = 'NONE'; bpy.context.scene.unit_settings.scale_length = 1.0`.
- **Pivot at the base [verified].** Put the object's origin at the center of its base, at (0, 0, 0). With "Set Pivot to Scene Origin" on, the MeshPart's pivot lands there and the model sits at Y = 0.
- **One object per MeshPart [verified for one object].** Join everything that should be one MeshPart into one object. The importer made one MeshPart named after the object, inside a Model named after the file. Several objects in one FBX: [untested].
- **Apply all transforms [verified].** Run `bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)` with the origin at the base. The import came in at Orientation 0,0,0.
- **Axis mapping [verified].** With §3 and §4, Blender (x, y, z) arrives in Roblox as (−x, z, y): a 180° turn about the vertical, not a mirror. Blender's front (−Y) faces Roblox's Front (−Z). Use it to place details that must face a direction, and to match a Studio camera to a Blender render.
- **Worn or organic shapes [verified on one stone]:** decimate a dense mesh (Collapse) to the budget, measure the deviation from it, and spend triangles only where it's visible (`${CLAUDE_SKILL_DIR}/references/textures.md`, "Worn stone").
- **How to build:**
  - Generate the geometry with `bmesh` in one script.
  - Use flat shading (`use_smooth = False`) for a low-poly look.
  - Leave out faces that sit flush against another part, such as bar ends against posts or plank backs against a core box. Build each face with outward winding. On the crate, this cut 372 triangles (every box closed) to 208.
  - Check winding and UVs with a script, not by eye: every face normal points outward, and no UV island is mirrored (`(T × B) · n > 0`). The barrel's first build had 96 inside-out faces that only this check caught [file-checked].
  - Find shader nodes by type and read enum identifiers rather than hardcoding them (Blender MCP rules).
  - Check it with `look` from several angles before exporting.
- **Count triangles** from the evaluated mesh (`calc_loop_triangles()`). With a triangulated export it matches Studio exactly [verified: 314 = 314 and 208 = 208].

**Triangle budgets.** Roblox's hard limit is **20,000 triangles per mesh** (`${CLAUDE_SKILL_DIR}/../roblox/references/currency.md`). These starting budgets are [untested]. Scale them to the asset's size on screen and how many copies will appear; scene-wide budgets belong to `roblox-assets`.

| Asset type | Starting budget [untested] |
|---|---|
| Small prop (≤ 4 studs: cans, crates, rocks) | 50–300 |
| Medium prop or furniture (4–10 studs) | 300–1,500 |
| Building or landmark (10–40 studs) | 1,000–5,000 |
| Hero piece or very large structure | up to ~10,000; split it beyond that |

## 2. Color: an embedded sRGB texture, not a material color
**Why [verified]:** a plain Principled Base Color exports only as a legacy Phong `DiffuseColor`, holding Blender's linear values. Studio imported sRGB 239,236,231 as `MeshPart.Color = 151,139,138`, which matches neither the sRGB nor the linear reading of the stored value. Roblox's importer docs list only textures and vertex colors as ways an FBX carries color.

**Recipe [verified]:** a 16×16, 8-bit, sRGB PNG filled with the target color → Image Texture node → Principled Base Color. Set Base Color's fallback value to white, so the FBX writes `DiffuseColor = 1,1,1`. The mesh needs UVs; Smart UV Project is fine for a solid swatch. The importer uploaded the PNG as `MeshPart.TextureID` (no SurfaceAppearance), the pixels read back exactly, and the default `Color` (163,162,165) didn't tint the opaque texture (on screen, within ~5 RGB levels of a reference Part). **Run the one-color code in `${CLAUDE_SKILL_DIR}/references/palette.md`**, then read the PNG back and check every pixel.

- **Several colors on one MeshPart** [verified for 2 swatches]: use a palette texture (swatch and UV code in `palette.md`).
- **Vertex colors instead** [untested]: use a Color Attribute and export with `colors_type='SRGB'`. The importer reads vertex colors unless "Ignore Vertex Colors" is on. `MeshPart.Color` multiplies them, so it would need to be 255,255,255.
- **Real surface textures** (stone, wood, worn paint) [verified]: bake an object-space procedural to a 512² sRGB PNG and embed it the same way; it uploads as `TextureID` with byte-identical pixels. Lay wood grain's +U along the plank on every long face. Stay ≤ 1024 px (the docs disagree on the maximum; `currency.md`). Read `${CLAUDE_SKILL_DIR}/references/textures.md` first.
- **PBR maps → SurfaceAppearance [verified on one barrel]:** wire color, metalness, roughness and normal maps as in `textures.md` and add `use_tspace=True` to the §3 call. The importer made a `SurfaceAppearance` with all four maps, byte-identical and each visibly working.

## 3. Export the FBX
This exact call produced the verified import. Settings tagged [verified] in the comments had their individual effect confirmed.
```python
bpy.ops.export_scene.fbx(
    filepath=OUT, use_selection=True, object_types={'MESH'},
    global_scale=1.0, apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',   # [verified] raw values = Blender units; with Scale Unit = Studs, 1 BU = 1 stud
    axis_forward='-Z', axis_up='Y',
    bake_space_transform=True,               # [verified] Y-up baked into the mesh, no root rotation (static meshes only)
    use_mesh_modifiers=True, mesh_smooth_type='FACE',
    use_triangles=True,                      # [verified] Blender triangle count = Studio count
    colors_type='NONE', add_leaf_bones=False, bake_anim=False,
    path_mode='COPY', embed_textures=True,   # [verified] PNG embedded, uploaded as TextureID with exact pixels
)
```
**Always check the file before handing it over**, with the parser script and expected results in `${CLAUDE_SKILL_DIR}/references/fbx-check.md`. That file also lists these settings for a user who exports by hand.

## 4. Studio import: give the user these steps
```
1. If this replaces an earlier version, rename the old model first (e.g. tower → tower_old)
   so the two paths don't clash. Keep it as a reference until verification is done.
2. File → Import (may be labelled "Import 3D") → <project>\exports\<asset>.fbx
3. File Geometry → Scale Unit: Studs
4. File Transform → World Forward: Front, World Up: Top (the defaults)
5. File General → Anchored: on (for static props; the default is off)
               → Add to Workspace: on, Set Pivot to Scene Origin: on
               → Upload to Roblox: on (the texture uploads with the mesh)
6. Leave every other setting at its default.
7. Preview: right color(s) in the right places, no red "missing texture" warning → Import.
   Tell me when it's in.
```
Steps 3–6 are the verified import [verified: tower, crate, stone, plank, PBR barrel]. The model lands near the camera's focus, not at the origin.

**Open Cloud instead of the Importer** (only when the user asks): follow `open-cloud.md`, including its key and ID rules. It matches the Importer's size, axes, UVs, triangles and texture bytes, but arrives as a **package**, **unanchored**, with a **random yaw** and **no preview or warnings**. An update adds a version under the same asset ID, and **placed copies don't update by themselves** [all verified].

## 5. After import (Studio MCP)
Get the `studio_id` with `list_roblox_studios`. Find the MeshPart: the Model is named after the file, the MeshPart after the Blender object. Studio MCP behavior that matters here (undo recording in `execute_luau`, one `screen_capture` at a time, `character_navigation` limits, Output clearing) is in `${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`. Put related edits in one `execute_luau` call.

**a) Set CollisionFidelity explicitly, every time** (the rule is in `roblox-assets`). The Importer and the Open Cloud upload left it at Default on every test mesh except one tower import, which came in as PreciseConvexDecomposition [verified].
- **Hull** for solid props [verified on tower, crate, stone and barrel]. It hugged the walls (within 0.04 studs on the tower, 0.01 on the stone, exact on the crate and barrel), but bulged up to 0.33 studs under an overhang and closed over open tops and shallow recesses (the crate's 0.12-stud plank recess) like a lid.
- **Box** for meshes that are boxes [verified by raycasts, no playtest: exact on the plank], and for small decor of other shapes [untested]. **PreciseConvexDecomposition** where players walk on, inside or under the mesh [untested].
- The new value only reads back about a second later. Re-read it after `task.wait(1.5)` [verified].

**b) Set `Color` to the texture's color as a fallback** (for a detailed texture, its mean color). Setting it doesn't change how an opaque TextureID looks [verified]. Whether it shows while the texture is still loading is [untested]. With a palette, see `${CLAUDE_SKILL_DIR}/references/palette.md`.

**c) Verify**, **d) collision** (raycasts, then a playtest for anything players touch) and **e) screenshot** (with a reference Part in frame, and an objective color comparison): run the scripts and methods in `${CLAUDE_SKILL_DIR}/references/studio-checks.md`. Raycasts hit the collision shape, not the visible mesh. The same file has **f)** texture fingerprints, **g)** captures at the user's pixel density, **h)** PBR map A/B tests and **i)** tilt vs camera perspective: a barrel that "looked tilted" was a downward camera, not geometry [verified], so check (i) before changing a model. Then read `get_console_output`.

## 6. Visual check from player distance (before showing the model)
Technical checks (size, triangles, byte-identical pixels) are not enough. In the first texture test every check passed, and the user still saw a stone that read as a tiled box and a plank that read as flat tan [verified].
- **Blender, before export:** render at the Studio viewport size and 70° vertical FOV, with the sun from `Lighting:GetSunDirection()` (setup in `studio-checks.md` g): 3 angles that each show a lit face, plus one from about 15 studs judged at 1:1 pixels.
- **Studio, after import:** capture at the user's pixel density (`studio-checks.md` g), close up and at 15 studs, next to any previous version. Studio rendered textures brighter than EEVEE, so judge readability in Studio [verified].
- **Ask:** does it read as the object, or as a box with a picture on it? Is the detail that sells it (grain, chips, cracks) still there at 1:1?
- **Scale of detail:** at 15 studs and 70° on a 766-px-tall viewport, 1 stud ≈ 36 px. Detail finer than ~4 px averages away under mip filtering, and raising contrast alone doesn't bring it back; make the features bigger [verified on the plank: grain local contrast 5 → 10 in Studio].

## 7. Report
End every run with this table:

| Verified live | Only checked in code | Could not test |
|---|---|---|

- **Verified live:** seen in Blender or Studio through the MCPs: property reads, mesh and texture readbacks, screenshots, playtests.
- **Only checked in code:** confirmed by reading files or running queries and scripts, but not seen or played in Studio. Examples: the parsed FBX, collision raycasts without a playtest.
- **Could not test:** not checked, with the reason. Never imply a check you didn't run, and keep every [untested] rule you relied on in this column until it's actually verified.
