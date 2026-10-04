# 16: Risk Register (AD) and Future Expansion (AE)

## AD. Risk register

Likelihood (L) and impact (I) are rated H, M, or L.

| # | Risk | L | I | Mitigation | Early signal |
|---|---|---|---|---|---|
| R1 | **Built-in MCP changes** (tool renames, schema changes, `studio_id` semantics) break gateway assumptions | M | M | Generic passthrough. Only targeted interception, keyed by tool name with schema-tolerant parsing. Nightly contract tests against Studio beta channel. Unknown tools default to `ask`. | Contract test failures, doctor "unclassified tools" |
| R2 | **Plugin API limits** (S1–S4, S6) are narrower than documented: plugin absent in client DMs, VirtualInput unavailable from plugin context, snapshot fidelity gaps | M | H | Phase 0 spikes *before* building. Documented fallbacks for each (file 01 §8). The design degrades by capability flags. | Spike reports |
| R3 | **Studio-only platform** (Windows/macOS). Cloud and Linux users get a reduced product. | H | M | Headless profile with honest `unknown` gates. Open Cloud Luau Execution covers server logic. Possible future remote-Studio runner (self-hosted Windows/macOS) via Remote Control. | User mix telemetry (opt-in) |
| R4 | **Token cost blow-up** from images, personas, or workflows | M | H | Budget governor, cost previews, image budgets, size guidelines for workflows, deterministic-first analyzers, caching by hash. Efficiency evaluated per release. | Eval token trends, per-task reports |
| R5 | **False confidence from simulation** (users or Claude treat E3 as truth) | H | H | Mandatory evidence grades. Output lint. Question router. Calibration plus predictive-accuracy tracking. Wording rules in skills. | Reports lacking grades (lint), user feedback |
| R6 | **Knowledge staleness or hallucination** | M | H | Epistemic statuses, probes, version-change pipeline, API existence checks, live-docs fallback, pack CI | Probe failure rate after Studio updates |
| R7 | **Data loss** (game DataStores or project state) | L | Critical | DataStoreGuard in tests. `DATA_MIGRATION` tier. Migration tests. Snapshot-before-mutate. WAL. Attribution-guarded rollback. Never rewrites user git history (shadow refs only). | Fault-injection suite |
| R8 | **Security of RBXOS itself** (local daemon as attack surface; token theft; prompt injection) | M | H | Loopback only. Per-install token plus HMAC. Socket permissions. Provenance labels. Content can't raise tiers. Production publish needs typed confirmation. Signed binaries. Third-party security review in Phase 8. | Security review findings |
| R9 | **Team Create and human-concurrency conflicts** | M | M | Drift detection, deferral, selective rollback, ownership rules | Conflict reports |
| R10 | **Roblox policy and ToS** (automation, assets, data) | L | H | Bots only in Studio and headless. No alt-account automation. Respect asset permissions. Compliance checks. Content from generators is reviewed. | Policy changes monitored in knowledge pack updates |
| R11 | **Scope and complexity of RBXOS itself** (maintenance burden, slow delivery) | H | M | Strict phase gates. First usable release after Phase 2. Every component justified (file 02 §B). Defer embeddings and dashboards. Eval-driven priorities. | Phase slippage > 30% |
| R12 | **Router misses** (Claude lacks context, reads files anyway or makes wrong assumptions) | M | M | Handles for everything relevant. Miss logging. Bandit tuning. Claude may always search or read directly (never restricted). | Miss rate metric |
| R13 | **Snapshot cost** on huge places (time and memory spikes in Studio) | M | M | Incremental dirty-root snapshots. Yielding serializer. Rojo-owned content excluded. Configurable roots. | Snapshot latency p95 |
| R14 | **Luau Execution limits** (5 min, 10 concurrent; no players) | H | L | Split suites. Use headless only for server logic. Studio for player-facing work. | CI duration |
| R15 | **Vision limits** (subtle art-quality judgments unreliable) | M | M | Deterministic metrics first. Art-director findings carry region evidence. Human acceptance of visual baselines. | User rejection rate of art findings |
| R16 | **Critic sycophancy or negativity bias** (useless praise, or nitpicks blocking progress) | M | M | Evidence-required findings. Phase-relative severity. Adversarial verification at milestones. Users can dismiss findings with reasons, which feeds calibration of the critic prompt. | Dismissal rate |
| R17 | **Analytics privacy and data minimization** | L | M | Aggregate-only Analytics API. No personal data stored. Telemetry opt-in for RBXOS itself. | — |
| R18 | **Ecosystem shift** (Roblox ships its own equivalents, e.g. a playtest agent that improves rapidly) | H | M | Integration-first design. Each RBXOS subsystem sits behind an adapter, so it can *consume* Roblox's version (e.g. the Roblox `playtest` subagent as another evidence source). The durable value is memory, evaluation, and orchestration. | Roblox announcements, tracked by the researcher agent |

## AE. Future expansion

### AE.1 More advanced player simulation
- **Learned policies:** train small policies (behavior cloning from *aggregate* live funnels, or reinforcement learning in headless sandboxes) to replace the hand-written utility functions. Hand-written affect dynamics stay as an interpretable baseline.
- **Multi-agent social simulation:** emergent group behaviors (leader and follower, griefer impact on others) and party formation from friend graphs.
- **Population digital twin:** a calibrated population per game, updated after every release, with predictive accuracy as the headline metric. Simulation is used for *forecasting* release impact before live tests.

### AE.2 Real player analytics
- An automated instrumentation planner: loops → funnels → events.
- Cohort explorer reports.
- Anomaly detection on daily metrics.
- Linking live drop-off points to Brain systems and recent changesets, which gives "release X introduced a 9% drop at funnel step 3, likely C-412".

### AE.3 A/B testing
- Experiment portfolio management: sequential testing, guardrail automation, holdouts, and a feature-flag lifecycle (stale flag cleanup by the guardian).
- Multi-armed bandits only for low-risk cosmetic or tuning parameters, never for monetization without explicit approval.

### AE.4 Autonomous development loops (bounded)
- **Routines** (Claude Code scheduled triggers):
  - nightly regression plus knowledge verification
  - a weekly "improve" proposal that drafts a changeset in a branch or worktree, plus a report, for human review
- **Autonomy contract:** a loop may act only within an explicitly granted tier (default SAFE_EDIT in a sandbox branch), must pre-register goals and stop criteria, may not publish, and must produce a reviewable changeset with evidence.
- **Escalation ladder:** report only → propose changeset → apply to staging → (never) production without a human.

### AE.5 Additional AI models
- MCP servers are model-agnostic. The `rbxos` and gateway servers work with any MCP client (Codex, Gemini CLI, Cursor), which degrades gracefully without Claude Code hooks and skills.
- Specialist agents can bind to other models where they're stronger (for example a dedicated vision model for art critique) through an adapter in agent definitions, or through MCP sampling servers.
- Evidence grading and pre-registration are model-independent, so mixed-model systems stay epistemically honest.

### AE.6 Other game engines
- The engine-agnostic core is the Router, Memory, Lab, Gates, Versioning model, Knowledge verifier framework, and Critic protocols.
- Engine adapters implement the following interfaces against Unity, Godot, or Unreal editors:
  - `EnginePort`: read model, write ops, test sessions, input, capture, profiling, snapshot
  - `SyncProvider`
  - `CloudPort`: analytics and experiments
  - a knowledge pack
- The Brain's schemas generalize: "instances" become scene graph nodes, "remotes" become RPCs or net messages, and "systems" stay the same.
- Roblox-specific modules (SEC rules, ConfigService Lab) become one adapter's plugins.

### AE.7 Additional development environments
- An IDE extension view (VS Code, JetBrains) rendering changesets, gates, and the Brain map, using the same daemon API.
- The Claude desktop and web apps through Remote Control to a machine running Studio.
- A remote Studio runner (a Windows or macOS build agent with Studio) that lets cloud sessions get full visual and multiplayer evidence. This needs Roblox licensing review and stable automation of Studio launch via its command-line interface (`--task EditPlace` / `EditFile`).

---

## Closing: the system in one paragraph
Claude stays the reasoning engine. RBXOS gives it:
- **a memory** (Brain, decisions, and constitution, routed and never dumped),
- **senses** (gateway to Roblox's own tools plus a companion plugin for profilers, captures, multi-client tests, and taps),
- **hands with an undo button** (changesets spanning files and DataModel), and
- **an epistemology** (evidence grades, pre-registered experiments, probes that re-verify knowledge, critics that must cite evidence).

Mechanical work runs in a deterministic daemon at zero token cost. Judgment is spent only where it changes outcomes. Simulated players generate hypotheses, real players settle them, and the user remains the creative director throughout.
