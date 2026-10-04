# 09: Visual Intelligence (N) and Asset Intelligence (O)

## N. Visual Intelligence

### N.1 Capture pipeline

```
shots.yaml ──► Shot runner (Edit DM or Client DM during test)
                ├─ set device preset (StudioDeviceSimulatorService)
                ├─ freeze determinism: Lighting.ClockTime fixed, physics paused or test-step,
                │   ParticleEmitters: seeded/disabled or "capture after N emits", streaming: wait for
                │   region loaded (RequestStreamAroundAsync), animations: pose at time t
                ├─ position camera (CFrame/FOV) or follow a bot at timeline mark
                ├─ capture (StudioCaptureService / built-in screen_capture fallback)
                │   + UI geometry dump (all visible GuiObjects: rects, text, ZIndex, visibility)
                └─ store PNG (CAS, blake3) + metadata {shot, device, checkpoint, studio_version}
```

Shot definitions:

```yaml
shots:
  - id: hub.overview
    camera: {cframe: [0, 40, -60, 0, 0, 0], fov: 60}      # or "follow: bot-0 @ t=12s"
    clock_time: 18.5
    ui: true
    devices: [desktop-1080p, phone-landscape-19.5x9]
  - id: combat.heavy-hit
    filmstrip: {scenario: combat.heavy-swing-hits-dummy, around_event: Feel.Impact, frames: 16, fps: 20}
```

### N.2 Analysis layers (cheapest first)
1. **UI geometry audit** (deterministic, see file 08 Device testing). It catches overlap, clipping, safe-area problems, truncation, tiny text, small touch targets, and occlusion. This is where "objective text overlaps the crosshair" is found, *without* vision.
2. **Regression diff** against the baseline:
   - SSIM per shot, plus a tiled region diff for localized changes.
   - pHash for a coarse check.
   - Missing-asset detection: magenta or blank textures, `ContentProvider` failures in the runtime log, and meshes not loaded.
3. **Metrics:**
   - Luminance histogram (crushed blacks, blown highlights).
   - Palette extraction compared with the constitution's art-direction palette.
   - Contrast of UI text over the rendered background.
   - Visual-noise estimate (edge density) for readability.
4. **Vision judgment** (the `art-director` agent) runs only on:
   - shots flagged by layers 1–3,
   - milestone reviews, or
   - explicit requests.

   Inputs are a downscaled shot or tiled filmstrip, the art-direction section of the constitution, the rubric, and prior critiques of the same shot (so it doesn't repeat itself).

**Art-director rubric:** composition and focal point, lighting mood vs. intent, scale and readability of silhouettes, color harmony and palette adherence, visual hierarchy (where the eye goes in 1 s), environmental storytelling, UI consistency (typography, spacing, motion), animation pose quality (from filmstrips), VFX readability vs. noise, and polish defects (z-fighting, seams, floating objects, stretched textures).

The output is per-shot findings with severity, *region boxes* (so fixes are targeted), and suggested direction. Findings are evidence-linked by shot id and region.

### N.3 Visual regression workflow
- Each accepted changeset that touches visuals (UI, lighting, assets, maps) updates the baseline for affected shots after user acceptance, or automatically if all diffs are under threshold.
- Baselines are kept per checkpoint, so you can compare version 41 against version 42 by changeset or by published place version.
- **Before/after compositions:** a side-by-side tile with a diff heat overlay. It is shown to the user and, only if flagged, to Claude.

### N.4 Cost control
- Images are downscaled to ≤ 1024 px on the long edge.
- Filmstrips are tiled into one image of at most 4×4 frames.
- A per-task image budget is set (default 8 images in active mode).
- Repeated critiques of an unchanged shot are served from cache (keyed by image hash plus rubric version).

## O. Asset Intelligence

### O.1 Asset index (part of the Brain)
Every content reference is extracted from the DataModel and from code:
- `MeshPart.MeshId` and `TextureID`, and `SurfaceAppearance`
- `Decal` and `Texture`
- `Sound.SoundId` and `AudioPlayer.Asset`
- `Animation.AnimationId`
- `ParticleEmitter.Texture`
- `ImageLabel.Image`
- `MaterialVariant`
- packages
- string asset ids in code

Each asset record holds:
- **Kind and usage sites:** which systems and instances use it.
- **Ownership and permission status:** whether the asset is owned by the user or group, public, or inaccessible. Inaccessible audio and animations are a classic Roblox failure; status is detected via the runtime `ContentProvider:PreloadAsync` callback statuses and load errors.
- **Budget metrics:** triangles (`SceneAnalysisService:GetTriangleCompositionAsync`), texture memory where available, and audio memory.
- **Provenance:** generated (by which tool), inserted from the Toolbox (by whom, when), uploaded, or created.

### O.2 Feedback-coverage and gap detection
Each gameplay feature or action has an **expected feedback manifest**. It is derived from the game-feel model, and the feel spec can override it:

```yaml
feature: Combat.SwordHeavy
expects: {animation: [windup, swing, recover], sfx: [swing, impact, impact_variation≥3], vfx: [trail, impact],
          camera: [impulse], ui: [hit_marker], haptic: optional}
```

**Detection is empirical.** During scenario runs, the runtime lib records which Sounds played, which emitters emitted, which animations played, and the camera and UI changes within the action window. The result is the coverage matrix (file 07 §7.10).

```
Combat system:  ✓ logic  ✓ networking  ✓ animation (windup, swing)
Missing:        ✗ impact VFX   ✗ impact SFX (only 1 variation needed 3)   ✗ hit marker   ✗ camera impulse
Conclusion:     Technically functional, weak feel. Priority: impact SFX (high player impact, low cost),
                impact VFX, camera impulse; recover animation later.
```

**Prioritization** uses frequency of the action per session (from bots or live data) × feel-gate weight ÷ production cost. Asset gaps are ranked by player impact.

### O.3 Asset sourcing
For each gap, the options are:
1. An existing project asset (search the index for similar kinds and names).
2. Built-in generation: `generate_mesh`, `generate_material`, or `generate_procedural_model`.
3. Creator Store via `search_asset`, which always goes through quarantine.
4. A placeholder plus a task for a human artist. RBXOS writes an **asset brief**: purpose, style references from the constitution, technical constraints such as a triangle budget, and timing.

### O.4 Supply-chain scanning (insert quarantine)
Each inserted model lands in `ServerStorage.RBXOS_Quarantine`. The scanner then checks:
- All scripts. **Red flags:** `require(<number>)` (remote module loading), `getfenv`, `setfenv`, `loadstring`, string-obfuscated code (high-entropy strings, `string.char` chains, `\x` escapes), `HttpService` or `MarketplaceService` usage, `TeleportService`, `InsertService`, hidden instances (zero-size, transparent, deeply nested), `RunContext` mismatches, and scripts disguised with service names.
- Non-script risk: excessive part counts, unanchored physics bombs, and offensive decals (flagged for human review, not auto-judged).

**Verdicts:**
- **clean:** moved to the target.
- **suspicious:** user review with a findings list, and default strip-scripts.
- **malicious:** deleted from quarantine, recorded in a known issue, and asset id added to a project blocklist.

### O.5 Asset hygiene in the guardian
Detected problems:
- Duplicated meshes or textures that differ only by id.
- Unused assets in ServerStorage.
- Oversized textures for their screen size.
- Unanchored decorative parts.
- `CanCollide`/`CanQuery`/`CanTouch` flags left on decoration (a performance cost).
- Missing `CollisionFidelity` optimization.
- Audio without `SoundGroup` assignment (mix control).
