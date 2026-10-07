---
name: roblox-physics-animation
description: "Roblox physics, characters, NPC AI and animation tech: assemblies, constraints and movers, network ownership, vehicles, ragdolls, custom character controllers, cameras, enemies and pathfinding, Animator and AnimationTrack priorities and markers, IK, procedural animation."
---

# Physics, characters and animation

## Physics fundamentals
- An **assembly** is rigidly connected parts that simulate as one. Anchored parts don't simulate. Anchor everything static, and weld decorative children to the moving root.
- Use **constraint-based movers** (`AlignPosition`, `AlignOrientation`, `LinearVelocity`, `AngularVelocity`, `VectorForce`, `Torque`) for controllable motion. Legacy BodyMovers (`BodyVelocity`, `BodyGyro` etc.) are deprecated for new work (E4).
- Setting `CFrame` on unanchored parts every frame fights the solver. Either anchor and drive `CFrame` (kinematic, cheap, no physics response) or use movers (physical). Pick one per object.
- **Network ownership** decides who simulates. A client simulating a part means smooth local response and an exploitable result. The server simulating means authoritative but latent for the interacting player. Choose per object, document it, or use **Server Authority mode** for predicted server-owned physics (see `roblox-networking`).
- Collision groups (`PhysicsService:RegisterCollisionGroup`, `BasePart.CollisionGroup`) for filtering. Use `CanQuery`/`CanTouch` false on decor for performance.
- Spatial queries: `workspace:Raycast`, `Shapecast`/`Blockcast`/`Spherecast`, `GetPartBoundsInBox`/`GetPartsInPart` with `RaycastParams`/`OverlapParams`. Prefer these to `Touched` for hit detection.

## Characters
- Tune the Humanoid first (`WalkSpeed`, `JumpHeight`, `HipHeight`, `AutoRotate`), then the controls. For identity-defining movement (momentum, wall-run, dash, grapple), consider a **custom controller**: state machine plus movers or a custom CFrame integrator, keeping the Humanoid for animation and state only, or replacing it entirely. That's a major decision, so record it in `.apex/decisions.md`.
- Humanoid states (`HumanoidStateType`) can be disabled with `SetStateEnabled` (e.g. disable `Ragdoll`/`FallingDown` for arcade feel).
- Ragdolls: `BallSocketConstraint`s replacing `Motor6D`s on death or knock. Decide ownership (who simulates) to avoid jitter, and clean up on respawn.

## Cameras
`Camera.CameraType = Scriptable` for full control. Update in `RenderStepped` or `BindToRenderStep` with an explicit priority. Use a spring or critically damped smoothing for follow. Raycast for collision so the camera doesn't clip walls. Lock-on and over-shoulder cameras need input remapping on mobile.

## Animation
- Load and play on the **`Animator`** (inside Humanoid or AnimationController). Playing from the client on the local character replicates automatically. NPC animations should be played by the server, or by clients for cosmetic-only LOD.
- **Priority** (Core < Idle < Movement < Action < Action2–4) and **weights** decide blending. Most "animation won't play" bugs are priority or ownership issues. An animation must be owned by the experience owner (user or group) **or explicitly granted to this experience** via asset Permissions to load.
- Use `AnimationTrack:GetMarkerReachedSignal("Hit")` to sync gameplay and VFX to animation frames. Use `AdjustSpeed` for hitstop and timing.
- **IK:** `IKControl` for look-at, foot planting and hand placement. Procedural layers (lean into turns, head look, recoil offsets via `Motor6D.Transform` in a stepped loop) add life cheaply.
- Under **Server Authority**: don't cache `AnimationTrack`s across frames. Query `Animator:GetTrackByAnimationId()` instead (E4).
- Animation LOD: stop or simplify animations of distant or offscreen NPCs.

## NPCs and enemy AI
For enemies, monsters, companions or hordes, read `${CLAUDE_SKILL_DIR}/references/npc-ai.md` (server authority, tick budgets, state machines, perception, `PathfindingService` failure handling).

## Verify
Physics behavior is version- and ownership-sensitive. Playtest with Server & Clients to see what *other* players observe. Watch for jitter at ownership boundaries and with the Network Simulator's latency.
