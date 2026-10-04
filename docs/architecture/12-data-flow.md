# 12: Data Flow (U): "Make the combat feel more impactful."

The trace below follows one request end to end. Token figures are illustrative targets, not measurements.

```
USER: /roblox Make the combat feel more impactful.
```

### Stage 0: Prompt intake (hook, about 100 ms, 0 tokens of reasoning)
1. `UserPromptSubmit` → `rbxos hook prompt`. The daemon stores the prompt and classifies it as `intent=polish (high)`, `systems=[Combat]` (glossary match "combat"), `scope=system`, `concepts=[game-feel, hitstop, camera-impulse, impact-vfx]`. It sets the session mode to active.
2. The router builds a pack (budget 3k). **CRITICAL** items:
   - Combat system summary
   - D-027 (hit model: client-proposed, server-validated)
   - constitution §fantasy ("fragile time-thief, every hit is risky") and §art (muted palette, warm accents)
   - feel spec for `Sword.*`
   - the last feel report (14 days old, flagged STALE because the Combat hashes changed)

   **IMPORTANT** handles: `k.design.feel.hitstop`, `k.engine.animation-markers`, the asset coverage matrix, X-041 (hit-window experiment).
3. The entry skill's `` !`rbxos context --from-last-prompt` `` inserts the pack. Claude reads about 2.6k tokens of context instead of exploring files.

### Stage 1: Context retrieval and analysis (Claude, small)
4. Claude notes that the feel report is stale and asks for fresh evidence rather than guessing: `rbxos.test_run {level: scenario, targets: ["combat.*"], instrument: ["feel","assets"], repeat: 10}` → job.
5. The engine runs 3 combat scenarios × 10 with input-level bots on 1 client and network `wifi-good`. This costs 0 tokens. The result summary:
   ```
   Sword.Light  input→anim 31ms · hit→feedback p50 205ms (server confirm) · channels: sfx✓ vfx✗ hitstop✗ cam✗
   Sword.Heavy  input→anim 36ms · hit→feedback p50 214ms · channels: sfx✓(1 var) vfx✗ hitstop✗ cam✗ ui✗
   Enemy reaction: flinch anim ✓ (plays after server confirm)
   ```
6. A filmstrip of the heavy hit (16 frames tiled) is captured. **No image is sent yet.** Deterministic checks first.

### Stage 2: Reality check and planning (Claude, medium)
7. Claude runs the Reality Check from the skill. The desired experience: *"each hit lands with a crunch; heavy hits feel weighty but still risky"*. The constraint is D-027: damage is server-authoritative. Feedback, however, can be **client-predicted**, which is consistent with D-027 and needs no reopen. Uncertain claim: hitstop through local animation speed changes might desync the visuals of other clients. Plan: spike it.
8. Scope options are not needed (system scope, moderate). The plan:
   - (a) client-predicted impact feedback: VFX, SFX with 3 variations, camera impulse, and hit marker on the local hit proposal, with reconciliation on server rejection (fade-out)
   - (b) hitstop of 60 ms light and 110 ms heavy, local only, via `AnimationTrack:AdjustSpeed`, and enemy flinch predicted locally
   - (c) everything behind config `combat.feel.v2` so it can be A/B tested

   The anti-slop check passes: the feel package serves the fantasy ("risky, weighty").
9. `rbxos.knowledge_probe` checks the spike in the sandbox: does `AdjustSpeed(0)` on the attacker's local AnimationTrack affect replication to other clients? The 2-client sandbox test shows other clients see an unaltered animation, and it replicates through Animator. The claim is recorded as `observed` (K6).

### Stage 3: Implementation (Claude plus tools)
10. `changeset_begin {title: "Combat feel v2", systems: [Combat], risk: medium}`. The `PreToolUse` hook auto-checkpoints: git shadow commit plus a DataModel snapshot of 3 dirty roots.
11. Edits:
    - Files (Rojo-owned): `CombatController.luau`, new `ImpactFeedback.luau`, `Config` keys.
    - Asset gaps: `search_asset` for impact SFX → three candidates, inserted to **quarantine**, scanned clean, then moved. VFX built from existing project emitters, with tuned emitter parameters.
    - luau-lsp diagnostics arrive automatically after each edit: one type error, fixed immediately.
    - The `PostToolUse` fast rules flag nothing.

### Stage 4: Testing (engine, 0 tokens; Claude reads failures only)
12. `test_run {level: [unit, scenario], targets: ["combat.*"], repeat: 10}`:
    - all pass
    - feel metrics: hit→first feedback p50 is **38 ms**, which is in band
    - all channels present except haptic (optional)
13. `mp_session {clients: 4, network: "mobile-4g", timeline: [late join at 20 s], fuzz: {remotes: ["Combat.*"], intensity: standard}, invariants: ["combat.no-damage-after-round", "combat.max-damage"]}`:
    - one failure: under 4G latency, a server-rejected hit still shows full impact VFX for about 180 ms, then fades. This is a design question, not a bug. Claude adjusts the prediction to show a *lighter* provisional impact and to escalate on server confirm. Re-run passes.
    - The fuzzer finds nothing new. Invariants hold.

### Stage 5: Visual inspection (cheap first)
14. `visual_compare {shots: ["combat.heavy-hit", "hud.combat"], devices: [desktop-1080p, phone-landscape]}`:
    - The UI geometry audit flags the new hit marker overlapping the stamina bar on phone landscape (deterministic).
    - An SSIM diff on the combat shots is expected (new VFX).
    - Only the flagged phone HUD shot and the heavy-hit filmstrip are sent to Claude and to `art-director` (a 2-image budget).
15. The art director notes that the impact VFX color (cyan) breaks the constitution palette (warm accents) and the trail is too long, which reduces readability. Claude fixes the color, the trail length, and the hit marker anchor. Re-capture passes.

### Stage 6: Player evaluation
16. A bot A/B test (E3) via `experiment_create` (variants `combat.feel.v2 = false/true`, population = constitution mix):
    - mastery and competitive archetypes: combat engagement proxies up (time in combat +12% [+6, +18], voluntary re-engage after a hit +15%)
    - casual archetype: unchanged
    - no increase in quit-before-5-min

    Reported explicitly as **simulation evidence (E3)**: "Feel cannot be measured by bots. The proxies only suggest players engage more."
17. A critic pass, scoped to feel, finds one minor issue: the heavy swing's windup lacks an audio tell for enemies (fairness in PvP). This is logged as a suggestion and not blocking in the vertical-slice phase.

### Stage 7: Refinement and decision
18. Claude adds the windup tell SFX (cheap) and re-runs the scenario subset: pass.
19. The diminishing-returns check: the GAME FEEL gate passes, the critic shows only nits, and the last iteration's delta is small. Further gains need real players. Recommendation: ship behind the flag to staging, then a live experiment with goal D1 and guardrail session length.

### Stage 8: Final result and memory
20. `changeset_commit` → semantic diff report. `task_report` returns:
    ```
    Combat feel v2 — committed C-219 (flag combat.feel.v2, default ON in Studio, OFF live)
    Gates: FUNCTIONALITY ✓ GAME FEEL ✓(E2) MULTIPLAYER ✓(E2) SECURITY ✓(E2) UX ✓ VISUAL ✓ PERF ✓ (+0.04 ms client)
    Evidence: 30 scenario runs, 4-client MP under 4G, bot A/B (E3), art-director review
    Decisions: none changed (D-027 respected)   Knowledge: +1 observed claim (AdjustSpeed local-only)
    Open: windup tell — suggestion addressed; live experiment proposed (needs LIVE_CONFIG)
    Tokens: 41k total (context 6k, tool results 9k, images 2 ×, specialists 1 × art-director)
    ```
21. Memory updates:
    - experiment X-192 (E3) recorded
    - feel report refreshed
    - asset index updated (3 SFX with provenance)
    - journal written
    - visual baselines updated after the user accepts
