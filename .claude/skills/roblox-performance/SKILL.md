---
name: roblox-performance
description: "Use for Roblox lag, FPS drops, memory growth, slow servers or any optimization. Measure-first, covering CPU, GPU and rendering, memory and leaks, physics, network, streaming, particles, mobile budgets, MicroProfiler and profiling tools, and regression detection."
---

# Roblox performance

**Measure → locate → hypothesize → change one thing → re-measure.** An unmeasured "optimization" is E1 at best. Report before and after numbers from the same scenario.

## Locate the bottleneck first
| Symptom | Likely domain | Look at |
|---|---|---|
| Low client FPS, everything slow | render or client CPU | MicroProfiler (Ctrl+F6): is the frame long on the **render** side or in **scripts/physics**? Check Developer Console → Memory/Stats. |
| Hitches every N seconds | GC, a periodic script, or streaming | MicroProfiler spikes. Look for periodic loops and bulk `Instance.new`/`Clone`. |
| Server lag (rubber-banding, delayed actions) | server CPU, physics, or network | Developer Console server stats (heartbeat), Script Profiler on the server, number of unanchored assemblies, remote traffic. |
| Memory climbs over a session | leaks | per-player tables not cleared, undisconnected connections, instances not destroyed, growing caches. Compare memory categories over time. |
| Mobile-only problems | GPU and memory budget | test on a real low-end device or the Device Emulator with a memory cap. Watch texture memory, particles and transparency. |

When Studio is connected, check the Studio MCP `skill` tool for Roblox's own profiling guides (names vary, so list them first).

## Common big wins (verify each by measurement)
- **Scripts:** event-driven over polling. Don't run `while true do task.wait()` loops per object; use one manager loop or `Heartbeat` over a list. Throttle non-critical updates (AI perception at 5–10 Hz, not 60). Don't do `GetDescendants` or `FindFirstChild` scans in hot paths. Batch remote traffic.
- **Physics:** anchor everything that doesn't need to move. Reduce unanchored assembly count, simplify collision (`CollisionFidelity`, `CanCollide=false` and `CanQuery=false`/`CanTouch=false` on decor). Avoid large `Touched` surfaces, and put sleeping-friendly constraints on piles of debris.
- **Rendering:** fewer unique meshes and materials (instancing works for identical mesh plus material), mesh LOD via `RenderFidelity`, limited overlapping transparency, `CastShadow=false` on small or decor parts, fewer shadow-casting lights, and lower particle `Rate`/`Lifetime` and size (overdraw is the mobile killer). UI: avoid hundreds of live frames, and pool list items.
- **Memory:** enable streaming for large worlds and tune `StreamingTargetRadius`, set `ModelStreamingMode` per model, keep texture sizes appropriate to on-screen size, and unload unused maps (parent to ServerStorage or destroy).
- **Network:** replicate state, not per-frame events. Use unreliable channels for cosmetic high-frequency data. Avoid replicating large instance trees repeatedly (clone on the client from ReplicatedStorage templates for cosmetic spam).
- **Animation:** limit simultaneously animating rigs far away (disable distant NPC animation or use LOD), and avoid stacking dozens of tracks.

## Budgets (E2 starting points; project data overrides)
Define per-device targets before optimizing: e.g. 60 FPS on mid-range phone for the core loop, 30 FPS floor on low-end, server heartbeat ≥ 55 at full server. Track instance count, part count, unanchored assemblies, active particles, draw-heavy effects and memory per category for key scenes. Set budgets **per system** ("combat VFX ≤ N active emitters"), so new features have to fit.

## Regression detection
Keep a fixed **benchmark scenario** (same place, spawn, camera path and player count). Record MicroProfiler and Stats numbers per release. After publishing, compare live per-version client FPS, memory and crash rate (Creator Hub analytics, or Open Cloud if available). A feature isn't done if it regresses the budget without a recorded decision.

## Don't
- Don't micro-optimize Luau syntax before finding the bottleneck.
- Don't sacrifice the intended visuals or feel by default. Find the cheaper technique that preserves them (impostors, LOD, client-only effects, baking). See `roblox-boundary-breaker`.
