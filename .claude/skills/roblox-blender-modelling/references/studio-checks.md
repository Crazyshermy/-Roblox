# Post-import checks in Studio (scripts)

Read this for SKILL.md §5 c–e. Run each script with the Studio MCP's `execute_luau`. Replace `workspace.tower.LighthouseTower` with the imported MeshPart (the Model is named after the file, the MeshPart after the Blender object). Tags are the same as in SKILL.md.

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
