# Color textures: one swatch or a palette

Read this for the SKILL.md §2 recipe. Tags are the same as in SKILL.md.

## One color [verified]
Fill a 16×16, 8-bit, sRGB PNG with the target color, wire it to Principled Base Color, and set Base Color's fallback to white:
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

## Several colors on one MeshPart: a palette texture
**[verified for 2 swatches]** A MeshPart has one `TextureID`, so every color goes into one PNG with one swatch per color, and each face's UVs sit inside its swatch.
- While you build, tag each face with its swatch index in an int face attribute.
- Use the one-color block above, but replace the solid fill with vertical swatches (first block below).
- Set the UVs with the second block. It projects each face onto its main plane and shrinks it into the middle half of its swatch.
- Margins: with 2 swatches every UV stays at least 2 texels inside its swatch, and nothing blended in Studio [verified]. With 3–4 swatches the margin drops to 1 texel; that's [file-checked] in Blender only, and Studio's filtering at 1 texel is [untested].
- The block removes the tag attribute, so it isn't exported.

```python
SWATCHES = [(112, 72, 42), (206, 163, 108)]  # sRGB 0-255, one per color; up to 4 in a 16x16 PNG
N = len(SWATCHES)
img.pixels.foreach_set([c for row in range(16) for col in range(16)  # replaces the solid fill
                        for c in (*(x / 255 for x in SWATCHES[col * N // 16]), 1.0)])
```
```python
import bmesh
from mathutils import Vector
OBJ, TAG = "WoodenCrate", "swatch"  # TAG: int face attribute set while building, index into SWATCHES
me = bpy.data.objects[OBJ].data
bm = bmesh.new(); bm.from_mesh(me); bm.normal_update()
tag, uv = bm.faces.layers.int[TAG], bm.loops.layers.uv.verify()
lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
mid, size = (lo + hi) / 2, max(hi - lo)
for f in bm.faces:
    ax = max(range(3), key=lambda i: abs(f.normal[i]))
    a, b = [i for i in range(3) if i != ax]
    cu = (f[tag] + 0.5) / N
    for l in f.loops:
        p = (l.vert.co - mid) / size  # each axis within -0.5..0.5
        l[uv].uv = (cu + p[a] * 0.5 / N, 0.5 + p[b] * 0.5 / N)
bm.to_mesh(me); bm.free()
me.attributes.remove(me.attributes[TAG])  # build helper only; keep it out of the export
```
Read the PNG back and check each pixel against `SWATCHES[col * N // 16]`. Check that each face's U stays within `[i / N, (i + 1) / N]` for its swatch `i`.

**What the crate import showed [verified, 2026-10-08]** (two swatches: planks 112,72,42 and trim 206,163,108):
- The importer made one MeshPart with a `TextureID` and no SurfaceAppearance.
- The uploaded texture read back as 16×16 with exactly 128 pixels of each color.
- The top and all four sides rendered each face in its swatch's color. Against same-facing reference Parts in the same sunlight, the trim came within 3 RGB levels and the planks within 6.
- Swatch edges didn't blend, close up (2.5 studs) or at 11 studs. A pixel line across a trim-to-plank edge stepped straight from `196,175,132` to `~110,72,49` with one anti-aliased pixel between. Plank pixels next to the trim were no lighter than the plank's center.

**Checked in Blender and the FBX only [file-checked]:** the blocks above, re-run on a copy of the crate, reproduced its UVs and pixels exactly. The FBX checks matched SKILL.md §3 (byte-identical PNG, `DiffuseColor` 1,1,1).

**Not tested:**
- 3–4 swatches, where the margin is 1 texel.
- The bottom face, which sat on the ground.
- Very long viewing distances.

**After import:** `MeshPart.Color` holds only one value; set it to the color that covers the most surface. It doesn't tint the other swatches [verified]: with `Color` set to the plank brown, the crate's trim still rendered within 3 RGB levels of a trim-colored reference Part.
