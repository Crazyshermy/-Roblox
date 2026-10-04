---
name: roblox-game-feel
description: "Game feel and juice: input response, anticipation, impact, hitstop, hit reactions, camera shake and FOV, recoil, sound layering, VFX, haptics, recovery timing, and hiding latency so server-authoritative actions feel instant. Use when actions feel weak, floaty or laggy."
---

# Game feel

"It works" is not "it feels good". Feel comes from **timing and the layering of feedback channels**, and both can be specified and checked.

## Model every action
`INPUT → ANTICIPATION → ACTION → IMPACT → FEEDBACK → RECOVERY`
| Phase | Question | Roblox tools |
|---|---|---|
| Input | Does something happen **on the same frame** locally, on **every device**? | client-side response first (animation, sound, camera). Bind through `ContextActionService`/IAS or a `ProximityPrompt` (with hold duration for anticipation), so touch and gamepad work too. A keyboard-only key is a mobile bug. Never wait on the server to start presentation. |
| Anticipation | Is the action telegraphed (for the player's own readability, and opponents' counterplay)? | wind-up animation (`AnimationTrack` + `GetMarkerReachedSignal`), sound swell, slight camera pull |
| Action | Is the active moment clear and fast? | fast animation segment, trails (`Trail`, `Beam`), whoosh sound |
| Impact | Does the hit *land*? | **hitstop** (freeze anims ~40–100 ms with `AdjustSpeed(0)`. On *another* player's character this is a local-only visual (E2), so the attacker's client applies it to its own view), impact VFX at contact point (`ParticleEmitter:Emit(n)`), impact sound layered (transient + body + tail), target reaction anim/knockback |
| Feedback | Does the player understand the result? | damage numbers, hit marker, health bar flash, camera shake scaled to magnitude, controller rumble (`HapticService`), UI punch (scale tween) |
| Recovery | Is there a cost and rhythm? | recovery frames, return-to-idle blend, cooldown readability |

Prefer engine effect primitives (`ParticleEmitter:Emit`, `Beam`, `Trail`, `TweenService`) over per-object per-frame script loops: one `Heartbeat` connection per particle doesn't scale.

Timing values are **conventions (E3), not laws**: tune by feel and playtest, and record chosen values in config.

## Latency hiding (server authority without mush)
- **Predict presentation, confirm consequences.** On input, the client immediately plays the swing (animation, whoosh, camera). When the *client's own* hit check (same rules as the server: range, arc, timing marker) sees a hit, it plays the **impact layer locally right away**: hitstop, impact sound, sparks and the target's flinch. Only **consequences** wait for the server: damage numbers, health change, kill feed, loot. If the server rejects, soften it (no damage number, quick fade) and don't pop anything back.
- **Don't double-play animations.** An animation the client plays on its *own* character's Animator replicates to other clients automatically. Don't have the server tell other clients to play it as well. Broadcast only effects that don't replicate (custom VFX and sounds), and skip the attacker, who already played them.
- Put unavoidable network delay into the **anticipation** (wind-up, fuse), never between the hit and the impact feedback.
- With Server Authority mode: effects read simulated state in `RenderStepped` and must undo mispredictions (see `roblox-networking`).

## Channel coverage check
For each key action, list which channels fire: animation · sound · VFX · camera · UI · haptic · target reaction · world reaction (debris, decals, physics). Strong actions use 4+ channels; missing **impact sound** and **hitstop** are the most common causes of "weak".

## Camera
- Shake: short, decaying, directional (from impact direction), magnitude-scaled; respect a reduced-motion setting. FOV kick for speed/dash (+5–10°, ease back). Avoid shaking UI.
- Custom camera work (over-shoulder, lock-on, spring arm) is often the single biggest jump away from "default Roblox". See `roblox-physics-animation` for rigs.

## Sound
For the mixing graph and wired Audio API, see the audio notes in `roblox-assets`. Layer and vary: randomize pitch (±5–10%) and alternate samples to avoid machine-gun repetition; use `SoundGroup`s for mixing and ducking; positional audio for world events. Silence before a big moment amplifies it.

## Movement feel
Acceleration/deceleration curves, coyote time, jump buffering, landing recovery, turn responsiveness. The default controller is tuned for generality; custom tuning (or a custom controller) is how platformers, action games and racers get identity.

## Verify
Describe the intended timeline per action (ms per phase, channels). If Studio is connected, playtest and capture frames around the action; check the first-feedback latency on the client (should be same-frame for local presentation). Ask the user to playtest feel: it is the one dimension where human perception is the real test.
