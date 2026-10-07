# 15: Implementation Plan (AB) and Dependency Graph (AC)

Effort is in person-weeks (pw) for one senior engineer who is fluent in Rust and Luau, *or* an equivalent capable agent with human review. Each phase ends with acceptance criteria that are checked by the eval harness, not by assertion.

**Guiding order:**
1. Safety and plumbing.
2. Understanding (Brain and router), because every later feature depends on it.
3. Reliable action (bridge and versioning).
4. Verification (QA).
5. Perception (visual, performance, assets).
6. Adversarial work (security).
7. Judgment backed by evidence (Lab, players, critics).
8. Live operations.

---

## Phase 0: Spikes and foundations (5–6 pw)

**0.A Verification spikes** (from file 01 §8). Each produces a short report in `docs/spikes/` and, where relevant, a knowledge claim.

| WP | Spike | Exit |
|---|---|---|
| 0.A1 | S1, S2, S3: plugin presence, VirtualInput, and capture in client DataModels of `ExecuteMultiplayerTestAsync` | Matrix of what works per DataModel. Choose the primary path or fallback for E.2. |
| 0.A2 | S4: `SerializationService` round-trip fidelity across a 20-class fixture place, plus Terrain | Fidelity report. Snapshot-root strategy confirmed. |
| 0.A3 | S5: stdio proxy of `StudioMCP` (tools/list, call, images, list_changed) | Gateway feasible, or fall back to hooks-only |
| 0.A4 | S6: `NetworkSettings` from a plugin during tests | Chaos design confirmed |
| 0.A5 | S7: Luau Execution capabilities (DataStore scope, HttpService, output limits) | Headless test design |
| 0.A6 | S8, S9, S10: Roblox subagent billing, bare `/roblox`, WebSocket throughput | UX and transport decisions |

**0.B Foundations**

| WP | Deliverable | Notes |
|---|---|---|
| 0.B1 | `schemas/` v0 plus codegen (Rust and Luau) | AA.1–AA.10 |
| 0.B2 | `rbxos` binary skeleton: daemon (lockfile, socket, actors), JSON-RPC, logging, config | Linux, macOS, Windows CI |
| 0.B3 | `rbxos-store`: SQLite plus migrations plus CAS | |
| 0.B4 | Gateway v1: passthrough, `studio_id` pinning, journaling, output shaping for `search_game_tree`, `script_grep`, `get_console_output` | Depends on 0.A3 |
| 0.B5 | Policy engine v1: tiers, tool classification, `PreToolUse` hook, AST screening for `execute_luau` | |
| 0.B6 | Plugin skeleton: `plugin.json`, `.mcp.json`, `hooks.json`, `bin/` shim with signed-binary download | |
| 0.B7 | Doctor and bootstrap v1 (T.3 steps 1–2 and 4–5, 7, 9) | |
| 0.B8 | Fake-Studio test double (simulated StudioMCP plus bridge) for CI | Enables testing without Studio |

**Acceptance:**
- (1) A fresh machine runs `/plugin install` and `/rbxos:roblox`, and Claude can use the built-in Studio tools through the gateway with journaling.
- (2) A destructive `execute_luau` in Edit returns `ask`.
- (3) Wrong-Studio calls are rejected.
- (4) A `search_game_tree` on a 50k-instance place returns ≤ 2k tokens plus a handle.

---

## Phase 1: Understanding: Brain, search, router, memory, entry skill (8–10 pw)

| WP | Deliverable |
|---|---|
| 1.1 | `rbxos-index`: full-moon parsing of scripts (requires, symbols, API usage, connections, remote sites with argument shapes), rbx-dom parsing of rbxl/rbxm/rbxmx, Rojo project resolution, Script Sync and mirror support, incremental hashing |
| 1.2 | K1 generator from the API dump plus creator-docs YAML. API existence and context checker. |
| 1.3 | `rbxos-brain`: system clustering, ownership and writes inference, `explain_system`, graph query DSL, lazy annotations via the `summarizer` agent |
| 1.4 | `rbxos-search`: lexicon (seed: 150 concepts), BM25, graph expansion, slice shaping. **Labeled query set** (100 queries, 3 games). |
| 1.5 | `rbxos-router`: classifier, scoring, budgets, ledger, pack rendering. `UserPromptSubmit` and `SessionStart` hooks. |
| 1.6 | `rbxos-memory`: constitution sections, decisions with reopen conditions, issues, lessons, journal. Tools: `decision_*`, `constitution_propose`, `issue_record`, `lesson_record`. |
| 1.7 | Plugin: `roblox` entry skill, mode skills v1, `luau-engineering`, `design-reasoning` (reality check, boundary breaker, scope options, anti-slop, creative risk), project shim generation |
| 1.8 | Knowledge seed pack v0: about 120 cards (engine core, patterns, anti-patterns, Studio basics), claims as `documented` with citations. Probes deferred to Phase 6. |
| 1.9 | luau-lsp integration (sourcemap generation from the Brain for non-Rojo projects). `.lsp.json`. |
| 1.10 | Agents v1: `systems-architect`, `game-designer`, `game-critic` (reasoning-only), `anti-slop-auditor`, `researcher`, `summarizer` |
| 1.11 | `/roblox init` (T.4 steps 1–4, 6–8. The baseline playtest comes in Phase 3.) |
| 1.12 | Eval harness v1: 30 tasks across 3 open-source games, baseline vs. RBXOS (success, tokens, wall time) |

**Acceptance:**
- (1) Search recall@10 ≥ 0.85 on the labeled set (embeddings come later if this fails).
- (2) Router miss rate ≤ 15% on eval tasks.
- (3) Context tokens per task are reduced ≥ 40% vs. baseline at equal or better success rate.
- (4) Binding decisions are injected 100% of the time when relevant systems are touched (eval cases).
- (5) Cold index of a 2k-script project takes ≤ 60 s.

---

## Phase 2: Reliable action: bridge, versioning, runtime observation (8–10 pw)

| WP | Deliverable |
|---|---|
| 2.1 | Companion plugin: bridge transport (WebSocket plus HTTP fallback, auth, chunking, reconnect), capability dispatcher, dock widget, roles |
| 2.2 | Capabilities: `dm.read`, `dm.watch`, `dm.write` (ChangeHistory recordings), `logs`, `snapshot`, `ui.confirm` |
| 2.3 | Installer: per-install token, `.rbxm` build and copy, keychain |
| 2.4 | `rbxos-versioning`: operations WAL, changesets, checkpoints (git shadow ref plus DataModel manifest), incremental snapshots, semantic DataModel diff, rollback with attribution guard, recovery on reconnect or crash |
| 2.5 | Runtime observation: log streaming, error clustering, suspect ranking. `observe` and `runtime_query`. Monitor `rbxos watch`. |
| 2.6 | Sync-ownership enforcement (E.6) in the gateway and policy |
| 2.7 | Team Create awareness (drift detection, deferral) |
| 2.8 | Hooks: `PostToolUse` (journal, reindex, fast rules), `PreCompact`, `SessionEnd`, `PostToolUseFailure` |

**Acceptance:**
- (1) Kill Studio mid-changeset, then reopen: reconciliation identifies uncertain operations correctly in 10/10 fault-injection runs.
- (2) Rollback restores files and DataModel to byte-identical snapshot hashes, excluding non-serializable properties listed by spike 0.A2.
- (3) Human edits are never discarded without a prompt (fault-injection suite).
- (4) A new runtime error appears as a monitor line within 3 s.

---

## Phase 3: Verification: QA engine, gates, headless and CI (8–10 pw)

| WP | Deliverable |
|---|---|
| 3.1 | Static rules engine (SEC, DATA, MON, TXT, PERF, NET, STR, ARCH) with AST data-flow (taint) for SEC-002 |
| 3.2 | Unit testing: Jest-Lua and TestEZ detection. Lune runner for pure modules. In-engine runner via Run mode and Luau Execution. |
| 3.3 | Test runtime library v1: Telemetry, Taps, ScenarioRunner, ConfigOverride, DataStoreGuard. Injection into test DataModels only. |
| 3.4 | Scenario DSL compiler plus intent-level actions (navigate, equip, activate, wait_for, assert) plus input-level actions (VirtualInput or built-in input tools) |
| 3.5 | Multiplayer orchestration (`mp_session`): `ExecuteMultiplayerTestAsync`, `AddPlayers`, leaves, network profiles, invariants runner, repro seeds, repeat and flakiness stats |
| 3.6 | Gates engine: `gates.yaml` profiles by phase, incremental evaluation, `gates_check`, `Stop` hook governor (block once, scope-reduction check), `task_report` |
| 3.7 | Architecture guardian metrics plus findings. `systems-architect` trigger on high severity. |
| 3.8 | Headless mode and `rbxos ci` (Rojo build or mirror → upload to dev place → Luau Execution suites → JUnit and Markdown) |
| 3.9 | Agents: `qa-engineer`, `luau-engineer`. Skills: `roblox-test`, `roblox-debug` v2 (with `debug_break` via ScriptDebuggerService). |

**Acceptance:**
- (1) Eval tasks with injected bugs: RBXOS finds and fixes ≥ 80% with regression tests added.
- (2) MP suite reproduces 5 seeded race-condition bugs.
- (3) CI pipeline runs green on a reference game in GitHub Actions without Studio.
- (4) The `Stop` hook never blocks twice in one task (property test).

---

## Phase 4: Perception: visual, device, performance, assets (8–9 pw)

| WP | Deliverable |
|---|---|
| 4.1 | Capture capability (StudioCaptureService plus fallback), shots runner, determinism controls, filmstrips, tiling, CAS |
| 4.2 | UI geometry audit (overlap, safe area, truncation, size, touch target, contrast, occlusion) |
| 4.3 | Device matrix via StudioDeviceSimulatorService. Memory emulation. |
| 4.4 | Visual regression: SSIM, pHash, region diffs, baselines per checkpoint, before/after compositions |
| 4.5 | `art-director` agent and rubric. Image budget enforcement. |
| 4.6 | Performance: profilers (script, heap, scene), Stats sampling, attribution to systems, budgets, perf diff per changeset, bisect integration. `perf-analyst` agent. |
| 4.7 | Asset index, permission and status checks, feedback-coverage matrix (runtime lib `Feel` module), gap prioritization |
| 4.8 | Supply-chain scanner plus quarantine flow in the gateway for `insert_asset` |
| 4.9 | Skills: `roblox-polish`, `roblox-ui`. Agent: `feel-analyst`. |

**Acceptance:**
- (1) Seeded UI defects (12 types × 4 devices) detected ≥ 95% deterministically.
- (2) Visual regression false-positive rate ≤ 5% on 50 unchanged shots × 5 runs.
- (3) Perf regression of ≥ 1 ms server script time is attributed to the correct changeset in 9/10 runs.
- (4) 20 known-malicious free-model samples are quarantined with 0 false negatives on the sample set.

---

## Phase 5: Adversarial: security and data safety (5–6 pw)

| WP | Deliverable |
|---|---|
| 5.1 | Remote contract inference to fuzz grammar. Fuzzer strategies. Malicious-client harness (exploiter archetype). |
| 5.2 | Invariants framework (economy, inventory, combat). Sanctioned-writers map. Unauthorized-change detector. |
| 5.3 | `security-adversary` agent. `security-sweep` workflow. Findings with repro. Severity and gate wiring. |
| 5.4 | Data safety: schema version checks, migration test harness with fixtures, data-loss drill scenario |
| 5.5 | Compliance checklist rules (TXT, PolicyService, monetization) |

**Acceptance:**
- (1) On a deliberately vulnerable reference game with 15 seeded exploits, ≥ 13 are found with working repros.
- (2) Zero production DataStore access from tests (guard verified by test).

---

## Phase 6: Knowledge verification at scale (4–5 pw, can overlap Phases 3–5)

| WP | Deliverable |
|---|---|
| 6.1 | Probe runner across environments (Lune, sandbox Edit, Server, Client, multiplayer, headless) |
| 6.2 | Version-change pipeline (API dump diff → claim invalidation → re-verify) as a `knowledge-verify` workflow plus nightly routine |
| 6.3 | Discrepancy records. Ad-hoc discovery probes (`knowledge_probe` with code). K6 promotion flow. |
| 6.4 | Pack expanded to about 380 items. Pack CI (citation or probe required). |
| 6.5 | Optional embeddings for search if Phase 1 recall fails the target |

**Acceptance:** ≥ 90% of engine-behavior claims have a probe or citation. Simulating a Studio version change correctly flips seeded "changed behavior" claims.

---

## Phase 7: Judgment backed by evidence: players, Lab, critics v2 (10–12 pw)

| WP | Deliverable |
|---|---|
| 7.1 | Perception module (non-omniscient), affordance discovery plus `affordances.yaml` |
| 7.2 | Bot architecture: beliefs, affect, utility selection, actuation (intent and input), logging. Archetype presets. Populations. Party simulation. |
| 7.3 | Phantom players (server-side load) |
| 7.4 | Lab: pre-registration, config variants, runs across seeds, analysis (bootstrap CI, per-archetype, sensitivity), experiment records, question router |
| 7.5 | Persona playtester agent plus loop (screenshots plus perceptible state, think-aloud, budget, cost preview) |
| 7.6 | Psychology engine: symptom → hypotheses → discriminating predictions → ablation bots (oracle objective, infinite patience…) |
| 7.7 | Critic v2 (evidence-required), `critic-panel` workflow with adversarial verification. Feel model v2 with feel specs. Fun-proxy library. |
| 7.8 | Diminishing-returns detector. `roblox-improve` and `roblox-experiment` skills v2. |

**Acceptance:**
- (1) On 3 reference games with seeded design defects (hidden objective, reward too late, softlock, dead-end area), bots and the psychology engine rank the correct hypothesis first in ≥ 70% of cases.
- (2) Simulation reports always carry E3 labels (lint on outputs).
- (3) Critic findings carry evidence references ≥ 95% of the time.

---

## Phase 8: Hardening, docs, release v1.0 (4 pw)
- Security review of the daemon, bridge, and policy.
- Fuzzing of the JSON-RPC surfaces.
- Signed releases.
- Upgrade and downgrade tests.
- User guide.
- `claude plugin eval` suites for skill triggering.
- Telemetry opt-in.

## Phase 9: Live operations and real evidence (5–6 pw)
- Open Cloud wrappers: publish (staging and production with confirmation tokens), configs, experiments, Analytics Query.
- Instrumentation planner: generates `AnalyticsService` funnel, onboarding, progression, and economy events for the game's loops.
- Post-publish regression watch.
- Calibration of archetypes (ABC) from live funnels, with predictive-accuracy tracking.
- `roblox-ship` skill.
- Scheduled routines: nightly digest, weekly calibration.

## Phase 10+: Autonomy and expansion
- Bounded autonomous loops (§AE).
- Additional engine adapters.
- Multi-model specialists.

**Total to v1.0 (Phases 0–8):** about 60–72 pw. Phase 9 adds 5–6 pw. Parallelizable with 3 engineers to about 6–7 months. Phases 4, 5, and 6 can run concurrently after Phase 3.

---

## AC. Dependency graph

```
                    ┌──────────── 0.A Spikes ────────────┐
                    ▼                                     ▼
0.B1 Schemas ─► 0.B2 Daemon ─► 0.B3 Store ─┬─► 0.B4 Gateway ─► 0.B5 Policy ─► 0.B6 Plugin ─► 0.B7 Doctor
                                           │                                     │
                                           ▼                                     ▼
                                   1.1 Index ─► 1.2 K1 ─► 1.3 Brain ─► 1.4 Search ─► 1.5 Router ─► 1.7 Skills
                                           │                 │              ▲            ▲
                                           │                 └─► 1.6 Memory ┘            │
                                           │                                1.8 Pack ────┘
                                           ▼
                         2.1 Bridge ─► 2.2 DM caps ─► 2.4 Versioning ─► 2.5 Runtime obs ─► 2.6/2.7
                                           │                 │
                                           ▼                 ▼
                         3.3 Runtime lib ─► 3.4 Scenarios ─► 3.5 Multiplayer ─► 3.6 Gates ◄── 3.1 Rules
                                │                 │                │              ▲
                                │                 │                │      3.2 Unit / 3.8 CI
              ┌─────────────────┼─────────────────┼────────────────┼──────────────────────┐
              ▼                 ▼                 ▼                ▼                      ▼
        4.1 Capture       4.6 Perf          4.7 Assets/Feel   5.1 Fuzzer           6.1 Probe runner
        4.2 UI audit      (profilers)       4.8 Supply chain  5.2 Invariants       6.2 Version pipeline
        4.3 Devices                                           5.3 Adversary        (needs 2.1 + 3.3)
        4.4 Vis-regress                                       5.4 Data safety
              │                 │                 │                │
              └────────┬────────┴────────┬────────┘                │
                       ▼                 ▼                         │
                 7.1 Perception ─► 7.2 Bots ─► 7.4 Lab ─► 7.6 Psych engine
                       │                         ▲  ▲
                 4.1 ─►7.5 Personas ─────────────┘  └── 9.x Live experiments/analytics (calibration)
                 4.x + 7.x ─► 7.7 Critic v2 ─► 7.8 Stop/diminishing returns
```

**Critical path:** Schemas → Daemon → Store → Index → Brain → Router (usable product) → Bridge → Versioning → Runtime lib → Scenarios/MP → Gates → (Perception ∥ Security ∥ Knowledge) → Bots → Lab.

**The first usable release** ("RBXOS 0.3", after Phase 2) already beats plain Claude plus the built-in MCP on context efficiency, memory, safety, and rollback. This gives an early feedback loop.
