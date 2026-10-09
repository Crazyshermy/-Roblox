# Post-import checks in Studio (scripts)

Read this for SKILL.md §5 c–i and the §6 player-distance check. Run each script with the Studio MCP's `execute_luau`. Replace `workspace.tower.LighthouseTower` with the imported MeshPart (the Model is named after the file, the MeshPart after the Blender object). Tags are the same as in SKILL.md.

## c) Verify (read-only, Edit DataModel)
Fill in the expected values from Blender:
```lua
local PART = workspace.tower.LighthouseTower
local EXPECT_SIZE, EXPECT_TRIS = Vector3.new(4, 26.907, 4), 314
local EXPECT_PIXELS = { ["239,236,231"] = 256 } -- palette: one entry per swatch, e.g. { ["112,72,42"] = 128, ["206,163,108"] = 128 }

local AssetService = game:GetService("AssetService")
local function rgb(c) return string.format("%d,%d,%d", math.floor(c.R * 255 + 0.5), math.floor(c.G * 255 + 0.5), math.floor(c.B * 255 + 0.5)) end
local out = {}
table.insert(out, string.format("Size %s (expect %s) | Orientation %s | Anchored %s | bottom Y %.3f",
	tostring(PART.Size), tostring(EXPECT_SIZE), tostring(PART.Orientation), tostring(PART.Anchored), PART.Position.Y - PART.Size.Y / 2))
table.insert(out, string.format("CollisionFidelity %s | Color %s | TextureID %q | children %d",
	tostring(PART.CollisionFidelity), rgb(PART.Color), PART.TextureID, #PART:GetChildren()))
local okM, em = pcall(function() return AssetService:CreateEditableMeshAsync(Content.fromUri(PART.MeshId)) end)
if okM then
	local tris = 0
	for _, f in em:GetFaces() do tris += #em:GetFaceVertices(f) - 2 end
	table.insert(out, string.format("triangles %d (expect %d)", tris, EXPECT_TRIS))
	em:Destroy()
else
	table.insert(out, "mesh read failed: " .. tostring(em))
end
if PART.TextureID ~= "" then
	local okI, img = pcall(function() return AssetService:CreateEditableImageAsync(Content.fromUri(PART.TextureID)) end)
	if okI then
		local buf, counts, list = img:ReadPixelsBuffer(Vector2.zero, img.Size), {}, {}
		for i = 0, img.Size.X * img.Size.Y - 1 do
			local k = string.format("%d,%d,%d", buffer.readu8(buf, i * 4), buffer.readu8(buf, i * 4 + 1), buffer.readu8(buf, i * 4 + 2))
			counts[k] = (counts[k] or 0) + 1
		end
		local same = true
		for k, n in counts do table.insert(list, k .. " x" .. n); same = same and EXPECT_PIXELS[k] == n end
		for k, n in EXPECT_PIXELS do same = same and counts[k] == n end
		table.insert(out, string.format("texture %dx%d: %s | matches expected: %s", img.Size.X, img.Size.Y, table.concat(list, " | "), tostring(same)))
		img:Destroy()
	else
		table.insert(out, "texture read failed: " .. tostring(img))
	end
end
return table.concat(out, "\n")
```

## d) Collision
**Raycasts** hit the collision shape, not the visible mesh [verified: hits sat outside the surface where Hull bulged]. For round-ish parts, cast inward from 32 directions at several heights, plus one ray straight down the axis, and compare against the mesh's radius. For other shapes, cast along the X and Z axes.
```lua
local PART = workspace.tower.LighthouseTower
local base = PART.Position - Vector3.new(0, PART.Size.Y / 2, 0)
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Include
params.FilterDescendantsInstances = { PART }
local reach, out = PART.Size.Magnitude, {}
for _, h in { 0.5, 2, PART.Size.Y * 0.5, PART.Size.Y * 0.9 } do
	local lo, hi = math.huge, 0
	for i = 0, 31 do
		local a = i / 32 * 2 * math.pi
		local dir = Vector3.new(math.cos(a), 0, math.sin(a))
		local hit = workspace:Raycast(base + Vector3.new(0, h, 0) + dir * reach, -dir * reach, params)
		if hit then
			local d = ((hit.Position - base) * Vector3.new(1, 0, 1)).Magnitude
			lo, hi = math.min(lo, d), math.max(hi, d)
		end
	end
	table.insert(out, string.format("h=%.1f collision radius %.3f..%.3f", h, lo, hi))
end
local down = workspace:Raycast(base + Vector3.new(0, PART.Size.Y + 10, 0), Vector3.new(0, -(PART.Size.Y + 20), 0), params)
table.insert(out, "down-ray on axis hits height " .. (down and string.format("%.3f", down.Position.Y - base.Y) or "nil"))
return table.concat(out, "\n")
```

**Playtest anything players touch** [verified method]:
1. `start_stop_play`.
2. In the Client DataModel, push the character into the part from 4 sides with `Humanoid:MoveTo` aimed past its center. Log the closest root-part distance and the Y range; Y should stay steady.
3. Walk a loop of waypoints around the base. (`character_navigation` can't target a point inside a solid object, so navigate beside it.)
4. Drop the character onto the top.
5. `get_console_output`, then stop the playtest.

```lua
local PART = workspace.tower.LighthouseTower
local char = game.Players.LocalPlayer.Character
local hum, hrp = char:FindFirstChildOfClass("Humanoid"), char.HumanoidRootPart
local axis = PART.Position * Vector3.new(1, 0, 1)
local function flat(p) return ((p - axis) * Vector3.new(1, 0, 1)).Magnitude end
local out = {}
for _, deg in { 0, 90, 180, 270 } do
	local dir = Vector3.new(math.cos(math.rad(deg)), 0, math.sin(math.rad(deg)))
	local y = hrp.Position.Y
	hrp.CFrame = CFrame.lookAt(axis + dir * (PART.Size.X / 2 + 5) + Vector3.new(0, y, 0), axis + Vector3.new(0, y, 0))
	task.wait(0.6)
	local closest, y0, y1, t0 = math.huge, math.huge, -math.huge, os.clock()
	while os.clock() - t0 < 3 do
		hum:MoveTo(axis - dir * 6)
		closest, y0, y1 = math.min(closest, flat(hrp.Position)), math.min(y0, hrp.Position.Y), math.max(y1, hrp.Position.Y)
		task.wait(0.05)
	end
	table.insert(out, string.format("from %d deg: closest %.2f, Y %.2f..%.2f, state %s", deg, closest, y0, y1, tostring(hum:GetState())))
end
hum:MoveTo(hrp.Position)
return table.concat(out, "\n")
```

## e) Screenshot and color comparison [verified method]
Use `screen_capture` with `camera_position` and `look_at_position`, one call at a time, and include a reference in the frame:
- a temporary anchored 4×4×4 Part one stud away, for scale, or
- the previous version, for color.

**For a color comparison:**
- Make each reference Part's face flush with, and facing the same way as, the face you measure, so both get the same light.
- Keep the references out of the model's shadow. `Lighting:GetSunDirection()` points toward the sun, so shadows fall the opposite way.
- Give the references the MeshPart's `Material`.
- A reference Part shows the material's surface grain, but the textured MeshPart showed none, so average a flat area.

Delete temporary parts afterwards. To compare colors objectively:
1. Load the screenshot JPG in Blender with colorspace `Non-Color`. The tool result gives its path.
2. Average a box of pixels inside each face. For a single color, you can average the bright, low-saturation pixels in each object's columns instead.
3. To check for blending, read a line of pixels across each color edge. It should step straight from one color to the other.
4. Remove the image again.

## f) Texture fidelity by fingerprint [verified method]
For textures bigger than a few swatches, compare fingerprints instead of pixel lists. For each channel compute the sum, the sum of squares, and the sum of value × (pixel index mod 9973), with pixels in top-to-bottom order. Equal fingerprints on both sides were taken as identical pixels; this method confirmed six uploaded textures (RGB and 8-bit gray, 512² and 512×256) and two later versions. Gray PNGs read back as R = G = B.
```python
# Blender: fingerprint of the source PNG (Blender's rows are bottom-up)
im = bpy.data.images.load(PNG, check_existing=False); im.colorspace_settings.name = "Non-Color"
W, H = im.size; p = im.pixels[:]; s, sq, ws = [0] * 3, [0] * 3, [0] * 3
for yt in range(H):
    base = (H - 1 - yt) * W * 4
    for x in range(W):
        k = (yt * W + x) % 9973
        for c in range(3):
            v = round(p[base + x * 4 + c] * 255); s[c] += v; sq[c] += v * v; ws[c] += v * k
bpy.data.images.remove(im); print(W, H, s, sq, ws)
```
```lua
-- Studio: the same fingerprint of a TextureID or SurfaceAppearance map (top-left origin)
local img = game:GetService("AssetService"):CreateEditableImageAsync(Content.fromUri(ID))
local W, H = img.Size.X, img.Size.Y
local buf = img:ReadPixelsBuffer(Vector2.zero, img.Size)
local s, sq, ws = { 0, 0, 0 }, { 0, 0, 0 }, { 0, 0, 0 }
for i = 0, W * H - 1 do
	local k = i % 9973
	for c = 0, 2 do local v = buffer.readu8(buf, i * 4 + c); s[c + 1] += v; sq[c + 1] += v * v; ws[c + 1] += v * k end
end
img:Destroy()
```
`SurfaceAppearance.ColorMap`, `NormalMap`, `RoughnessMap` and `MetalnessMap` were readable from `execute_luau`.

## g) Player-distance views at the user's pixel density [verified method]
- **Blender render (SKILL.md §6):** render at the Studio viewport size (`workspace.CurrentCamera.ViewportSize`, e.g. 1366 × 766) and vertical FOV (70°: camera Sensor Fit = Vertical, `angle_y` = 70°), with the sun from `Lighting:GetSunDirection()` mapped to Blender axes (SKILL.md §1).
- `screen_capture` returns an image only about 497 × 279, much smaller than the user's viewport. Read `workspace.CurrentCamera.ViewportSize` and `FieldOfView`.
- **Match the user's pixel density** by narrowing the field of view for the capture: FOV = `2·atan((279/2) / ((viewportHeight/2) / tan(FOV/2)))`. That's 28.62° for a 766-px-tall viewport at 70°. The capture's centre then shows what the user sees at 1:1. Set the FOV back afterwards.
- **Compare old vs new under the same light:**
  - Put temporary, unrotated copies side by side in a temp Folder, check overlaps with `GetPartBoundsInBox`, and delete the folder afterwards.
  - Or capture each model from an identical offset, centred.
- **Measure:** mask the object's pixels, keep the connected region nearest the image centre, and use the standard deviation of a 3×3 high-pass as "local contrast". JPEG noise raises every number a little, so compare like with like.
- Camera at 15 studs: e.g. offset (−3, 10.5, −10.2) or (−4.5, 5.25, −13.35) from the model's centre.

## h) PBR maps, A/B [verified method]
Clone the MeshPart, clear one map on the clone (`sa.NormalMap = ""` worked from `execute_luau`), and screenshot the original and the clone from the same relative camera, one capture at a time. Measure the difference (for a normal map, the row-to-row luminance stdev over the relief; for metalness, the mean luminance of the metal areas), then delete the clones.

## i) "It looks tilted": geometry or camera? [verified method]
- Read `Orientation`. Then take the ring centres from `EditableMesh` vertices at the top and bottom Y, using the midpoint of each ring's bounding box. Don't average the vertices: seam duplicates bias the mean (0.3° false tilt in the test).
- Capture from a level camera and check that the silhouette edges are vertical.
- A downward 70° camera with the object near the frame edge made a perfectly vertical barrel appear to lean 22° (measured with `WorldToViewportPoint` on its top and bottom centres).
