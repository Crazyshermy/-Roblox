# FBX export: manual settings and the file check

Read this when the user exports by hand, and every time before you hand an FBX over (SKILL.md §3).

## The export call's settings in Blender's export panel
Use these when the user exports by hand (File → Export → FBX):
- **Limit to:** Selected Objects
- **Object Types:** Mesh
- **Scale:** 1.00
- **Apply Scalings:** FBX Units Scale
- **Forward / Up:** -Z / Y
- **Apply Unit:** on
- **Apply Transform:** on
- **Smoothing:** Face
- **Apply Modifiers:** on
- **Vertex Colors:** None
- **Triangulate Faces:** on
- **Add Leaf Bones:** off
- **Bake Animation:** off
- **Path Mode:** Copy, with the **Embed Textures** button on

## Check the file before handing it over
Blender bundles an FBX reader you can use. Set `OUT` (the .fbx) and `PNG` (the source texture) first:
```python
import importlib, hashlib
pf = importlib.import_module("io_scene_fbx.parse_fbx")
root, _ = pf.parse(OUT)
dec = lambda b: b.decode("utf-8", "replace").split("\x00")[0] if isinstance(b, bytes) else b
find = lambda e, i: next((x for x in e.elems if x.id == i), None)
objs = find(root, b"Objects")
kinds = {e.props[0]: dec(e.id) for e in objs.elems}
print("UnitScaleFactor", [p.props[4:] for p in find(find(root, b"GlobalSettings"), b"Properties70").elems if dec(p.props[0]) == "UnitScaleFactor"])
for e in objs.elems:
    if e.id == b"Model":
        print("Model", dec(e.props[1]), "Lcl props:", [dec(p.props[0]) for p in find(e, b"Properties70").elems if dec(p.props[0]).startswith("Lcl")])
    elif e.id == b"Geometry":
        v, idx = find(e, b"Vertices").props[0], find(e, b"PolygonVertexIndex").props[0]
        print("polys", sum(i < 0 for i in idx), "X", min(v[0::3]), max(v[0::3]), "Y", min(v[1::3]), max(v[1::3]),
              "Z", min(v[2::3]), max(v[2::3]), "vertex colors:", find(e, b"LayerElementColor") is not None)
    elif e.id == b"Material":
        print("DiffuseColor", [p.props[4:] for p in find(e, b"Properties70").elems if dec(p.props[0]) == "DiffuseColor"])
    elif e.id == b"Video":
        c = find(e, b"Content")
        print("embedded PNG identical:", c is not None and hashlib.sha1(c.props[0]).digest() == hashlib.sha1(open(PNG, "rb").read()).digest())
print("texture linked to:", [dec(c.props[3]) for c in find(root, b"Connections").elems if dec(c.props[0]) == "OP" and kinds.get(c.props[1]) == "Texture"])
```
**Expected results:**
- `UnitScaleFactor` is 100.
- The Model has no `Lcl` props.
- The geometry is Y-up, with Y running from 0 to the height. The X, Y and Z ranges equal the Blender dimensions.
- The polygon count equals the triangle count.
- `DiffuseColor` is 1,1,1, and the texture is linked to `DiffuseColor`.
- The embedded PNG is identical to the source.
- There are no vertex colors.

If any of these fail, fix the export before the user imports.
