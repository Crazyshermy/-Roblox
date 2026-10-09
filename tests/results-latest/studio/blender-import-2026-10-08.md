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

## Texture, PBR and Open Cloud tests (2026-10-08, evening)
**Run details:** as above, plus Claude Code 2.1.295 · Opus 5.5 (effort and Apex version not recorded) · the Open Cloud Assets API v1 from Git Bash with Windows' `curl.exe`. Same tester. These are the imports behind the texture, PBR, player-distance and Open Cloud **[verified]** tags added in Apex 1.4.0. Asset and user IDs are left out of this record.

### Test models
| Model | Triangles | Size (studs) | Texture |
|---|---|---|---|
| Worn stone block, v1 | 44 | 3 × 2 × 2 | 512² baked albedo |
| Worn stone block, v2: chipped corners, worn edges, one crack | 560 (decimated from ~43k, within 0.008 studs) | 3 × 2 × 2 | 512² baked albedo with baked AO |
| Wooden plank, v1 → v2 → v3 → v3.1 (wider grain, latewood lines, irregular spacing) | 12 | 6 × 0.3 × 1 | 512×256 baked wood grain |
| Barrel, 24-sided, steel hoops | 288 | 2.2 × 3.2 × 2.2 | 512² color, normal, roughness and metalness |

### Results (Importer, SKILL.md §3–§4 settings, `use_tspace=True` for the barrel)
| Check | Result |
|---|---|
| Baked procedural → `TextureID` | All textures read back byte-identical (per-channel sums and fingerprints). 512×512 and 512×256 kept full size |
| Axis mapping | Blender (x, y, z) arrived as (−x, z, y), a 180° turn about the vertical, not a mirror. `EditableMesh` reports V as 1 − Blender's V (same image) |
| Wood grain | With +U along the length on every long face, the grain ran along the plank in Studio |
| Triangle count | 560 = 560 (stone v2) and 12 = 12 (plank) |
| PBR → `SurfaceAppearance` | ColorMap, NormalMap, RoughnessMap and MetalnessMap all present and byte-identical; roughness not inverted; `TextureID` empty, AlphaMode Overlay, `Color` white. 8-bit grayscale PNGs read back as R = G = B |
| PBR A/B | NormalMap cleared on a copy: painted-surface row-to-row luminance stdev 3.07 → 0.46 (hoop relief gone). MetalnessMap cleared: scraped-steel mean luminance 89 → 145 (reflective → flat grey) |
| CollisionFidelity on import | Default on all three meshes |
| Hull | Barrel: matched the 24-sided wall (1.091–1.100) and closed over the shallow lid recess. Stone v2: within 0.01 studs of the faces, followed the corner chip (1.39 instead of 1.5). Raycasts only |
| Box | Plank: side hits at exactly 3.000 and 0.500, top at 0.300. Raycasts only, no playtest |
| Re-import of unchanged geometry | Plank v2 kept the same MeshId as v1 and got a new TextureID |
| Blender vs Studio color | Stone v2 front face 106,109,110 in Studio vs 98,98,94 in a Blender EEVEE render from the same camera and sun; barrel paint 36,81,166 vs 21,71,124. Studio rendered brighter and cooler |
| "Tilted" barrel | Axis 0.00000° from vertical, base at Y = 0. A downward 70° camera with the barrel near the frame edge showed a 22° lean (`WorldToViewportPoint`) |

### Player-distance review
Every technical check on stone v1 and plank v1 passed, but the user's visual review rejected both: the stone read as a tiled box and the plank as flat tan at play distance. This led to the SKILL.md §6 check.
- 1:1 captures: `screen_capture` returns about 497 × 279. A `FieldOfView` of 28.62 (for a 1366 × 766 viewport at 70°) matched the user's pixel density at the capture's centre.
- Plank local grain contrast at 15 studs, 1:1, 3×3 high-pass stdev: v1 5.0, v2 9.1–10.9, v3 6.7 (more natural, softer), v3.1 10.1. The user judged evenly spaced, uniformly wavy grain as stylized.
- Stone v2 in Studio matched its Blender render from the same camera.

### Open Cloud Assets API (plank v3 and v3.1)
| Check | Result |
|---|---|
| Create (`POST /assets/v1/assets`, `assetType` Model, `expectedPrice` 0) | Operation done within 3 s, moderation Approved, no fee |
| A `;` in the request JSON | `400 Unterminated string`; nothing created (curl's `-F` reads `;` as a separator) |
| Key handling | Read from a user-scope environment variable at each call and passed on stdin (`-H @-`); never printed or written |
| Compared with the Importer | Same size (no scale setting), axis mapping, pivot, 12 triangles and byte-identical texture. Different: arrived as a package (Model + `PackageLink`), `Anchored` false, a new MeshId for geometry identical to an earlier upload. `Color` and `CollisionFidelity` at defaults |
| Studio MCP `insert_asset` | Landed at the camera focus with a −144° yaw and an `Assistant:<guid>` CollectionService tag |
| `InsertService:LoadAsset` | Latest revision as a plain Model, no `PackageLink` |
| Update (`PATCH`, content only, no `updateMask`) | Done within 3 s as revision 2 of the same asset, Approved. New TextureID, byte-identical to the new PNG; MeshId reused (geometry unchanged) |
| Placed package copy after the update | Stayed on `PackageLink.VersionNumber` 1 with the old TextureID for ~100 s. `AutoUpdate` and `Status` aren't readable from MCP `execute_luau`, so "AutoUpdate off" is inferred from the docs, not read |

### Not tested
Textures above 1024 px, an export without tangents, group creators, glTF/GLB uploads, metadata-only updates, version rollback, updating a placed copy from Studio's package menu or with AutoUpdate on, and a playtest on the stone, plank or barrel collision.
