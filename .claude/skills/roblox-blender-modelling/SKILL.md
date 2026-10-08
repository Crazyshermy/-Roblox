---
name: roblox-blender-modelling
description: "Use when a model is made in Blender for Roblox, or a Blender FBX imports at the wrong size, color or orientation. Covers Blender MCP modelling at 1 unit = 1 stud, pivots, triangle budgets, color via embedded sRGB or palette textures, the exact FBX export and 3D Importer settings, and post-import MeshPart checks in Studio."
---

# Roblox modelling in Blender

You build and export the model with the Blender MCP. **The user runs Studio's 3D Importer.** It's a UI tool, so never try to drive it; give them exact settings instead. You then fix and check the result with the Studio MCP. General asset rules (collision choice, texture sizing, scene budgets, sourcing) belong to `roblox-assets`. This skill is the Blender-to-Studio procedure.

Every rule here is tagged:
- **[verified]**: confirmed after a real import. Setup: Blender 5.2.2 LTS, Blender MCP addon 1.8, Roblox Studio in Oct 2026. Test models: a 314-triangle 4 × 27 × 4 lighthouse tower and a 208-triangle 4 × 4 × 4 two-color crate. On other versions, assume it still holds, but confirm it in the post-import checks.
- **[file-checked]**: confirmed in Blender and in the exported FBX, but not yet after an import. What Studio does with it stays [untested] until an import confirms it.
- **[untested]**: a reasonable recommendation that hasn't been confirmed in Studio. Say so when you use it, and never report it as verified.

## Workflow
1. **Check tools.** Run the Blender MCP's `get_addon_status` and `get_scene_info`. You need the Studio MCP (`list_roblox_studios`) after the import. If no Studio is listed, ask the user to turn on *Assistant → … → Manage MCP Servers → Enable Studio as MCP server*.
2. **Build** the model (§1) and **color** it (§2).
3. **Export** and check the file (§3). Save the .blend as well, so source and export match.
4. **Hand over** the import settings (§4), then wait for the user to import.
5. **Fix and verify** in Studio (§5). Before the user saves the place, follow "Before the user saves" in `${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`.
6. **Report** with the table (§6).

**Default paths**, unless the user gives others:
- `<project>/blender/<asset>.blend`
- `<project>/blender/textures/<asset>_albedo.png`
- `<project>/exports/<asset>.fbx`

Look at an existing file before overwriting it.

**Starting a new asset while another asset's .blend is open:**
1. Check that `bpy.data.is_dirty` is False. If it isn't, ask before discarding anything.
2. Delete the old object.
3. Run `bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)`.
4. Run `bpy.ops.wm.save_as_mainfile(filepath=<new .blend>)`.

The old file stays untouched: the crate test left `tower.blend` byte-identical.

**Useful `.gitignore` lines:** `*.blend[0-9]*` (Blender backups), `*.lock` (Studio lock files), `*.fbm/` (textures Studio unpacks next to an imported FBX).

## 1. Build in Blender
- **Scale [verified].** Scene → Units: Unit System = None, Unit Scale = 1.0. Model in studs, so 1 Blender unit = 1 stud. With §3 and §4, a 4 × 26.907 × 4 object imported as `Size = 4, 26.907, 4`.
  ```python
  bpy.context.scene.unit_settings.system = 'NONE'; bpy.context.scene.unit_settings.scale_length = 1.0
  ```
- **Pivot at the base [verified].** Put the object's origin at the center of its base, at (0, 0, 0). With "Set Pivot to Scene Origin" on, the MeshPart's pivot lands there and the model sits at Y = 0.
- **One object per MeshPart [verified for one object].** Join everything that should be one MeshPart into one object. The importer made one MeshPart named after the object, inside a Model named after the file. Several objects in one FBX: [untested].
- **Apply all transforms [verified].** Run `bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)` with the origin at the base. The import came in at Orientation 0,0,0.
- **How to build:**
  - Generate the geometry with `bmesh` in one script.
  - Use flat shading (`use_smooth = False`) for a low-poly look.
  - Leave out faces that sit flush against another part, such as bar ends against posts or plank backs against a core box. Build each face with outward winding. On the crate, this cut 372 triangles (every box closed) to 208.
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

**Recipe [verified]:** a 16×16, 8-bit, sRGB PNG filled with the target color → Image Texture node → Principled Base Color. Set Base Color's fallback value to white, so the FBX writes `DiffuseColor = 1,1,1`. The mesh needs UVs; Smart UV Project is fine for a solid swatch. The importer uploaded the PNG as `MeshPart.TextureID` (no SurfaceAppearance), the pixels read back exactly, and the default `Color` (163,162,165) didn't tint the opaque texture: on screen it rendered within ~5 RGB levels of a reference part colored 239,236,231.

```python
import bpy, os
MAT = "TowerMat"                                       # the object's single material
PNG = "<project>/blender/textures/tower_albedo.png"    # absolute path, next to the .blend (save the .blend first)
RGB = (239, 236, 231)                                  # target color, sRGB 0-255

names = [i.identifier for i in bpy.types.ColorManagedInputColorspaceSettings.bl_rna.properties["name"].enum_items]
assert "sRGB" in names, names
os.makedirs(os.path.dirname(PNG), exist_ok=True)
img = bpy.data.images.new(os.path.splitext(os.path.basename(PNG))[0], 16, 16, alpha=False, float_buffer=False)
img.colorspace_settings.name = "sRGB"
img.pixels.foreach_set([RGB[0] / 255, RGB[1] / 255, RGB[2] / 255, 1.0] * 256)  # byte image: raw sRGB values
img.filepath_raw, img.file_format = PNG, 'PNG'
img.save()
img.filepath = bpy.path.relpath(PNG)
img.reload()

nt = bpy.data.materials[MAT].node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or nt.nodes.new("ShaderNodeTexImage")
tex.image, tex.interpolation = img, 'Closest'
nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # FBX DiffuseColor = 1,1,1
```
Read the PNG back with `bpy.data.images.load` and check every pixel × 255 equals `RGB`.

- **Several colors on one MeshPart** [verified for 2 swatches]: use a palette texture. Read `${CLAUDE_SKILL_DIR}/references/palette.md` for the swatch and UV code.
- **Vertex colors instead** [untested]: use a Color Attribute and export with `colors_type='SRGB'`. The importer reads vertex colors unless "Ignore Vertex Colors" is on. `MeshPart.Color` multiplies them, so it would need to be 255,255,255.

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
Steps 3–6 are the verified import [verified: tower and crate]. The model lands near the camera's focus, not at the origin.

## 5. After import (Studio MCP)
Get the `studio_id` with `list_roblox_studios`. Find the MeshPart: the Model is named after the file, the MeshPart after the Blender object. Studio MCP behavior that matters here (undo recording in `execute_luau`, one `screen_capture` at a time, `character_navigation` limits, Output clearing) is in `${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`. Put related edits in one `execute_luau` call.

**a) Set CollisionFidelity explicitly, every time** (the rule is in `roblox-assets`; the importer's choice varied for the same mesh).
- **Hull** for solid props [verified].
  - On a tapered tower it matched the visible surface within 0.04 studs at foot level. It bulged up to 0.33 studs under an overhang, and it closed over the open railing top like a lid.
  - On the box-shaped crate it was exactly the 4 × 4 × 4 box: 60 side rays hit at 2.000 studs and 25 top rays at 4.000. It bridged the planks' 0.12-stud recess, which is fine for a crate.
- **PreciseConvexDecomposition** where players walk on, inside or under the mesh [untested].
- **Box** for small decor [untested].
- The new value only reads back about a second later. Re-read it after `task.wait(1.5)` [verified].

**b) Set `Color` to the texture's color as a fallback.** Setting it doesn't change how an opaque TextureID looks [verified]. Whether it shows while the texture is still loading is [untested]. With a palette, see `${CLAUDE_SKILL_DIR}/references/palette.md`.

**c) Verify**, **d) collision** (raycasts, then a playtest for anything players touch) and **e) screenshot** (with a reference Part in frame, and an objective color comparison): run the scripts and methods in `${CLAUDE_SKILL_DIR}/references/studio-checks.md`. Raycasts hit the collision shape, not the visible mesh.

**f) Output.** Read `get_console_output`.

## 6. Report
End every run with this table:

| Verified live | Only checked in code | Could not test |
|---|---|---|

- **Verified live:** seen in Blender or Studio through the MCPs: property reads, mesh and texture readbacks, screenshots, playtests.
- **Only checked in code:** confirmed by reading files or running queries and scripts, but not seen or played in Studio. Examples: the parsed FBX, collision raycasts without a playtest.
- **Could not test:** not checked, with the reason. Never imply a check you didn't run, and keep every [untested] rule you relied on in this column until it's actually verified.
