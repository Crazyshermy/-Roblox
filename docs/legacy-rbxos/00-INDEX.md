# RBXOS: A Roblox Development Environment for Claude Code

**Architecture document, v1.0 (2026-10-04)**

> Working name: **RBXOS**. Claude Code plugin id `rbxos`, user-facing command `/roblox`.
> Status: design. Nothing in here is built yet. Every claim about a Roblox or Claude Code capability was checked against current documentation during the research phase (see `01-research-findings.md`). Anything not yet confirmed by an experiment is marked **⚠ VERIFY** and listed as a Phase 0 spike.

---

## How to read this document

| # | File | Covers (brief section letters) |
|---|------|------|
| 00 | `00-INDEX.md` | Executive summary, design stance, top decisions |
| 01 | `01-research-findings.md` | Research results, build-vs-integrate, challenged assumptions, contradictions, infeasibilities, missing capabilities |
| 02 | `02-system-architecture.md` | **A** Executive architecture, **B** component breakdown |
| 03 | `03-claude-integration.md` | **C** Claude integration, **V** example commands, **S** multi-agent, **R** usage efficiency |
| 04 | `04-mcp-and-studio-bridge.md` | **D** MCP architecture, **E** Studio bridge, **W** tool definitions |
| 05 | `05-knowledge-system.md` | **F** knowledge architecture and verification |
| 06 | `06-project-brain-router-memory.md` | **G** Project Brain, semantic search, **H** context router, **P** memory |
| 07 | `07-game-intelligence.md` | Design intelligence, fun model, critic, anti-slop, game feel, boundary breaker, scope, risk, genre, **I** player intelligence, **J** Fun Laboratory |
| 08 | `08-qa-security-performance.md` | **K** QA, **L** security, **M** performance, device testing, quality gates, stopping criteria |
| 09 | `09-visual-and-asset-intelligence.md` | **N** visual intelligence, **O** asset intelligence |
| 10 | `10-versioning-and-recovery.md` | **Q** versioning, **X** failure scenarios |
| 11 | `11-installation.md` | **T** one-installation architecture |
| 12 | `12-data-flow.md` | **U** end-to-end request walkthrough |
| 13 | `13-tech-stack-and-repo.md` | **Y** technology stack, **Z** repository structure |
| 14 | `14-schemas.md` | **AA** data schemas |
| 15 | `15-implementation-plan.md` | **AB** implementation plan, **AC** dependency graph |
| 16 | `16-risks-and-future.md` | **AD** risk register, **AE** future expansion |

---

## Executive summary

### What the research changed

The brief assumed most of the "hands and eyes" would have to be built from scratch. As of October 2026 that is no longer true, and the architecture changes because of it.

1. **Roblox Studio ships a built-in MCP server.** It has 26 tools: script read, edit, and grep; DataModel search and inspection; `execute_luau` in Edit, Server, or Client DataModels; play start and stop; console output; `screen_capture`; character navigation; keyboard and mouse input; asset search, insert, and generation; docs lookup; Assistant skills; and Roblox-hosted `explore`/`playtest` subagents. It stays in lockstep with Roblox Assistant and routes by `studio_id` across multiple Studios. Roblox has deprecated its older open-source Rust MCP server in favor of this one. **We integrate it. We do not rebuild it.**
2. **The Studio plugin API now covers most of the deeper capabilities**, but the built-in MCP server does not expose them:
   - `StudioTestService` runs programmatic multiplayer tests with up to 8 clients and can add players mid-session.
   - `VirtualInput` provides per-client input injection.
   - `StudioCaptureService` captures screenshots.
   - `ScriptProfilerService`, `HeapProfilerService`, and `SceneAnalysisService` provide profiling and scene analysis.
   - `ScriptDebuggerService` provides breakpoints, stacks, and variables.
   - `StudioDeviceSimulatorService` controls device presets, resolution, and orientation.
   - `NetworkSettings` sets latency, jitter, and loss per direction.
   - `SerializationService` serializes `.rbxm` from Luau.
   - `HttpService:CreateWebStreamClient` opens WebSocket, SSE, or raw streams, Studio-only.

   **This gap is where our own code belongs:** a companion Studio plugin plus a local daemon.
3. **Open Cloud already provides real-player evidence infrastructure:**
   - Headless **Luau Execution** against a place version (up to 5 minutes per task, 10 concurrent per place).
   - **Place Publishing**.
   - The **Analytics Query API**: retention, funnels, economy, and per-place-version performance and crash metrics.
   - **Configs** with live `ConfigService`.
   - An **Experiments API**: A/B tests on configs and matchmaking.

   The planned "experimentation engine" should be a thin layer over these, not a parallel system.
4. **Claude Code's plugin system is the natural "one installation" vehicle.** One plugin can bundle skills, subagents, hooks (including `UserPromptSubmit` context injection, `PreToolUse` policy, and `Stop` gates), MCP servers, an LSP server (luau-lsp diagnostics pushed after every edit), background **monitors** (Studio events streamed into the session), **workflows** (deterministic multi-agent fan-out), and `userConfig` secrets.
5. **Studio Script Sync reached general availability in June 2026** and coexists with Rojo. File sync is a solved problem that we wrap behind a `SyncProvider` abstraction. We do not invent our own.

### What RBXOS is

RBXOS is an **intelligence and orchestration layer**. It is not a bigger MCP server. Its runtime pieces:

```
Claude Code ──(plugin: skills · agents · hooks · LSP · monitors · workflows)──┐
   │                                                                          │
   ├── MCP "studio"  → rbxos gateway → Roblox built-in Studio MCP (integrated)│
   ├── MCP "rbxos"   → rbxos daemon  (Project Brain, Router, Knowledge,       │
   │                                  Lab, QA, Versioning, Policy, Open Cloud)│
   └── LSP "luau"    → luau-lsp (type/diagnostic feedback, zero Claude cost)  │
                          │                                                   │
          rbxosd daemon ──┼── WebSocket ── RBXOS Companion Studio Plugin      │
                          │                (Edit DM · Server DM · Client DMs) │
                          ├── Open Cloud (Luau Execution, Publish, Analytics, │
                          │               Configs, Experiments, DataStores)   │
                          └── Lune / rbx-dom offline engine (headless mode)   │
```

### The ten decisions that shape everything

1. **Integrate the built-in Studio MCP through a thin gateway.** Building our own primitive tools is wasted effort. The gateway adds policy, auto-checkpointing, `studio_id` pinning, journaling, and output shaping. It passes through any tool it doesn't recognize, so Roblox's future tools show up automatically.
2. **Build a companion Studio plugin for the capabilities the built-in server lacks:** multi-client tests, per-client input, profilers, debugger, device and network simulation, snapshots, runtime taps, and the bot runtime.
3. **Put a long-lived local daemon (`rbxosd`, Rust) under everything.** Indexing, the bridge, snapshots, telemetry, and policy must outlive any single Claude session, be shared across sessions and subagents, and fail independently of Claude.
4. **Make the context router deterministic, not LLM-driven.** Retrieval and ranking run in the daemon in milliseconds and cost zero tokens. The router injects a small budgeted pack of "critical" items plus *handles* that Claude can expand on demand. This is progressive disclosure.
5. **Keep all project memory in git-tracked plain files** (`.rbxos/`: constitution, decisions, experiments, known issues, quality-gate profiles). The machine index is a disposable SQLite cache. People can review, diff, and own the memory.
6. **Treat knowledge as claims with epistemic status, not as facts.** Each claim is tagged documented, observed, inferred, convention, uncertain, or outdated. Executable *probes* re-verify claims whenever the Studio/API version hash changes. Generated API facts come from the API dump. Curated cards add only what the docs can't say.
7. **Grade evidence explicitly, from E0 (assertion) to E5 (real-player controlled experiment).** Simulated players produce E3 at most. No subsystem may present E3 as if it were E4 or E5. This replaces the brief's single "confidence: 0.71" numbers, which are false precision.
8. **Run player simulation in two tiers.** Thousands of cheap in-engine utility-AI bots, parameterized by motivation vectors and costing zero tokens, find reachability problems, softlocks, pacing timelines, exploits, and load issues. A few expensive LLM "persona playtesters" (think-aloud from screenshots and perceptible state) are reserved for onboarding and comprehension questions. Real players come through Open Cloud Experiments.
9. **Treat every experiment as a config variant.** Simulated experiments and live A/B tests use the same mechanism: `ConfigService` keys plus the Open Cloud Experiments API. A hypothesis tested in simulation can be promoted to a live test without code changes.
10. **Make checkpoints span both worlds.** File state goes into git on a shadow ref. DataModel state goes into a content-addressed `.rbxm` snapshot store, and Terrain is captured with `CopyRegion`. Rollback restores both, attributes edits to the agent or the human, and never silently reverts human work.

### Design stance on the brief's hard requirements

- **"/roblox must not restrict Claude."** RBXOS is purely additive. It does not replace the system prompt with an output style, does not restrict tools through `allowed-tools`, and does not route Claude's reasoning through a fixed pipeline. Its hooks are no-ops unless the session has activated `/roblox`, or the project opts into ambient mode. The only things it constrains are *actions on the user's project* (permission tiers) and *churn on settled decisions* (decision memory). Neither constrains reasoning, and both can be overridden with evidence or user approval.
- **"Do not dumb down."** The scope-intelligence protocol (file 07) requires Claude to present architecture options together with a quantified *experience-preservation* estimate, and it forbids silent simplification. The `Stop` hook checks the task journal for unreported scope reductions.
- **"Do not waste usage."** Mechanical work runs in the daemon or engine. Claude sees summaries plus handles, never raw dumps. Specialists are invoked by explicit triggers and use model tiers. Images (the most expensive input) come after deterministic checks. File 03 §R lists 14 concrete levers.

### What I explicitly rejected from the brief, and why

| Brief proposal | Problem | Replacement |
|---|---|---|
| Numeric fun/novelty/risk scores ("Novelty: 91") | False precision. LLM-generated numbers have no calibration. | Ordinal rubrics with written justification, pairwise comparison between alternatives, and evidence grades. |
| "Confidence: 0.71" on experiments | Same issue. Simulation output gets mistaken for measurement. | Effect sizes with intervals for real data (E4/E5); per-archetype direction plus robustness counts for simulations (E3). |
| One "Player Brain" that simulates psychology faithfully | Not achievable. Variables like "quit threshold" aren't observable in simulation. | Archetypes as *behavior policies* whose parameters are calibrated against real funnels once live data exists (file 07 §I.6). |
| Separate `/roblox build`, `/roblox test`… command family as the primary UX | Splits intent and duplicates routing. | One `/roblox <anything>` entry with an intent classifier. Verbs are optional shortcuts, and modes are model-invocable skills. |
| Building our own Studio "hands" MCP | Duplicates the built-in server, which Roblox maintains in lockstep with Assistant. | Gateway plus companion plugin for the gap only. |
| Building our own A/B infrastructure | Duplicates the Open Cloud Experiments API and `ConfigService`. | Thin "Lab" layer over the native APIs. |
| Continuous LLM "guardians" | Burns usage continuously. | Deterministic monitors in the daemon. The LLM is invoked only when a threshold is crossed. |
