# 08: QA (K), Security (L), Performance (M), Device Testing, Quality Gates, Knowing When to Stop

## K. QA: automated and adversarial testing

### K.1 Test pyramid

| Level | What | Runner | Cost | Runs when |
|---|---|---|---|---|
| T0 Static | `luau-analyze --strict` and luau-lsp diagnostics, selene, StyLua check, **RBXOS rules** (below), API existence and context checks | daemon (subprocess), < 1 s incremental | 0 tokens | Every edit (PostToolUse), pre-commit |
| T1 Unit | Jest-Lua or TestEZ specs for ModuleScripts. Pure modules run in **Lune** (fast, headless). Engine-dependent ones run in-engine (Run mode or Luau Execution). | daemon → Lune / Studio / Open Cloud | 0 | Changeset commit; on demand |
| T2 Integration | Server-side system tests in Run mode with phantom players (`StudioTestService:ExecuteRunModeAsync`) | Studio | 0 | Commit of system-scope changesets |
| T3 Scenario | Declarative playtest scenarios (DSL) with 1 client, using intent- or input-level actions and assertions | Studio solo or MP | 0 | Feature changes; regression suite |
| T4 Multiplayer | 2–8 clients, staggered joins, leaves, network profiles, invariants | Studio MP | 0 | Networked feature changes; nightly |
| T5 Chaos | MP plus randomized timelines (join or leave mid-event, respawn storms, latency spikes, packet loss, `RandomizeJoinInstanceOrder`) and phantom load | Studio MP | 0 | Pre-milestone; nightly |
| T6 Security | Remote fuzzing, malicious-client scripts, invariant checks, static remote validation | Studio MP | 0–low | Remote, data, or purchase changes; pre-ship |
| T7 Visual | Shot capture, SSIM, UI geometry audit, device matrix | Studio | low (images only when flagged) | UI or art changes; milestone |
| T8 Performance | Budgets per scenario and device class, regression vs. baseline | Studio + live | 0 | Commit of hot-path changes; nightly |
| T9 Player | Bot populations, personas | Studio | 0 / budgeted | Lab, milestones |

### K.2 RBXOS static rules (examples; full catalog in `knowledge/rules/`)

| Rule | Detects |
|---|---|
| SEC-001 | `OnServerEvent` handler using an argument without a type or range check before it affects state |
| SEC-002 | Client-supplied numeric values flowing into currency, damage, or position writes (taint analysis over the AST data flow) |
| SEC-003 | `RemoteFunction:InvokeClient` used by the server, which can hang the server thread |
| SEC-004 | Missing per-player rate limiting on remotes that mutate state |
| DATA-001 | DataStore calls without `pcall` or retry. `SetAsync` where `UpdateAsync` is needed. No session lock. |
| DATA-002 | No `BindToClose` flush. No schema version field. |
| MON-001 | `ProcessReceipt` that is not idempotent or doesn't return `PurchaseGranted` after persistence |
| TXT-001 | User-generated text displayed to other players without `TextService` filtering |
| PERF-001 | `while true do wait()` polling. Per-frame `FindFirstChild` chains. `Touched` on many parts without debounce. |
| PERF-002 | Unbounded `:Connect` in per-player or per-character code without cleanup |
| NET-001 | `FireAllClients` with large tables at high frequency. Reliable remote used for per-frame cosmetic state. |
| STR-001 | StreamingEnabled is on, and code indexes workspace parts without `WaitForChild` or `StreamingMode` handling |
| ARCH-00x | Guardian thresholds (size, cycles, boundary violations) |

### K.3 Scenario DSL (`.rbxos/scenarios/*.yaml`)

```yaml
id: combat.heavy-swing-hits-dummy
clients: 1
setup:
  config: {combat.hitWindowMs: 250}
  spawn: {at: "Workspace.Arena.SpawnA"}
  fixtures: [{clone: "ServerStorage.Fixtures.TrainingDummy", to: "Workspace.Arena", name: Dummy}]
steps:
  - equip: {tool: "Sword"}
  - navigate: {to: "Workspace.Arena.Dummy", within: 5}
  - input: {key: "MouseButton1", hold_ms: 600}          # input-level (VirtualInput)
  - wait_for: {event: "Feel.Impact", timeout_s: 2}
assert:
  - expr: "Workspace.Arena.Dummy.Humanoid.Health < 100"
  - feel: {action: "Sword.Heavy", channels: [impact-vfx, impact-sfx, hitstop], hit_to_feedback_ms_p50: {lte: 90}}
  - no_errors: true
repeat: 10
network: "wifi-good"
```

Scenarios compile to a runtime plan executed by the client and server runtime libraries. Failures return the step, assertion, logs for that window, and a screenshot handle.

### K.4 Multiplayer chaos testing
- **Timeline perturbations:**
  - Join during critical windows (round start, boss phase, trade confirm).
  - Leave mid-transaction.
  - Respawn storms.
  - Simultaneous conflicting actions (two players grab the same item in the same frame window).
  - Server-side `task.delay` jitter injection on project handlers (opt-in, via the runtime lib's wrapper).
  - Network profile switches mid-run.
- **Detectors:**
  - Invariant violations.
  - Duplicated instances or items.
  - Desync: the difference between server state and each client's replicated view of key attributes, sampled.
  - Orphaned connections and instances (`SceneAnalysisService:GetUnparentedInstancesAsync`, plus counts of connections created by the runtime-lib wrapper).
  - Error bursts.
  - Server frame time spikes.
- **Repro:** every failure carries `{seed, timeline, network, build checkpoint}`. `rbxos.test_run {repro: id}` re-executes it deterministically, as far as Roblox allows. Flakiness is measured by repeat count.

### K.5 Invariants (`.rbxos/invariants/*.luau`)
Invariants are written by Claude or users and evaluated on the server DataModel every N frames and at events.

```luau
return {
  id = "economy.conservation",
  check = function(world)
    -- total currency = initial + minted (by sanctioned sources) - sinks
    local total = world.sumAttribute("Players", "Coins")
    return total == world.ledger.initial + world.ledger.minted - world.ledger.spent,
      ("drift=%d"):format(total - (world.ledger.initial + world.ledger.minted - world.ledger.spent))
  end,
}
```

The `world.ledger` comes from the runtime lib's optional wrappers around the project's economy API. The RBXOS refactor guidance encourages a single economy service, which makes this possible.

## L. Security architecture

Security has two halves:
- **L.1–L.3** cover safety *of the agent* acting on the project.
- **L.4–L.7** cover security *of the game*.

### L.1 Permission tiers (capabilities, cumulative)

| Tier | Grants | Default |
|---|---|---|
| `READ_ONLY` | Read tools, search, observe, captures in Edit | always |
| `SANDBOX` | Any action in the sandbox place, and in test DataModels | always |
| `TEST` | Start and stop tests, input, bots, fuzzing in **test DataModels only**, network and device simulation | on |
| `SAFE_EDIT` | Script and instance edits in the project with auto-checkpoint. Limits per changeset: ≤ 500 instances destroyed, ≤ 40 scripts modified, no protected paths. | on |
| `STRUCTURAL_EDIT` | Above the SAFE_EDIT limits, protected paths, and sync-provider configuration | ask |
| `CONSTITUTION_EDIT` | Change vision, principles, or refusals | ask (sections configurable) |
| `DATA_MIGRATION` | DataStore schema changes, migration scripts against **dev** stores | ask |
| `LIVE_CONFIG` | Publish Open Cloud config drafts and start or stop live experiments | ask |
| `PUBLISH_STAGING` | Publish to the staging place | ask (or allow per project) |
| `PUBLISH_PRODUCTION` | Publish to production places, and production DataStore writes | **always ask, with typed confirmation in the terminal**. Never auto-approved, even in bypass mode, via hook `deny` unless a one-time confirmation token is present. |

**Enforcement points (defense in depth):**
1. Claude Code `PreToolUse` hooks.
2. The gateway.
3. The daemon (`rbxos` tools and Open Cloud).
4. The companion plugin (refuses `dm.write` beyond the granted tier, and shows an in-Studio confirmation for destructive operations).
5. Credential scoping (§L.2).

### L.2 Credentials
- **Open Cloud API keys are split by tier**, with least privilege:
  - a read key (analytics, configs read)
  - a staging key (publish to the staging place only, using the API key's resource restrictions)
  - an optional production key
- Keys are stored through plugin `userConfig` with `sensitive: true` (the OS secure store), or in the daemon's keychain entry. The production key is only *loaded* after a confirmation token is issued by the `ship` flow.
- Studio-side code (plugin, runtime lib) **never** receives Open Cloud keys.
- **Studio API access:** the doctor checks "Enable Studio Access to API Services". The test runtime installs a **DataStore guard** that routes DataStore calls in tests to a mock or dev scope unless `DATA_MIGRATION` is granted for a dev universe. Production data is never touched from Studio tests.

### L.3 Agent-specific threats

| Threat | Mitigation |
|---|---|
| Destructive Luau via `execute_luau` | AST screening → `ask`. Auto-checkpoint before any Edit-DM execution. Snapshots enable rollback. |
| Prompt injection from game content (instance names, comments, toolbox descriptions, chat logs) | Provenance labels in tool output (`untrusted:*`). The policy engine ignores in-content instructions. Privileged tools need tier grants that content cannot raise. Personas never receive tool access beyond input. |
| Malicious free models (backdoors) | Quarantine-then-scan on insert (file 09 §O.4) |
| Wrong-target edits (multiple Studios) | `studio_id` pinning by place. Universe checks. |
| Runaway loops (fix-break-fix) | Changeset-level failure detection → rollback → failed-approach memory. Budget governor. |
| Secret leakage into the repo | Pre-commit secret scan on `.rbxos/` and source. Keys never written to files. |

### L.4 Security Adversary (game)
- **Static:** the SEC and DATA rules, plus remote contract inference. The inferred argument types for each remote become the *fuzz grammar*.
- **Dynamic (malicious-client harness):** the client runtime acts as an exploiter. It can call any remote with any arguments, and it can modify its own character (CFrame teleport, WalkSpeed, network-owned parts). This is what real exploit clients can do.

  **Fuzz strategies:**
  - Type confusion.
  - Boundary numbers: NaN, ±inf, −0, 2^53, negative.
  - Huge strings and tables (memory).
  - Deeply nested tables.
  - Other players' instances.
  - Destroyed instances.
  - Replayed valid sequences.
  - Out-of-order sequences (claim reward before completing).
  - Spam at 10–1,000 per second.
  - Concurrent calls from multiple clients.
  - Teleport to objective.
  - Speed modification.

  **Oracles:**
  - Invariants.
  - Server errors.
  - Server frame time.
  - Unauthorized state change detectors: the runtime lib snapshots key state before and after each fuzz action, with a "sanctioned writers" map.
- **`security-adversary` agent** reasons about *chains*, e.g. "rate limit is per-remote but shop and inventory share state; alternate calls bypass it". It writes targeted exploit scenarios that the harness executes. Findings are only reported with a reproduced exploit, or are explicitly labeled *theoretical*.
- **Normal vs. malicious:** each finding states which capability it needs. "A normal player can do this through the UI" is a design bug. "A modified client can do this" is a security bug.

### L.5 Data safety
Checks:
- DataStore schema versioning.
- Migration functions tested against fixture snapshots of old schemas.
- A session-locking pattern.
- Budget- and throttle-aware code (`DATA-*` rules).
- A "data loss drill" scenario: kill the server mid-save and verify recovery.

`DATA_MIGRATION` changes require a migration test in the changeset.

### L.6 Compliance checks
- Text filtering (TXT-001).
- `PolicyService` gating for paid random items or other region-restricted features.
- The monetization disclosure pattern.
- Chat and voice usage per policy.
- An age-suitability questionnaire alignment checklist, presented as a reminder for the user, not legal advice.

### L.7 Vulnerability response
1. Severity is assigned (critical, high, medium, low).
2. Critical and high findings **block** the `PUBLISH_*` gates.
3. A known issue is created, plus a regression scenario.
4. For a live game: if a kill-switch config exists for the feature, RBXOS proposes flipping it (`LIVE_CONFIG`, ask), then a fix, a staging publish, and a production publish.

## M. Performance system

### M.1 Budgets (`gates.yaml` → per device class, per scenario)
```yaml
perf:
  device_classes:
    low_mobile:  {client_fps_p10: ">= 30", client_mem_mb: "<= 900",  draw_tris_k: "<= 250"}
    mid_mobile:  {client_fps_p10: ">= 45", client_mem_mb: "<= 1400"}
    desktop:     {client_fps_p10: ">= 60"}
  server:        {heartbeat_ms_p90: "<= 8", script_ms_p90: "<= 4", mem_mb: "<= 2500"}
  network:       {kbps_per_player_p90: "<= 60", remote_calls_per_player_s: "<= 30"}
  instances:     {workspace_parts: "<= 40000"}
```
These are defaults by phase, and the constitution can override them.

### M.2 Collection
- **Studio tests:**
  - `Stats` (heartbeat, physics, memory categories).
  - `ScriptProfilerService` (server and client) → per-function cost attributed to Brain systems.
  - `HeapProfilerService` → Luau heap by allocation site.
  - `SceneAnalysisService` → triangles, instances, script, animation, and audio memory.
  - Bridge taps → remote calls and bytes.
  - Emulated memory (`EmulatedTotalMemoryInMB`) for low-end device runs.
- **Live:** Analytics Query API performance metrics by `PlaceVersion` and `Platform` (FPS percentiles, memory, crash rate, server CPU and FPS), with 28-day retention.

### M.3 Usage
- **Perf diff per changeset:** "Changeset C-311 increased server `script_ms_p90` by 1.8 ms in scenario `combat.12p` (attributed: `HitValidation.rewind` 1.5 ms)". It is computed automatically when the changeset touches hot paths (systems with high runtime cost in the overlay).
- **Tradeoff reporting:** when a feature is expensive, the perf analyst presents options with *experience impact*, e.g. "lower particle rate on low_mobile only", rather than silently cutting quality.
- **Post-publish watch:** compares the live metrics of the new `PlaceVersion` against the previous version for 24–72 h and raises a regression alert through the monitor and the next session's `SessionStart` context.

## Device testing
- **Matrix** (defaults):
  - desktop 1080p and 1440p ultrawide
  - laptop 1366×768
  - tablet landscape and portrait
  - phone landscape (16:9, 19.5:9 with notch)
  - phone portrait if supported
  - console 1080p at 10-foot UI scale
- Each runs with graphics quality low and high.
- **Mechanism:**
  - `StudioDeviceSimulatorService` sets the device, resolution, orientation, and pixel density.
  - `NetworkSettings.EmulatedTotalMemoryInMB` emulates low memory.
  - Input type is emulated: touch via VirtualInput pointer actions, gamepad via the controller emulator where scriptable (⚠ VERIFY).
- **UI audit (deterministic, per device):** every visible `GuiObject`'s `AbsolutePosition` and `AbsoluteSize` is checked for:
  - overlaps between interactive or important elements
  - off-screen or clipped elements
  - safe-area and inset violations (`ScreenInsets`, `GuiService:GetGuiInset`)
  - text truncation (`TextFits == false`)
  - text too small (TextBounds height vs. device DPI, giving a physical size)
  - touch targets smaller than ~44 pt equivalent
  - contrast ratio of text over its rendered background (sampled from the screenshot)
  - z-order occlusion of key HUD elements (e.g. objective text under the crosshair)
- Only failing devices or shots produce images for Claude.

## Quality gates

### Gate definitions (excerpt of `gates.yaml` defaults)

| Gate | Measured by | Prototype | Vertical slice | Alpha | Beta / Live |
|---|---|---|---|---|---|
| FUNCTIONALITY | T1–T3 pass, no runtime errors in scenarios | blocking | blocking | blocking | blocking |
| ARCHITECTURE | Guardian: no cycles, boundary violations = 0, max module size | advisory | advisory | blocking (no high) | blocking |
| PERFORMANCE | Budgets per device class | advisory | advisory (desktop) | blocking (mid_mobile) | blocking (low_mobile) |
| SECURITY | SEC rules, fuzz suite, invariants | blocking (critical) | blocking (high+) | blocking (medium+) | blocking (medium+) |
| DATA SAFETY | DATA rules, migration tests | n/a | blocking if DataStores are used | blocking | blocking |
| UX | UI audit on the device matrix | advisory | blocking (desktop and phone) | blocking (full matrix) | blocking |
| GAME DESIGN | Critic: no blocker. Anti-slop: all verdicts resolved. | advisory | advisory | blocking (blockers) | blocking |
| PLAYER EXPERIENCE | Bot metrics vs. targets (time-to-first-reward, softlocks = 0), persona clarity | advisory | blocking (softlocks) | blocking | blocking (+ live guardrails) |
| VISUAL QUALITY | Visual regressions resolved. Art-director blockers = 0. | n/a | advisory | blocking | blocking |
| AUDIO | Feedback-channel coverage for core actions, mix levels (loudness range) | n/a | advisory | blocking | blocking |
| GAME FEEL | Feel spec met for core actions | advisory | blocking (core verbs) | blocking | blocking |
| NOVELTY | Anti-slop plus critic "generic" findings ≤ threshold | advisory | advisory | advisory | advisory |
| MULTIPLAYER | T4/T5 suites, invariants, desync | advisory | blocking (if MP) | blocking | blocking |
| COMPATIBILITY | No deprecated APIs (K1), StreamingEnabled-correct | advisory | advisory | blocking | blocking |
| DEVICE | Device matrix pass | n/a | advisory | blocking | blocking |
| MAINTAINABILITY | Strict-typing coverage %, duplication %, test coverage of core systems | advisory | advisory | blocking (thresholds) | blocking |

Each gate result carries `{status: pass|fail|unknown, evidence_grade, evidence_refs, confidence}`. **`unknown` never counts as pass.** For example, VISUAL in headless mode is `unknown`, and the report says so.

### Gate evaluation
- Gates are evaluated incrementally. Only the gates whose inputs changed (touched systems, UI, assets) are recomputed.
- The `Stop` hook reads cached gate state and never runs suites inline.
- `rbxos.gates_check` runs the needed suites as a background job.

## Q.3 Knowing when to stop (diminishing-returns detector)
Claude may declare "further changes are unlikely to produce meaningful improvement" only when **all** of these hold:
1. All blocking gates for the current phase pass with evidence grade ≥ E2 (E3 for player experience).
2. Over the last K = 3 improvement iterations on the target, the gate metric deltas are below ε (configured per metric) **and** critic findings are only minor or nit, with a decreasing count.
3. No untested experience hypotheses remain for the targeted pillar, or the remaining ones require live evidence (E4/E5), in which case the recommendation is "ship to staging and run the live experiment".
4. The budget governor shows marginal cost per improvement rising.

The report then states what *would* change the conclusion, e.g. "live D1 data contradicting EH-3".
