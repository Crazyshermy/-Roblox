# 07: Game Intelligence: Design, Fun, Critique, Feel, Player Intelligence (I), Fun Laboratory (J)

The design-intelligence subsystems have two halves:
- **Reasoning protocols** live in skills and agents and cost tokens only when used.
- **Evidence machinery** lives in the daemon and the engine and costs no tokens.

Every protocol must end in something checkable: a scenario, a metric, an experiment, or a user decision.

## 7.1 Reality Check (before any system-scope or larger build)

Triggered by intent `build|concept|improve` with scope ≥ `system`, or explicitly. The output is a compact template stored in the task journal:

```
1 Desired player experience  — one sentence in player language + the moment it peaks
2 Game design                — loop(s) affected; what the player decides; feedback
3 Technical implementation   — systems touched/new; authority model; data
4 Roblox constraints         — cited knowledge claims (ids) + uncertain ones to probe
5 Performance                — budget impact estimate per device class
6 Networking                 — remotes, rates, replication, latency tolerance
7 Security                   — what a malicious client could attempt; invariants
8 Failure modes              — gameplay + technical (join mid-event, leave, respawn, streaming)
9 Testing                    — which evidence will prove it works and *feels* right
10 Build plan                — spike-first ordering; checkpoints; scope option chosen
```

Rules:
- If step 4 contains any `uncertain` claim on the critical path, a **spike** (probe or prototype in the sandbox) is scheduled before implementation.
- If the chosen implementation reduces step 1, that is a scope reduction, which must be explicit (§7.4).

## 7.2 Boundary Breaker (when something seems hard or impossible)

**Procedure:**
1. **Experience:** what must the player perceive or feel? Separate the *perception* from the *mechanism*.
2. **Limitation:** name it precisely and classify it as engine, API, performance, networking, asset, or cost-of-development. Cite knowledge claims. An unsupported "Roblox can't" is rejected.
3. **Search the technique space**, using the catalog in the knowledge pack `k.boundary.*`:

| Family | Examples |
|---|---|
| Client-side illusion | Local-only parts and effects per player (different realities per player in horror), camera manipulation, `ViewportFrame` portals and mirrors, fake reflections, screen-space UI over 3D, per-client lighting changes |
| Simulation split | Server-authoritative coarse simulation plus client fine simulation. Deterministic lockstep for small state. Interpolation buffers. |
| Precomputation | Baked navigation, baked lighting via vertex color and decals, precomputed time-rewind snapshots using `buffer` ring buffers |
| Procedural | `EditableMesh`/`EditableImage` runtime geometry and textures, procedural animation (IK controls), procedural audio layering |
| Custom systems | Custom character controller (replace the Humanoid controller with a constraint-based or custom CFrame controller), custom physics for specific objects, a custom camera system |
| Parallelism | Parallel Luau (Actors) for AI, pathing, and procedural generation |
| Perception tricks | Audio carrying the illusion (spatial audio, occlusion via the Audio API), post-processing, frame pacing, hitstop |
| Streaming and LOD | Streaming controls, model LOD swapping, impostors |
| Hybrid | Combinations of the above, e.g. "time manipulation" = server keeps authoritative state snapshots in buffers, plus clients play rewind VFX locally, plus per-player time bubbles rendered as local illusions |

4. **Evaluate options** by *experience preservation* (which perceptual pillars survive), cost, risk, performance, and security.
5. **Pick and spike:** prototype the riskiest assumption in the sandbox first, and record the result as an experiment or knowledge claim.

**Output:** a "boundary report" with 2–4 options and a recommendation. Rejected options are kept in the decision's `rejected` list.

## 7.3 "Feels like it shouldn't be Roblox" barrier catalog
A curated checklist. The critic and the polish mode run it against the project.

| Barrier (what screams "default Roblox") | Counter-techniques |
|---|---|
| Default character controller feel (floaty jump, instant turn) | Custom movement tuning or controller, acceleration curves, coyote time, landing recovery animations |
| Default camera | Custom camera rig (spring arm, FOV kicks, look-ahead, collision smoothing), cinematic transitions |
| Default animations | Custom animation set, procedural layers (lean, head look), animation blending |
| Flat lighting and default skybox | `Future` lighting, Atmosphere, color grading, light probes faked via local lights, art-directed time of day |
| Default sounds and no mix | Sound design pass, `SoundGroup` mixing, reverb zones, ducking, dynamic music layers |
| Default topbar and generic UI | Coherent UI system (typography, motion, sound), diegetic UI where it fits, minimal HUD |
| Primitive-part art with no material language | Material variants, a consistent palette, modular kits, decals for wear, silhouette design |
| Lobby → teleport → generic round | Seamless onboarding, narrative framing, an in-world lobby |
| Uniform scale and empty spaces | Composition, landmarking, environmental storytelling, density gradients |

## 7.4 Scope intelligence
When the estimated build cost exceeds the task threshold, or the request is "enormous", Claude must present options in this format:

```
Option A — Full fidelity      Experience pillars: ●●●●● (all)  Complexity: XL  Risk: high  Est: 6–8 wk
Option B — Core illusion      Experience pillars: ●●●●○ (loses: X)  Complexity: M  Risk: med  Est: 2 wk
Option C — Minimal            Experience pillars: ●●○○○ (loses: X, Y, Z)  Complexity: S  Risk: low  Est: 3 d
Recommendation: B, because constitution §priorities = "vertical slice by Nov"; upgrade path B→A: …
```

- Pillars come from the constitution and the desired-experience sentence. This is ordinal, and each lost pillar is named, never hidden in a number.
- **No silent simplification.** If Claude implements less than the chosen option, it records `scope_reduced` in the journal. The `Stop` hook verifies the reduction was reported to the user.

## 7.5 Creative risk evaluation
Each dimension is rated on an ordinal 1–5 scale with anchor descriptions:
- Novelty
- Technical risk
- Confusion risk
- Production risk
- Payoff

A one-line justification is required per rating. When comparing alternatives, use **pairwise preference with reasons** rather than absolute numbers. The constitution can declare a risk appetite (`conservative|balanced|bold`). The recommendation must respect it or argue explicitly against it.

## 7.6 Genre intelligence
A genre pack (`knowledge/design/genres/<genre>.md`) contains:
- Core fantasies.
- Canonical loops at 30 s, 5 min, and session length.
- Player expectations: conventions to keep, and conventions that are safe to break.
- Pacing curves.
- Failure modes (for horror: over-exposed monsters, no downtime, predictable scares).
- Roblox audience notes: device mix, session patterns, social play.
- Reference mechanics, each with *why it works*.
- Instrumentation suggestions.

**Genre combinations** load each pack plus an *interaction note* (`interactions/horror+social-deduction.md`) that describes synergies and conflicts. For example, horror's isolation conflicts with social deduction's need for communication. The resolution pattern is proximity voice and chat range limits that create isolation through the mechanics.

## 7.7 Fun model (hypotheses, not formulas)
- **Dimensions (vocabulary):** curiosity, tension, mastery, surprise, discovery, agency, power, fear, humor, competition, creativity, achievement, connection, expression, relaxation, chaos, belonging, challenge, novelty.
- **Moment model** (used by critics and feel analysis): motivation → action → feedback → emotion → expectation → consequence → next decision.
- **Arc model:** anticipation → action → consequence → reward → escalation → uncertainty → mastery → novelty.

**Experience hypotheses.** Every target experience is written as a falsifiable statement with observable proxies:

```yaml
- id: EH-3
  experience: "Dread builds when the lights flicker before the Warden appears"
  dimensions: [tension, fear, anticipation]
  mechanism: "flicker as reliable-but-delayed cue; 6–12 s variable gap"
  proxies:
    bots:   ["movement hesitation ↑ after cue", "path choice avoids dark corridors ↑"]   # E3
    persona:["think-aloud mentions anticipation/fear after cue"]                         # E3 (qualitative)
    live:   ["funnel: survives first Warden encounter ≥ 60%", "session length unaffected or ↑"] # E4/E5
  status: untested
```

Proxies for each dimension are listed in the knowledge pack (`k.design.fun-proxies`), with what can and cannot be measured by bots. Fear itself, for example, cannot be measured by a bot, while avoidance behavior under a reliable cue can.

## 7.8 Critic agent (`game-critic`)

**Mandate:** find why the game is bad. Default stance: skeptical.

**Protocol:**
1. Steelman the design intent from the constitution.
2. Attack it: boredom, repetition, generic mechanics, weak progression, pacing, confusing objectives, onboarding, weak feedback, fake depth, unnecessary systems, UI, jank, atmosphere, and multiplayer dynamics.
3. **Every finding must cite evidence:** a timeline, a screenshot or filmstrip id, bot metrics, code, a persona log, or analytics. Findings without evidence are labeled *speculative* and capped at low severity.
4. Severity: blocker, major, minor, or nit. It is judged against the *phase* profile, so a prototype isn't critiqued for polish.
5. Output schema: `{id, category, claim, evidence[], severity, confidence(ordinal), suggested_test, suggested_fix_direction}`.

**Anti-sycophancy:**
- The critic never sees the implementer's self-assessment.
- At milestones the critic runs in a panel workflow with independent critics, and each finding is checked by a verifier agent instructed to *disprove* it. Only surviving findings are reported.

## 7.9 Anti-slop system
- **Mechanic provenance ledger** (`.rbxos/mechanics.yaml`). Each mechanic has `serves:` links to fantasy and pillars, plus `why_here:`.
- **Generic-pattern catalog** (`k.design.slop.*`): coin currencies without a sink design, pets without a fantasy link, rebirth loops, egg gacha, generic quest boards, generic daily rewards, copycat simulator progression, pointless upgrade tiers, generic lobbies, and generic UI kits.
- **Detection:**
  - Static: names and structures in the Brain, such as a `Rebirth` module, `Coins` leaderstat, or `Egg` models.
  - Design-doc scan.
  - New mechanics proposed in plans.
- **For each detection,** the `anti-slop-auditor` asks "Why does this belong in *this* game?" and returns one of three verdicts:
  - *justified* (with reason)
  - *transform* (make it specific to the fantasy; e.g. "currency" becomes "time shards that rewind your death")
  - *remove*

  Verdicts go to the user. Common mechanics are not banned.

## 7.10 Game feel system

**Model** for each action: `INPUT → ANTICIPATION → ACTION → IMPACT → FEEDBACK → RECOVERY`.

**Instrumentation** in test sessions (runtime lib `Feel` module, client and server):
- Timestamps for: input received (`UserInputService`/`ContextActionService`, or the VirtualInput send time), animation start and markers (`AnimationTrack:GetMarkerReachedSignal`), the hit-confirm remote, damage applied, and feedback events (Sound played, `ParticleEmitter:Emit`, camera offset or FOV changes, UI tweens, hitstop/time-scale effects, haptics via `HapticService`).
- These produce an **action timeline** per action instance and aggregated latency distributions.

**Feedback-channel coverage matrix:**

```
Action: Sword.Heavy   visual-anticipation ✓  sfx-swing ✓  impact-vfx ✗  impact-sfx ✗  hitstop ✗
                      camera-impulse ✗  enemy-reaction ✓(flinch anim)  ui-feedback ✗  haptic ✗
Timeline p50: input→anim 34 ms · anim→hit 280 ms · hit→first feedback 210 ms (!) (server round-trip)
Finding: impact feedback waits for server confirm → feels mushy. Option: client-predicted impact
         feedback with server-confirmed damage numbers (consistent with D-027).
```

- **Feel spec** (`.rbxos/feel.yaml`) holds per-action targets: latency bands, required channels, and hitstop windows. Defaults come from `k.design.feel.*` and are labeled *convention*, since they are heuristics from game-feel practice, not laws.
- **Visual review:** a filmstrip (12–20 frames around the action, tiled into one image) goes to `feel-analyst` and optionally `art-director`.
- "The sword works" passes FUNCTIONALITY. "The sword feels good" requires the GAME FEEL gate: required channels present, latencies in band, and no critic blocker on feel.

---

## I. Player Intelligence

### I.1 Purpose and epistemics
Simulated players are **hypothesis generators and regression detectors**:
- Bots answer *behavioral* questions (can players find X, where do they stall, what breaks).
- Personas answer *comprehension* questions (do players understand X).
- Neither answers "is it fun". The maximum evidence grade is E3, and reports state it.

### I.2 Archetype model
An archetype is a parameter vector. **Every parameter has an operational definition**, meaning a concrete effect on the policy.

| Parameter | Policy effect (operational) |
|---|---|
| curiosity | Weight on unexplored affordances and areas. Novelty bonus decay rate. |
| competition | Weight on actions that improve rank or score. Attraction to PvP affordances. |
| cooperation | Weight on helping, reviving, or sharing. Distance kept to teammates. |
| exploration | Path entropy target. Willingness to leave the objective path. |
| collection | Weight on collectibles and completion counters |
| mastery | Retry propensity after failure. Preference for harder variants. |
| creativity | Weight on build and customization affordances |
| social / status | Weight on visible-to-others actions. Following friends. Emotes and chat. |
| fear_tolerance | Threshold for avoidance under threat cues |
| grind_tolerance | Repetitions of a non-novel loop before boredom saturates |
| complexity_tolerance | Max simultaneous unknown affordances before confusion rises |
| attention / patience | Time without perceived progress before frustration rises, and how fast |
| quit_threshold | Engagement level below which the session ends (stochastic) |
| friend_dependence | Probability of quitting when friends leave. Join-with-party behavior. |
| risk_tolerance | Choice between safe and risky options with different payoffs |
| roblox_experience | Knowledge of genre conventions. Reads UI and prompts faster. |
| skill | Aim, timing, and navigation noise (actuation error model) |

**Archetypes** are named presets with distributions, not single points: casual, competitive, explorer, social, collector, completionist, creative, mastery-focused, horror enthusiast, genre expert, Roblox veteran, Roblox newcomer, impatient, patient, solo, friend-dependent, and exploiter (used by security).

### I.3 Population
- The **mixture** of archetypes comes from the constitution's audience section (prior). Sampling draws individuals from each archetype's distributions.
- Friend groups are simulated with Studio's Party Simulator (`PartyId`) and bot social links.
- Reports always break results down *per archetype* and *for the mixture*.

### I.4 Bot architecture (in-engine, Luau, zero tokens)

```
Perception ─► Beliefs/Memory ─► Affect state ─► Utility selection ─► Actuation ─► Log
 (non-omniscient)  (known affordances,   (curiosity, boredom,   (options scored      (intent: Humanoid/
  camera frustum+LOS, visited cells,      frustration, confusion,  by params×affect×   Pathfinding;
  visible UI text,   believed objective,  fear, satisfaction;      perceived value−    input: VirtualInput
  prompts, sounds    failed attempts)     event-driven updates)    effort; softmax)    per client)
  heard, chat)
```

- **Non-omniscience is essential.** Bots only know what a player could perceive: UI text on screen, objective markers in view, ProximityPrompts within range, sounds within audible distance, and prior memory. That is what lets confusion and lostness emerge.
- **Affect dynamics** are simple, documented update rules with parameters, e.g. `boredom += k_b · (1 − novelty(event))` per minute. They are tunable and calibratable. They are not presented as psychology.
- **Option set:** pursue believed objective, explore, interact with affordance, follow friend, socialize, grind, idle, retry, change strategy, quit.
- **Fidelity levels:**
  - `intent` drives the Humanoid, Pathfinding, and tool activation directly. It is cheap and scales to many bots via phantoms on the server.
  - `input` uses VirtualInput on real clients (≤ 8). It tests the actual controls and UI.
- **Logs:** a per-bot timeline of positions, decisions with scores, affect, events, and the quit reason.

### I.5 Affordance discovery
- **Automatic:** ProximityPrompts, ClickDetectors, Tools, GuiButtons (visible, active), Seats, tagged collectibles (heuristic names), dialog NPCs, doors (hinge constraints), and pickups (Touched parts with tags).
- **Declarative:** `.rbxos/affordances.yaml` maps instance paths or tags to semantic types (`objective`, `reward`, `hazard`, `secret`, `shop`) without modifying the game.
- **Discovered-unintended detection:** bots reaching regions outside the declared nav, or out-of-bounds positions, and state transitions never seen in scenario specs. These are clustered and reported.

### I.6 Calibration (making archetypes honest)
- Before live data, every parameter is labeled `prior (uncalibrated)`, and reports say so.
- With live data (Open Cloud Analytics: funnel step completion, `TotalSessionsEndedInBucket`, retention, segment dimensions):
  1. Run approximate Bayesian computation over the archetype mixture weights and key parameters (patience, quit threshold, grind tolerance) to match the observed funnel and session-length distributions.
  2. Report calibration error.
  3. Re-calibrate per release.
- Calibrated populations improve *prediction*, not *truth*. Predictions are scored against the next release's real data, and this predictive accuracy is tracked as a first-class metric. If accuracy is poor, simulation results are down-weighted.

### I.7 LLM persona playtesters (budgeted, qualitative)
- **Agent:** `persona-playtester`, a vision-capable model, with persona text derived from an archetype.
- **Loop:** every 3–6 s of game time it receives a downscaled screenshot plus perceptible state (visible UI text, prompts, last sounds, chat). It chooses an action through the built-in input tools or `character_navigation`, and writes a one-line think-aloud.
- **Used for:** the first 3–5 minutes of onboarding, UI comprehension, and "is the objective clear?" questions. Default budget is ≤ 3 personas × 5 min per run, with a cost preview.
- **Output:** a think-aloud log, confusion events with timestamps, and screenshot handles. Evidence grade E3, qualitative.

### I.8 Player Psychology Engine (differential diagnosis)
**Symptom:** "players quit around 90 s" (from live funnels or bots).

1. **Hypotheses** (generated by Claude from the moment model): A unclear objective, B weak opening, C insufficient agency, D reward delay, E excessive complexity, F lack of novelty, G poor onboarding.
2. **Discriminating predictions** are generated *per hypothesis*:
   - A predicts that bots with *oracle objective knowledge* survive far longer while normal bots wander, and that persona logs show "what do I do?".
   - D predicts that a reward-pulled-earlier variant shifts quit time, but oracle knowledge doesn't.
   - E predicts that confusion spikes correlate with the number of simultaneous affordances.
3. **Tests** are chosen from cheapest to most expensive:
   - bot ablations (oracle objective, infinite patience, reduced UI)
   - heatmaps and dead-end analysis
   - persona runs
   - a live experiment
4. **Ranking:** hypotheses are ordered by how many discriminating predictions survived. Hypotheses with untested predictions remain open, and the report says which test would discriminate further.

### I.9 Outputs
- Session timelines and heatmaps (position density, deaths, stalls).
- Time-to-first-X metrics.
- Objective discovery time distributions.
- Dead ends and softlocks.
- Quit reasons by archetype.
- Affordance usage.
- Unintended discoveries.
- Variant comparisons.

---

## J. Fun Laboratory

### J.1 Loop
```
BUILD → PLAY → MEASURE → IDENTIFY PROBLEM → HYPOTHESIZE (pre-register) → MODIFY (config variant)
  → TEST (right evidence tier) → COMPARE → KEEP / REVERT / ITERATE → UPDATE KNOWLEDGE (scoped)
```

### J.2 Pre-registration (required)
`experiment_create` refuses to run without a hypothesis, a mechanism, predictions with direction and observable, falsification criteria, a population, and an evidence tier. This stops post-hoc story-telling, which is the main way an AI lab deceives itself.

### J.3 Variants as configs
- Tunable and switchable behavior is exposed through `ConfigService` keys, which RBXOS helps refactor toward (`Config.get("combat.hitWindowMs")` with defaults).
- Simulation runs set config overrides inside test DataModels.
- **The same variant definition** becomes a live Open Cloud experiment (`inGameConfigExperimentConfiguration`, one baseline, goal metric). No code divergence between simulation and live.
- Feature flags double as **kill switches** for live operations.

### J.4 Question router (which evidence tier answers what)

| Question type | Tier |
|---|---|
| Reachability, softlocks, exploits, pacing timelines, economy flow, load | bots (E3) |
| Comprehension, onboarding clarity, UI legibility | personas (E3, qualitative) plus UI audits |
| Preference, retention, monetization, "fun" | **live only** (E4 observational, E5 experiment) |
| Engine behavior | probes (knowledge) |

### J.5 Analysis

**Simulation:**
- Report the per-archetype effect direction and magnitude, with bootstrap intervals *across seeds and runs*, as a measure of simulation noise, not population truth.
- Include robustness: the effect's stability under ±25% perturbation of population mix and key parameters (sensitivity analysis).
- Phrase conclusions as "the hypothesis survived or failed in simulation (E3)".

**Live:**
- Use the Experiments API stats for the goal metric plus guardrails (session length, crash rate, revenue if applicable).
- Plan sample size and minimum duration before launch, from the baseline variance pulled from analytics.
- Warn about novelty effects for UI and feel changes, and recommend running past them.
- Report effect and interval from the API. Make no claims beyond significance.

### J.6 Decision and memory
- **Keep / revert / iterate** rules are declared at pre-registration, e.g. "keep if explorer D1 proxy improves without social regression".
- An experiment record is written to `.rbxos/experiments/`, and conclusions update:
  - (a) project knowledge (K6)
  - (b) decisions, if they were the basis
  - (c) **cross-project** design knowledge only after replication: ≥ 2 projects, or 1 live E5 result. Even then the conclusion is labeled with the context it held in.

### J.7 Example (the brief's #184, in RBXOS form)

```yaml
id: X-184
hypothesis: "Early progression is too slow, causing early quits."
mechanism: "first reward at ~4 min exceeds patience of low-patience archetypes"
predictions:
  - {observable: "quit before 5 min", direction: down, archetypes: [casual, impatient, newcomer]}
  - {observable: "explorer session length", direction: none}
falsified_if: "quit-before-5min does not decrease for casual/impatient by ≥ 15% relative across ≥ 20 seeds"
variants: [{name: base, baseline: true, config: {prog.firstRewardSec: 240}}, {name: fast, config: {prog.firstRewardSec: 90}}]
evidence_tier: bots
result (E3):
  casual: quit<5m −31% [−38,−22]   impatient: −40% [−47,−30]   explorer: session +4% [−3,+11]
  social: friend-follow time −12% [−20,−5] (unexpected: faster solo reward reduces grouping)
  sensitivity: effect sign stable under ±25% mix perturbation; social effect unstable
conclusion: "Survived for casual/impatient in simulation; social side effect is a new hypothesis (X-185).
             Not universally beneficial. Recommend live experiment with D1 goal + party-size guardrail."
```
