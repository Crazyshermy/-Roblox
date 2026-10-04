# 01: Research Findings, Build-vs-Integrate, and Challenged Assumptions

Research date: 2026-10-04. Primary sources were the Roblox `creator-docs` repository (engine class YAML reference, Studio, Assistant, and Open Cloud guides), the Claude Code documentation (plugins, skills, hooks, subagents, MCP, workflows), and community and press coverage. Sources are listed at the end.

---

## 1. Claude Code platform capabilities (October 2026)

| Capability | What it gives us | How RBXOS uses it |
|---|---|---|
| **Plugins** (`.claude-plugin/plugin.json`) | One installable unit that bundles skills, agents, hooks, MCP servers, LSP servers, monitors, workflows, output styles, `bin/`, `userConfig` (with secure storage for `sensitive` values), dependencies, and marketplace distribution. Persistent data lives in `${CLAUDE_PLUGIN_DATA}`. | **The installation vehicle.** Everything Claude-side ships as the `rbxos` plugin. |
| **Skills** (`SKILL.md`) | Model-invocable or user-invocable instructions. Key frontmatter fields: `context: fork`, `agent`, `paths` (glob activation), `arguments`, `model`, `effort`, `allowed-tools`, and `hooks`. Supports **dynamic context injection** with `` !`command` ``. Skill content persists across turns, and after compaction the 5k most recent tokens of each skill are re-attached. | `/roblox` entry skill plus mode skills. `` !`rbxos context …` `` injects the routed context pack *before* Claude sees the skill, which makes it deterministic and free. |
| **Subagents** (`agents/*.md`) | Per-agent `model`, `effort`, `tools`/`disallowedTools`, `skills` preload, scoped `mcpServers`, `memory: project`, `isolation: worktree`, `maxTurns`, and `hooks`. Each runs in an isolated context and returns a single report. | Specialist roster (critic, security adversary, art director, and others) with model tiering and structured outputs. |
| **Hooks** | 30+ events. Key ones: `SessionStart` (`additionalContext`, `watchPaths`), `UserPromptSubmit` (block or inject), `PreToolUse` (allow/deny/ask/defer, `updatedInput`), `PostToolUse` (`additionalContext`, `updatedToolOutput`), `Stop`/`SubagentStop` (block with reason), `PreCompact`/`PostCompact`, `FileChanged`. Handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent`. Matchers can target MCP tools (`mcp__plugin_rbxos_studio__.*`). | Policy enforcement, context routing, automatic reindexing, quality gates at `Stop`, and compaction-safe memory. |
| **MCP** | Tool search with deferred loading is on by default, so a large tool count doesn't cost context. Output cap defaults to 25k tokens and is overridable per tool via `_meta["anthropic/maxResultSizeChars"]`. Also: `list_changed`, resources (`@` mentions), prompts that become slash commands, elicitation, structured output, transports (stdio, http, ws), and *channels* (server push into the session). | Two plugin MCP servers (`studio` gateway and `rbxos`). Resources expose brain documents. |
| **LSP servers in plugins** | Diagnostics are pushed into context after edits by default. | luau-lsp with Roblox definitions and a generated sourcemap gives type errors at zero Claude cost. |
| **Monitors** (experimental) | A persistent background process whose output arrives as notifications. Can start `on-skill-invoke:<skill>`. | `rbxos watch` streams *deduplicated* Studio runtime errors and gate regressions. |
| **Workflows** | JavaScript scripts that orchestrate dozens to hundreds of subagents with schemas, `pipeline()`, and `parallel()`. Runs are resumable, and intermediate results stay out of Claude's context. They can be shipped in plugins. | Security sweeps (one agent per remote), independent critic panels with adversarial cross-checks, and large migrations. |
| **Memory** | `CLAUDE.md` hierarchy, auto memory, and subagent `memory:` scopes. | Kept minimal. RBXOS owns structured memory in `.rbxos/` and routes it. |
| **Routines / scheduled triggers** | Cron-fired sessions. | Nightly knowledge re-verification, analytics digest, and regression suite (Phase 9+). |

**Implications**

1. The routing logic belongs in **hooks and dynamic skill injection**, not in a custom agent loop.
2. A large tool count is acceptable because tool search defers loading. Each tool *result*, however, must be small.
3. Workflows give us deterministic multi-agent orchestration without writing an agent framework.

## 2. Roblox native AI capabilities

### 2.1 Built-in Studio MCP server (current recommended path)
- Built into Studio and enabled with Assistant → Manage MCP Servers → *Enable Studio as MCP server*. Uses **stdio** transport. The executable is `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP` on macOS and `%LOCALAPPDATA%\Roblox\mcp.bat` on Windows. Quick-connect supports Claude Code.
- **Tool parity with Assistant is maintained automatically**, so Roblox ships new tools without the client changing anything.
- Every call takes `studio_id`, and `list_roblox_studios` enumerates instances (name, instance id, place id).
- Tools (26):

| Group | Tools |
|---|---|
| Scripts | `script_read`, `multi_edit` (creates if missing), `script_search` (fuzzy, 10 results max), `script_grep` (50 matches max) |
| Assets and generation | `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `search_asset`, `insert_asset`, `upload_image`, `store_image` |
| DataModel | `subagent` (`explore` and `playtest` types, run by Roblox's agent), `search_game_tree`, `inspect_instance` |
| Execution | `execute_luau` (`datamodel_type`: Edit, Client, or Server) |
| Playtest | `get_studio_state`, `start_stop_play`, `get_console_output`, `screen_capture` (custom camera optional) |
| Input simulation | `character_navigation`, `user_keyboard_input`, `user_mouse_input` (can target UI instances) |
| Docs and skills | `http_get` (allow-listed Roblox docs), `skill` (Roblox-authored skills: `rbx-debug`, `rbx-device-simulator-lua`, `rbx-docs-search`, `rbx-perf-profiling`, `rbx-scene-analysis`, `rbx-unit-test`) |
| Session | `list_roblox_studios` |

- Roblox's own **Assistant** offers Planning Mode, a **playtesting agent** (beta), mesh and procedural generation, and BYOK external LLMs (Anthropic, OpenAI, Gemini).
- The legacy `Roblox/studio-rust-mcp-server` (`run_code`, `insert_model`, `run_script_in_play_mode`, `get_studio_mode`) **is no longer actively developed.**

**What the built-in server does *not* give us:**
- Multi-client test orchestration. Its play controls are single-session.
- Per-client input across N clients.
- Structured profiler data as a tool. The `rbx-perf-profiling` skill exists, but it is *guidance*, not structured data.
- A breakpoint debugger as a tool. `rbx-debug` is again a skill that drives it through `execute_luau`.
- DataModel snapshots and restore.
- Runtime event streams and push notifications.
- Remote-traffic taps.
- Network and device simulation as first-class calls.
- Project-level indexing or memory.
- Any notion of permissions beyond "the client is trusted".

### 2.2 Studio plugin API surface relevant to us (plugin security)

| Service / API | Enables | RBXOS consumer |
|---|---|---|
| `StudioTestService:ExecutePlayModeAsync / ExecuteRunModeAsync / ExecuteMultiplayerTestAsync(n ≤ 8, args)`, `:AddPlayers(n ≤ 8)`, `:EndTest`, `:GetTestArgs`, `:LeaveTest` | Programmatic solo, run, and multiplayer tests; staggered joins; client disconnects | QA, chaos testing, simulation |
| `UserInputService:CreateVirtualInput()` → `VirtualInput:SendKey/SendMouseButton/SendMousePosition/SendMouseDelta/SendPointerAction/SendTextInput` | Real input injection per client, restricted from CoreGui | Input-level bots, UX tests |
| `StudioCaptureService:CaptureScreenshot`, `RequestScreenshotPermissionAsync`; `StudioScreenshotCapture:GetBuffer/ScaleAsync`; `VideoCaptureService` | Screenshots as buffers, with a user permission prompt | Visual intelligence |
| `StudioDeviceSimulatorService` (`SetDeviceAsync`, `SetResolutionAsync`, `SetOrientationAsync`, `SetPixelDensityAsync`, custom devices) | Device matrix | Device testing |
| `NetworkSettings.Inbound/OutboundNetworkMinDelayMs / JitterMs / LossPercent`, `EmulatedTotalMemoryInMB` | Network and memory emulation during playtests | Chaos testing, low-end device testing |
| `ScriptProfilerService` (server and client start/stop/request), `HeapProfilerService`, `SceneAnalysisService` (instance/triangle composition, script/animation/audio memory, unparented-instance leaks), `Stats` | Structured performance data | Performance system |
| `ScriptDebuggerService` (breakpoints, threads, stack, variables, `Evaluate`, exception break mode) | Programmatic debugging | Debug mode |
| `SerializationService:Serialize/DeserializeInstancesAsync` (`.rbxm`), `Terrain:CopyRegion/PasteRegion` | DataModel snapshots | Checkpoints and rollback |
| `ChangeHistoryService:TryBeginRecording/FinishRecording`, `OnUndo/OnRedo` | Undo-integrated, attributable edits | Changesets |
| `ScriptEditorService:UpdateSourceAsync`, `RegisterScriptAnalysisCallback` | Safe source edits and in-editor diagnostics | Edit path, guardian surfacing |
| `HttpService:CreateWebStreamClient(WebSocket \| SSE \| RawStream)` (Studio-only, at most 4 clients) | Persistent bidirectional channel to localhost | Bridge transport |
| `LogService.MessageOut`, `GetLogHistory` | Log streams | Runtime observation |
| `AnalyticsService` (custom, funnel, onboarding, progression, and economy events; `GetPlayerSegmentsAsync`) | Live telemetry with no backend | Real-player evidence |
| `ConfigService` (snapshots, live refresh) | Live tuning and experiment variants | Fun Lab, kill switches |

### 2.3 Open Cloud

| API | Capability | Use |
|---|---|---|
| **Luau Execution** (`/cloud/v2/universes/{u}/places/{p}/versions/{v}/luau-execution-session-tasks`) | Headless real-engine Luau with full DataModel. Up to 5 minutes per task, 10 concurrent per place, binary I/O. | CI tests, headless mode on Linux and cloud sessions, server-logic sims, economy sims |
| **Place Publishing** | Upload `.rbxl` as a new place version (Saved or Published) | Staging deploys, Luau Execution targets |
| **Analytics Query API** | DAU, D1/D7/D30 retention, cohort retention, session length, funnels (step churn and completion), economy, monetization, acquisition. **Performance by `PlaceVersion`**: client FPS percentiles, memory, crash rate, server CPU/FPS/memory. 4 years of history for standard metrics, 28 days for performance. | Real-player evidence, post-publish regression detection |
| **Configs** | Draft, publish, and restore experience configs, read live via `ConfigService` | Tuning without publishing, feature flags, kill switches |
| **Experiments** | Draft, start, schedule, monitor, and complete A/B tests on config keys (and matchmaking). Exactly one baseline. Goal metric. Async operations. | The live half of the Fun Laboratory |
| DataStores / MemoryStores / Messaging / Secrets / Assets / Inventory / Notifications | Data inspection and migration, asset upload | Data safety, asset pipeline |

### 2.4 Community ecosystem

| Project | Status | Decision |
|---|---|---|
| `boshyxd/robloxstudio-mcp` (39–43 tools, read-only "inspector" edition) | **Archived June 2026** | Don't depend on it. Its read-only edition is a useful design reference for the READ_ONLY tier. |
| Other community MCPs (weppy, Justice219, drgost1 with 51 tools, and others) | Varying maintenance | Don't depend on them. The built-in server is the stable base. |
| **Rojo** (filesystem as source of truth) | Mature | Supported `SyncProvider`. Recommended for new RBXOS projects. |
| **Studio Script Sync** (GA June 2026) | Native | Supported `SyncProvider` for existing Studio-first projects |
| **luau-lsp** | Mature | Bundled as the plugin LSP |
| **Luau** `luau-analyze` (strict mode) | Official | Static gate |
| **selene** (lint), **StyLua** (format) | Mature | Static gate |
| **Lune** (standalone Luau runtime with a Roblox file-format library), **rbx-dom** (Rust `rbx_binary`/`rbx_xml`/`rbx_reflection`), **full-moon** (Rust Luau parser) | Mature | Offline engine: indexing, rbxl parsing, pure-logic tests |
| **Jest-Lua / TestEZ** | Jest-Lua is current, TestEZ is legacy | Unit-test frameworks (Roblox's `rbx-unit-test` skill detects both) |
| `Roblox/place-ci-cd-demo` (Rojo → upload → Luau Execution) | Official reference | Template for the headless CI path |
| Package managers (Wally, pesde), toolchain manager (rokit) | Mature | Detected and respected. Never forced. |

### 2.5 Community sentiment (inputs to design, not facts)
- There is widespread worry that AI floods the platform with low-quality, repetitive games. This validates the anti-slop and critic systems as *core*, not decoration.
- Developers want AI as an advisor and accelerator, not an autopilot. This argues for changesets, reviewable diffs, and the user staying creative director.
- The historic pain point was getting code onto disk and closing the loop. Script Sync and the built-in MCP now solve the basic loop. **What's still missing is higher-order evaluation: is it good, is it fun, is it secure, did it regress?** That is where RBXOS concentrates.

---

## 3. Build vs. integrate vs. wrap

| Capability | Decision | Rationale |
|---|---|---|
| Script read/edit/grep, instance inspection, Luau execution, play control, console, screenshot, basic input, asset search/insert/generation | **Integrate** (built-in MCP) **behind a wrapper** (gateway) | Roblox maintains it in lockstep. The wrapper adds policy, journaling, `studio_id` pinning, and output shaping. |
| Roblox `explore`/`playtest` subagents | **Integrate, optional** | Potentially offloads exploratory work from Claude usage. Billing and model behavior need checking (⚠ VERIFY S8). Treated as just another evidence source. |
| Multi-client tests, VirtualInput bots, profilers, debugger, device/network sim, snapshots, taps | **Build** (companion plugin + daemon) | Not exposed by the built-in server. The underlying APIs are plugin-security. |
| File sync | **Wrap** (`SyncProvider`: Rojo, Script Sync, none) | Solved natively and by the community |
| Type checking, lint, format | **Integrate** (luau-lsp, luau-analyze, selene, StyLua) | Mature |
| Unit-test frameworks | **Integrate** (Jest-Lua, TestEZ detection) | Mature |
| Live A/B, configs, analytics, publishing, headless execution | **Integrate** (Open Cloud) **behind a wrapper** (`rbxos-opencloud`) | Native. The wrapper adds scoped keys, rate limiting, and polling of async operations. |
| Project Brain, semantic search, context router, decision memory, knowledge verification, experiment registry, quality gates, critics, player simulation, changesets spanning files and DataModel, policy engine | **Build** | Nobody provides these. This is the product. |
| Rbxl/rbxm parsing | **Integrate** (rbx-dom) | Definitive library |
| Luau AST | **Integrate** (full-moon) | Used by selene and StyLua |
| Engine API metadata | **Integrate** (API dump plus creator-docs class YAML) | Machine-readable and versioned |

**Modularity rule:** every external integration sits behind a Rust trait (`StudioPort`, `SyncProvider`, `CloudPort`, `DocsSource`, `TestFramework`, `VisionProvider`) so that a Roblox update changes one adapter and nothing else.

---

## 4. Challenged assumptions

| # | Assumption in the brief | Verdict | Replacement |
|---|---|---|---|
| A1 | We need to build Claude's hands into Studio. | **Mostly false now.** | Integrate the built-in MCP. Build only the gap (§2.1). |
| A2 | A giant Roblox knowledge database will reduce hallucination. | **Risky.** A large unverified database *creates* authoritative-sounding hallucinations. | Small curated cards for what docs can't express; generated API facts from the dump; live doc lookup (`http_get`/`rbx-docs-search`) as fallback; executable probes; epistemic status on every claim (file 05). |
| A3 | Fun can be modeled as dimensions and simulated players can evaluate it. | **Partially false.** Bots can't feel. | Bots measure *behavioral proxies* (time to first reward, hesitation, dead-end rate, objective discovery time, path entropy). Fun stays a hypothesis tested with real players. Simulation output is capped at evidence grade E3. |
| A4 | Player psychology variables (quit threshold, patience…) drive simulated behavior realistically. | **Unfalsifiable until calibrated.** | Define each variable as a *policy parameter* with an observable effect. Default priors are labeled "uncalibrated". Fit them to real funnel and retention data once it exists (inverse modeling). |
| A5 | Numeric scores (Novelty 91, Confidence 0.71) aid decisions. | **False precision.** | Ordinal rubrics with justification, pairwise preference between alternatives, and real statistics only where data is real. |
| A6 | Continuous monitoring by guardian agents. | **Too costly as LLM work.** | Deterministic daemon monitors. An LLM is invoked only on threshold breach. |
| A7 | The playtest is the reality. | **Partly.** Studio playtests differ from live servers in latency, device, scale, DataStore behavior, and streaming conditions. | Network and device emulation reduce the gap. Live analytics by `PlaceVersion` (performance and crashes) close it after publishing. |
| A8 | Multiplayer chaos with many simulated players. | **Bounded.** Studio supports at most 8 real clients per test (more can be added with `AddPlayers`, which is also capped at 8 per call). It is machine-bound. | Real clients for replication and race tests (≤ 8). **Server-side phantom players** generate load (synthetic remote calls and NPC characters) to stress server logic beyond 8. This does not stress replication to real clients, and the docs say so. |
| A9 | A slash-command family (`/roblox build`, `/roblox test`…). | **Sub-optimal.** | One entry plus an intent classifier. Verbs become optional fast paths. Modes are model-invocable skills, so Claude can switch modes mid-task without user ceremony. |
| A10 | One installation. | **Achievable with 2–3 unavoidable consent clicks in Studio** (enable built-in MCP, approve plugin HTTP, approve screenshots) **plus an optional Open Cloud API key** created on the Creator Hub. | Installer plus doctor that detect and guide each click with deep links and status (file 11). |
| A11 | Automatic rollback on failure. | **Dangerous if naive.** The user may be editing Studio concurrently, and in Team Create collaborators are too. | Rollback only undoes *agent-attributed* changesets. Human edits are detected as drift and never reverted without confirmation. |
| A12 | The system can observe the running *live* game. | **Not directly.** There is no remote access to production servers. | Live observation through your own telemetry (`AnalyticsService` events), Open Cloud analytics, `ConfigService`-driven diagnostics flags, and optional HttpService to your own backend. |
| A13 | Simulated A/B before live A/B is always useful. | **Only for some questions.** | The Lab's question router sends comprehension and onboarding questions to personas, pacing and reachability to bots, and preference and retention to live experiments only. |
| A14 | Claude should automatically consult the constitution. | **Agreed, but via routing.** Whole-constitution injection wastes tokens. | Constitution sections are routed like any other context (file 06 §H). |

## 5. Contradictions in the brief and how they resolve

1. **"Don't restrict Claude" vs. permission modes, quality gates, and decision locks.** Restrictions apply to *actions on the project* and to *re-litigating settled decisions*, never to reasoning or tool availability. Gates *report* and can block a `Stop` once per task with reasons. They cannot trap Claude in a loop: there is a hard maximum of one block, after which Claude must report unresolved gates to the user.
2. **"Never simplify" vs. "minimize usage" vs. "know when to stop."** These are reconciled by an explicit *tradeoff surface*. Scope intelligence presents options, the user or constitution picks, and a budget governor plus a diminishing-returns detector stop polishing *only with evidence*.
3. **"Automatically load relevant knowledge" vs. "don't dump context."** The router resolves this with budgets plus handles.
4. **"Simulated players give insight" vs. "simulation isn't evidence."** Evidence grades resolve it, and a question router sends each question to the right evidence tier.
5. **"Continuous everything" (guardian, performance, visual) vs. efficiency.** "Continuous" means deterministic and in the daemon. "Judgment" means LLM, on triggers only.
6. **"Claude decides" vs. "creative vision preserved."** The user owns the constitution. Claude may *propose* amendments, and changes to vision or principles require user approval (permission tier `CONSTITUTION_EDIT`).

## 6. Technically impossible or impractical as stated

| Item | Reality | What we do instead |
|---|---|---|
| Headless *rendered* Roblox clients at scale | There is no supported headless client. Studio clients cap at 8 per test. | ≤ 8 real clients plus server-side phantom load plus Luau Execution for server logic |
| Running bots on live public servers with alt accounts | Against Roblox Terms of Use and community standards | Bots exist only in Studio tests and headless executions |
| Faithful emotional simulation | Not achievable with current technology | Behavioral proxies plus LLM personas that produce *qualitative* think-aloud, labeled as such |
| Pixel-perfect visual regression of animated scenes | Nondeterminism from particles, physics, time of day, and streaming | "Shot" definitions freeze `ClockTime`, pause physics, seed or disable emitters, and pin the camera. SSIM thresholds per shot plus a separate UI-geometry analyzer (fully deterministic). |
| MicroProfiler as structured API data | Dumps are file-based and Studio-UI-driven. `ScriptProfilerService` and `HeapProfilerService` are API-driven. | Use the API profilers. Delegate MicroProfiler interpretation to Roblox's `rbx-perf-profiling` skill when needed. |
| "Studio crashes, recover in-flight edits" | Edits not yet snapshotted can be lost | Write-ahead operation journal plus snapshot-before-mutate. Recovery replays from the last snapshot and the journal. Studio autosave recovery is a secondary source. |
| Plugins saving the place file | No plugin API saves the `.rbxl` | Snapshots via `SerializationService` plus the daemon-built mirror `.rbxl` (rbx-dom) |

## 7. Capabilities the brief missed (added)

1. **DataStore and data safety.** Studio playtests with API access enabled hit **real** DataStores. RBXOS defaults tests to a mock or dev-scoped store, provides schema versioning and migration checks, and treats data-loss risk as a top-severity gate.
2. **Free-model and Toolbox supply-chain security.** It scans inserted assets for scripts, `require(<assetId>)`, `getfenv`/`setfenv`/`loadstring`, obfuscation, and hidden HTTP or Marketplace calls, and quarantines anything suspicious. This is a well-known Roblox attack vector.
3. **Prompt-injection defense.** Instance names, script comments, asset descriptions, and chat logs are untrusted text that enters Claude's context. Tool outputs label provenance, and policy blocks privileged actions requested by content.
4. **Compliance gates.** Text filtering (`TextService` filtering of user-generated text is mandatory), `PolicyService` (regional restrictions such as paid random items), content maturity questionnaire alignment, monetization disclosure rules, and age-appropriate design.
5. **Localization and accessibility.** `LocalizationService` coverage, text expansion in UI (German and Russian strings run long), colorblind-safe palettes, input remapping, and the subtitles/captions question for audio-critical games (horror).
6. **Live operations.** Feature flags and kill switches via `ConfigService`, staged rollout, post-publish regression watching through per-`PlaceVersion` analytics, and rollback by republishing the previous version.
7. **Multi-place universes.** `TeleportService`, reserved servers, matchmaking, and cross-server `MessagingService`/`MemoryStore`. The Brain models the universe, not just a place.
8. **Team Create awareness.** Collaborator presence, drafts and collaborative editing, edit conflicts, and attribution.
9. **Determinism tooling.** Seeded RNG injection for tests and the `RandomizeJoinInstanceOrder` network setting to catch load-order bugs.
10. **Agent observability.** Every Claude action is journaled into a human-readable task log (`.rbxos/journal/`), which makes changesets auditable and supports post-mortems.
11. **Token budget governor.** Per-task budgets, a size guideline for workflows, and a "cost of next step" estimate shown before expensive evidence runs (persona playtests, large workflows).
12. **Headless mode.** Claude Code on the web and Linux have no Studio. RBXOS degrades to offline analysis (Lune, rbx-dom) plus Open Cloud Luau Execution. This was discovered from this very environment, which is a Linux cloud container.

## 8. Phase 0 verification spikes (⚠ VERIFY items)

| ID | Question | Why it matters | Fallback if negative |
|---|---|---|---|
| S1 | Does the companion plugin load in **each client DataModel** of `ExecuteMultiplayerTestAsync` sessions, and can it open its own WebStreamClient there? | Per-client bots and taps | Inject a client runtime as LocalScripts into test DataModels and multiplex through the server-DataModel bridge using a RemoteEvent created only in the test DM |
| S2 | Is `UserInputService:CreateVirtualInput()` callable from plugin context in client DataModels? What are its focus requirements? | Input-level bots | Use built-in `user_keyboard_input`/`user_mouse_input` (single client). Use intent-level control (Humanoid, Pathfinding) for the others. |
| S3 | Does `StudioCaptureService` capture client-DataModel viewports during play, and does the permission persist? | Visual testing of multiplayer views | Built-in `screen_capture`, one client at a time |
| S4 | `SerializationService` fidelity: are services' own properties, Terrain (via `TerrainRegion`), packages, and attributes/tags preserved? Are there size limits? | Rollback correctness | Rely on file-backed state (Rojo) plus property dumps. Shrink the snapshot scope. |
| S5 | Can a stdio MCP gateway transparently proxy `StudioMCP`, including `list_changed` and image content? | Gateway design | Use hooks-only policy and connect the built-in server directly |
| S6 | Do `NetworkSettings.*NetworkMinDelayMs` and related settings apply when set by a plugin before or during `ExecuteMultiplayerTestAsync`? | Chaos testing | Manual Network Simulator preset plus documentation |
| S7 | Luau Execution API: DataStore scope, HttpService availability, `require` of packages, output size limits | Headless test design | Narrow headless mode to pure logic |
| S8 | Roblox `subagent` (explore/playtest) billing and model when called via MCP from Claude Code | Usage offloading | Don't offload |
| S9 | Can a plugin skill be invoked as bare `/roblox`, or only as `/rbxos:roblox`? | UX | Installer writes a project-level `.claude/skills/roblox/SKILL.md` shim |
| S10 | Throughput and latency of a WebStreamClient WebSocket for binary snapshot payloads (several MB) | Snapshot speed | Chunked frames; HTTP POST fallback |

## Sources
- Roblox creator-docs (GitHub): `studio/mcp.md`, `assistant/skills.md`, `assistant/mcp.md`, `studio/command-line-interface.md`, `studio/testing-modes.md`, `studio/network-simulator.md`, `cloud/guides/experiments.md`, `cloud/guides/analytics/*`, `cloud/guides/configs.md`, `cloud/reference/risk-levels.md`, `reference/engine/classes/{StudioTestService, VirtualInput, UserInputService, StudioCaptureService, StudioScreenshotCapture, StudioDeviceSimulatorService, NetworkSettings, ScriptProfilerService, HeapProfilerService, SceneAnalysisService, ScriptDebuggerService, SerializationService, ChangeHistoryService, ScriptEditorService, HttpService, WebStreamClient, LogService, AnalyticsService, TestService, Plugin, Terrain}.yaml`. https://github.com/Roblox/creator-docs
- Connect to the Roblox Studio MCP server: https://create.roblox.com/docs/studio/mcp
- Assistant Updates: Studio Built-in MCP Server and Playtest Automation: https://devforum.roblox.com/t/assistant-updates-studio-built-in-mcp-server-and-playtest-automation/4474643
- Studio MCP Server Updates and External LLM Support for Assistant: https://devforum.roblox.com/t/studio-mcp-server-updates-and-external-llm-support-for-assistant/4415631
- Roblox/studio-rust-mcp-server (deprecated): https://github.com/Roblox/studio-rust-mcp-server
- Roblox Studio is Going Agentic (April 2026): https://about.roblox.com/newsroom/2026/04/roblox-studio-going-agentic and coverage at https://thenextweb.com/news/roblox-ai-assistant-agentic-tools-planning-procedural-models
- Luau Execution API: https://create.roblox.com/docs/cloud/reference/features/luau-execution and https://github.com/Roblox/place-ci-cd-demo
- [Full Release] Studio Script Sync: https://devforum.roblox.com/t/full-release-studio-script-sync/4688454
- boshyxd/robloxstudio-mcp (archived): https://github.com/boshyxd/robloxstudio-mcp
- Lune: https://github.com/lune-org/lune
- Claude Code docs: plugins reference https://code.claude.com/docs/en/plugins-reference, skills https://code.claude.com/docs/en/skills, hooks https://code.claude.com/docs/en/hooks, subagents https://code.claude.com/docs/en/sub-agents, MCP https://code.claude.com/docs/en/mcp, workflows https://code.claude.com/docs/en/workflows
- DevForum community threads on AI tools in 2026: https://devforum.roblox.com/t/every-single-ai-tool-u-need-w-roblox-studio-2026/4621350 and https://devforum.roblox.com/t/developer-intelligence-the-best-ai-for-roblox-studio-in-2026/4514838
- TechCrunch, Roblox AI game creation on mobile (2026-07-16): https://techcrunch.com/2026/07/16/roblox-launches-an-ai-powered-game-creation-feature-in-its-mobile-app/
