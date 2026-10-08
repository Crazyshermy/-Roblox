# Blender → Roblox Studio imports: live results (2026-10-07 and 2026-10-08)

**Run details:** Blender 5.2.2 LTS · Blender MCP addon 1.8 · Roblox Studio 3D Importer (October 2026; exact Studio version not recorded) · Roblox Studio's built-in MCP server · Windows. Claude Code version and model not recorded. One tester.

These are the imports behind the **[verified]** tags in `.claude/skills/roblox-blender-modelling/`. Checks were made through the Studio MCP: property reads, mesh and texture readbacks with `EditableMesh` and `EditableImage`, raycasts, playtests and screenshots.

## Test models
| Model | Triangles | Size (studs) | Color |
|---|---|---|---|
| Lighthouse tower: 16-sided, tapered, open railing top | 314 | 4 × 26.907 × 4 | one color, sRGB 239,236,231 |
| Wooden crate: core box, 12 trim bars, 18 planks; faces flush against another part left out (372 → 208) | 208 | 4 × 4 × 4 | two-swatch palette: planks 112,72,42, trim 206,163,108 |

## Results
| Check | Result |
|---|---|
| Scale: Unit System None, FBX Units Scale, importer Scale Unit = Studs | 1 Blender unit = 1 stud: `Size` matched the Blender dimensions for both models |
| Pivot: origin at the base center, "Set Pivot to Scene Origin" on | Base at Y = 0 |
| Orientation: `bake_space_transform=True` (Apply Transform) | `Orientation` 0,0,0, no root rotation |
| Triangle count: `use_triangles=True` | Blender = Studio exactly (314 = 314, 208 = 208), read back with `EditableMesh` |
| **Material color only** (Principled Base Color, no texture), 2026-10-07 | Imported as `MeshPart.Color` **151,139,138** instead of 239,236,231. Matches neither the sRGB nor the linear reading of the stored value |
| **Embedded sRGB texture + white Base Color fallback**, 2026-10-08 | Importer uploaded the PNG as `MeshPart.TextureID` (no SurfaceAppearance). Readback: 16×16, every pixel 239,236,231. `Color` stayed at the default 163,162,165 and didn't tint the opaque texture. Mean on-screen RGB 213,220,227 vs 218,225,231 for a hand-colored reference Part |
| **Two-swatch palette** (crate), 2026-10-08 | One MeshPart with a `TextureID`. Readback: exactly 128 pixels of each color. Top and four sides rendered within 3 RGB levels (trim) and 6 (planks) of same-facing reference Parts. No blending at swatch edges at 2.5 or 11 studs. Setting `Color` to the plank brown didn't tint the trim |
| CollisionFidelity on import | Varied: the same tower mesh came in as PreciseConvexDecomposition on 2026-10-07 and as Default on 2026-10-08. The crate came in as Default |
| `Hull` collision | Tower: within 0.04 studs of the surface at foot level, bulging up to 0.33 studs under an overhang, closed over the open top like a lid (down-ray hit at 26.907). Crate: exactly the 4 × 4 × 4 box (60 side rays at 2.000, 25 top rays at 4.000). Playtest on the tower: pushed from 4 sides, walked a loop, dropped onto the top, with a steady Y |

## Studio MCP behavior seen during these runs
- `execute_luau` (Edit DataModel) already runs inside a ChangeHistory recording: `IsRecordingInProgress()` returned true, `TryBeginRecording()` returned nil, the edits still applied, and the undo history showed one "Assistant" entry.
- A `CollisionFidelity` set from a script only read back as the new value about 1 s later.
- Three parallel `screen_capture` calls moved the same camera. One returned, and the other two stalled past 120 s until stopped. Sequential calls returned in seconds.
- `character_navigation` can't target a point inside a solid object.
- A Rojo project with no place lock (`servePlaceIds`) synced into a test place it didn't belong to and pushed another game's scripts and parts into it.

## Not tested
3–4 swatch palettes (1-texel margin), the bottom face, very long view distances, several objects in one FBX, vertex colors, `PreciseConvexDecomposition` and `Box` on these meshes, whether `Color` shows while the texture loads, whether one Ctrl+Z reverts exactly one `execute_luau` call, and whether Ctrl+S misbehaves for local place files (forum reports only).
