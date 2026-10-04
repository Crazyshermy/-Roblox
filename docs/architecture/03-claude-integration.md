# 03: Claude Integration (C), Example Commands (V), Multi-Agent (S), Usage Efficiency (R)

## C. How `/roblox` integrates with Claude Code

### C.1 Principles
1. **Additive only.**
   - No output style replaces the system prompt.
   - No `allowed-tools` restriction applies to the session.
   - No tool is removed.
   - Specialist subagents may have narrowed tools; that is their isolation, not the main session's.
2. **Inert unless engaged.** Every hook is first evaluated by `rbxos hook <event>`, which returns immediately (exit 0, no output) when any of these hold:
   - the daemon is not running and cannot start, or
   - the cwd is not inside an RBXOS project (no `.rbxos/project.toml` up the tree), or
   - the session's mode is `off`.
3. **Deterministic before generative.** Anything that can be computed is computed by the daemon and handed to Claude in compact form.
4. **Claude stays the decider.** Hooks inform, gate actions, and inject context. They never rewrite Claude's plans.

### C.2 Activation model

| Mode | How it's entered | What's active |
|---|---|---|
| `off` | default in non-RBXOS dirs; `/roblox off` | nothing (hooks are no-ops) |
| `ambient` | default in RBXOS projects (configurable: `project.toml: ambient = true`) | Policy hooks (always on when Studio tools are used), light router (CRITICAL-only, ≤ 600 tokens), LSP, monitor. No mode skills are auto-loaded. |
| `active` | `/roblox …` | Full router budget, mode skills, gates at `Stop`, journaling of the task |

Mode is stored in the daemon per `session_id`, which hooks receive in their input JSON. A fresh session starts in the project's default mode. `/roblox off` returns to normal Claude Code behavior immediately. Policy hooks stay on for Studio tools in *every* mode when the project has opted into protection. That is a safety choice, not a capability restriction.

### C.3 Plugin layout

```
plugin/
├── .claude-plugin/plugin.json          # name "rbxos", userConfig, dependencies none
├── skills/
│   ├── roblox/SKILL.md                 # entry point: /rbxos:roblox (+ project shim → /roblox)
│   ├── roblox-build/SKILL.md           # mode skills (model-invocable, user-invocable)
│   ├── roblox-debug/SKILL.md
│   ├── roblox-test/SKILL.md
│   ├── roblox-inspect/SKILL.md
│   ├── roblox-improve/SKILL.md
│   ├── roblox-concept/SKILL.md
│   ├── roblox-experiment/SKILL.md
│   ├── roblox-polish/SKILL.md          # game feel + visual + audio pass
│   ├── roblox-ship/SKILL.md            # publish pipeline (disable-model-invocation: true)
│   ├── roblox-init/SKILL.md            # project bootstrap (disable-model-invocation: true)
│   ├── luau-engineering/SKILL.md       # paths: "**/*.{lua,luau}"; user-invocable: false
│   ├── roblox-ui/SKILL.md              # paths: "**/{UI,Gui,Interface}/**"
│   └── design-reasoning/SKILL.md       # reality check, boundary breaker, scope options
│       ├── boundary-breaker.md  scope-options.md  reality-check.md  anti-slop.md
├── agents/  (see §S)
├── hooks/hooks.json
├── .mcp.json                            # "studio" (gateway) and "rbxos"
├── .lsp.json                            # luau-lsp
├── monitors/monitors.json               # rbxos watch (when: on-skill-invoke:roblox)
├── workflows/ security-sweep.js  critic-panel.js  migrate.js  knowledge-verify.js
├── bin/rbxos                            # shim → ${CLAUDE_PLUGIN_DATA}/bin/rbxos (verified download)
└── settings.json                        # none required
```

### C.4 The entry skill (`skills/roblox/SKILL.md`)

````markdown
---
name: roblox
description: Roblox development environment. Use for any work on a Roblox/Luau project — building systems, debugging, testing, game design, performance, security, visuals — or when the user invokes /roblox. Adds Roblox tools, project memory and evaluation; does not limit normal capabilities.
argument-hint: "[verb] <request>   e.g. /roblox debug players fall through the map"
---

# Roblox environment (RBXOS)

## Session state (injected — do not re-derive)
!`rbxos context --session ${CLAUDE_SESSION_ID} --activate --from-last-prompt`

## How to work in this environment
You are still Claude; this environment adds knowledge, tools and evidence. Use judgment.

1. **Intent.** The pack above contains `intent` (classified by the daemon) and the
   relevant mode playbook name. If the classification looks wrong, say so and pick
   the right mode skill yourself (roblox-build, -debug, -test, -inspect, -improve,
   -concept, -experiment, -polish, -ship).
2. **Context.** Items marked CRITICAL are already above. Expand handles
   (`⟨h:…⟩`) with `rbxos.expand` only when needed. Ask `rbxos.search` before
   reading files. Never bulk-read the project.
3. **Settled decisions** listed above are binding unless you have *new evidence*;
   to challenge one, call `rbxos.decision_reopen` with the evidence.
4. **Before major work** run the Reality Check (design-reasoning skill) and, if the
   request is large, present Scope Options. Never silently reduce the experience.
5. **Mutations** go through checkpoints automatically; group your work into one
   changeset per coherent change (`rbxos.changeset_begin/commit`).
6. **Verify with evidence**, cheapest first: diagnostics → tests → scenario →
   multiplayer → visual/perf. State the evidence grade (E0–E5) of claims you make
   about quality or fun.
7. **Finish** by calling `rbxos.task_report` (gates + journal); report unresolved
   gates honestly.
````

Notes:
- **No `$ARGUMENTS` goes into the `!` command.** Interpolating user text into a shell is an injection risk. The `UserPromptSubmit` hook has already stored the raw prompt in the daemon, keyed by session, and `--from-last-prompt` reads it from there.
- **Bare `/roblox`:** plugin skills are namespaced (`/rbxos:roblox`). `rbxos init` writes a project-level `.claude/skills/roblox/SKILL.md`. It is a version-stamped copy of the entry skill, refreshed by `doctor`, so `/roblox` works unprefixed (⚠ VERIFY S9: if plugin skills already resolve bare names unambiguously, the shim is skipped).

### C.5 Intent classification (deterministic, in the daemon)

The daemon classifies the stored prompt using a rules plus lexicon classifier: verb keywords, error-text detection, design vocabulary, and mentions of systems matched against the Brain's glossary. The output is:

```json
{ "intent": "debug", "confidence": "high|medium|low",
  "systems": ["CombatService", "WeaponService"], "concepts": ["Humanoid.Died", "RemoteEvent"],
  "scope": "local|system|cross-system|project|new-game",
  "risk_flags": ["touches_datastore"], "playbook": "roblox-debug" }
```

When confidence is low, the pack says so and Claude decides. No LLM call is made in the hook. An optional `prompt`-type hook using a small model can be enabled for ambiguous prompts (`router.llm_fallback = true`). It is off by default.

**Intents:** build, debug, test, inspect, improve, concept, analyze, experiment, polish, ship, explain, plan, refactor, migrate, research (knowledge), and meta (configure RBXOS).

### C.6 Hook specification

| Event | Command | Behavior | Latency budget |
|---|---|---|---|
| `SessionStart` (startup, resume, compact) | `rbxos hook session-start` | Ensure the daemon is up. Register the session. Emit `additionalContext`: a project one-liner, Studio connection state, open gate failures, active task (if resumed), and **≤ 400 tokens**. On `compact`, re-inject the active task's CRITICAL set. Return `watchPaths` for `.rbxos/constitution.md` and `.rbxos/decisions/`. | 150 ms |
| `UserPromptSubmit` | `rbxos hook prompt` | Store the prompt. Classify it. In *active* mode, inject the routed context pack (budget per §H). In *ambient* mode, inject CRITICAL only. Detect `/roblox off`. | 120 ms (p95) |
| `PreToolUse` matcher `mcp__plugin_rbxos_studio__.*\|mcp__plugin_rbxos_rbxos__.*\|Bash\|Edit\|Write` | `rbxos hook pre-tool` | Policy decision (`allow`/`ask`/`deny`) with reason. For mutating calls, an auto-checkpoint if none exists for the current changeset. `updatedInput` pins `studio_id`. For Bash, block `rojo upload`, `rbxcloud publish`, and similar outside the ship flow. | 50 ms (checkpoint is asynchronous with a snapshot barrier) |
| `PostToolUse` (same matchers) | `rbxos hook post-tool` | Journal the call. Trigger an incremental reindex of touched paths. Run *fast* static checks on edited Luau (rules engine, under 100 ms). Return `additionalContext` **only** for new problems (for example, "RemoteEvent `BuyItem` handler has no argument validation (rule SEC-002)"). | 150 ms |
| `PostToolUseFailure` | `rbxos hook tool-failure` | Classify failures (Studio disconnected, timeout, policy). Inject a recovery hint. | 50 ms |
| `Stop` | `rbxos hook stop` | Evaluate the gates affected by this task's changesets. If a **blocking** gate fails and this task hasn't been blocked before, return `decision: block` with a concise reason. Otherwise record the task report. Also checks for an *unreported scope reduction* (journal entries tagged `scope_reduced` without a matching user-facing note). | 2 s (uses cached results; never runs suites inline) |
| `SubagentStop` | `rbxos hook subagent-stop` | Validate the specialist's output schema. Store findings in the daemon. Replace verbose output with a summary plus handle. | 100 ms |
| `PreCompact` | `rbxos hook pre-compact` | Persist the task state (plan, open hypotheses, failed approaches) to the journal so nothing important lives only in context. | 200 ms |
| `SessionEnd` | `rbxos hook session-end` | Close the changeset (or mark it abandoned). Release Studio locks. | 200 ms |

`FileChanged` is used for `.rbxos/*.md`, so edits made by a person to the constitution or decisions are re-indexed immediately.

### C.7 Context pack format (what Claude actually sees)

```text
⟦rbxos context · task t-0192 · intent=debug(high) · budget 2.4k/3.0k tok⟧
PROJECT: "Chronoshift" — co-op time-manipulation horror (vertical-slice phase)
STUDIO: connected (studio_id=6f1…, place 8812…), Play: stopped, tier SAFE_EDIT
CRITICAL
 • System CombatService [server] ⟨h:sys/combat⟩ — owns hit validation, damage; 3 modules
   deps: WeaponService, DamageService, Remotes.Combat.{Swing,Hit}
 • Recent runtime error ×14 (last 3m, Server): ServerScriptService.Combat.DamageService:88
   "attempt to index nil with 'Humanoid'" ⟨h:err/9f2c⟩
 • Decision D-027 (binding): hit detection is client-proposed, server-validated
   (raycast re-check, 250 ms rewind). Reopen only with latency evidence. ⟨h:dec/27⟩
 • Constitution §Tech-3: server authority for all damage & currency.
IMPORTANT (expand if needed)
 ⟨h:k/remote-validation⟩ pattern card · ⟨h:k/character-lifecycle⟩ Character respawn race
 ⟨h:exp/41⟩ prior experiment on hit windows · ⟨h:issue/12⟩ known: ragdoll desync
OPTIONAL ⟨h:sys/weapons-ui⟩ ⟨h:perf/combat-baseline⟩
STALE (suppressed): old DamageService summary (source changed) → regenerate on expand
⟦/rbxos⟧
```

### C.8 CLAUDE.md footprint
`rbxos init` adds **at most 6 lines** to the project `CLAUDE.md`. They name the project, say that RBXOS manages context, and say not to bulk-read `.rbxos/cache`. Everything else is routed.

### C.9 Compaction
- `PreCompact` persists the task state.
- `SessionStart(compact)` re-injects the task's CRITICAL set plus the "failed approaches" list, which prevents loops after compaction.
- Skills are re-attached by Claude Code itself.

---

## V. Example `/roblox` commands

```text
/roblox
→ Activates. Shows a 6-line project status: phase, Studio link, failing gates,
  top 3 risks, last task. Asks what to work on.

/roblox Make a completely original multiplayer horror game based around players
        manipulating time.
→ intent=concept, scope=new-game. Loads roblox-concept. Generates 5 divergent
  concepts. Runs the anti-slop check and boundary-breaker on each. Presents 2–3
  with core fantasy, the 30-second / 5-minute / 30-minute loops, "why this
  couldn't be a generic Roblox game", technical spikes needed, and creative-risk
  rubric. After you choose: drafts the constitution and a spike plan
  (prototype the riskiest system first).

/roblox debug players sometimes take damage after the round ends
→ Router loads RoundService and DamageService plus recent errors. Claude forms
  hypotheses (race on round-end, lingering projectile, missing state guard),
  writes a scenario that reproduces it with 4 clients, bisects, fixes, re-runs
  the scenario 20× under 150 ms latency, and adds a regression test.

/roblox where is player death handled?
→ rbxos.search returns an architecture slice: Humanoid.Died connections
  (3 sites), a custom HealthService "Downed" state, and client
  DeathScreenController via Remotes.Player.Died. Answers in ~10 lines with handles.

/roblox improve
→ Ranks the highest-value improvements from gate failures, critic findings, the
  asset-gap matrix, perf budgets, and (if live) funnel drop-offs. Proposes the
  top 3 with expected impact and evidence grade. Implements the one you pick.

/roblox test multiplayer chaos on the trading system
→ 6 clients plus 2 late joiners, 200 ms ±80 jitter, 2% loss. Malicious-client
  fuzzer on Remotes.Trade.*. Invariants: item conservation, no dupes. Reports
  pass/fail with repro seeds.

/roblox polish the sword combat — it works but feels weak
→ roblox-polish. Instruments the swing timeline (input→anim→hit→feedback
  latencies). Builds an asset/feedback-coverage matrix. Proposes a feel
  package (hitstop, camera impulse, impact VFX/SFX, enemy flinch). Implements
  it behind a config flag. Captures a before/after filmstrip and runs a bot A/B
  for combat engagement proxies.

/roblox experiment does a shorter first loop improve explorer retention?
→ Pre-registers the hypothesis and falsification criteria. Creates a config
  variant. Runs the bot population (E3) and reports per-archetype effects.
  Offers to promote to a live Open Cloud experiment (E5) with a goal metric of
  D1 retention.

/roblox security audit
→ Launches the security-sweep workflow (one adversary agent per remote
  cluster, then cross-check) and the in-engine fuzzer. Outputs a ranked
  vulnerability list with exploit repros and fixes.

/roblox inspect
→ Full baseline: architecture map, guardian metrics, remotes table, perf
  baseline, UI device matrix, asset inventory, risks, opportunities. Written to
  .rbxos/reports/baseline-<date>.md. Claude reads only the summary.

/roblox ship staging
→ roblox-ship (user-invocable only): all gates for the current phase profile,
  publish to the staging place, smoke suite via Luau Execution, then a report.
  Production publish requires PUBLISH_PRODUCTION tier plus explicit confirmation.

/roblox off
→ Session returns to plain Claude Code behavior.
```

---

## S. Multi-agent architecture

### S.1 Roster

All agents ship in `plugin/agents/`. They return **JSON matching a schema**, which the `SubagentStop` hook validates and summarizes.

| Agent | Model | Tools (narrowed) | Invoked when | Output |
|---|---|---|---|---|
| `luau-engineer` | inherit | all edit tools, rbxos, studio | Parallelizable implementation of independent modules (rare). The main session usually implements. | changeset id plus notes |
| `systems-architect` | opus-class | Read, rbxos (read), no edit | New system design over a size threshold; guardian high-severity finding; cross-system refactor | ADR draft, module plan |
| `game-designer` | opus-class | rbxos (read), WebSearch | Concept, loop design, progression, scope options | design doc delta |
| `game-critic` | opus-class | rbxos (read: evidence, screenshots, timelines) | Milestones, `/roblox improve`, after a polish pass, on request. **Never** during routine edits. | findings with evidence refs and severity |
| `anti-slop-auditor` | sonnet-class | rbxos (read) | New mechanic or system added; concept stage | per-mechanic justification verdicts |
| `feel-analyst` | sonnet-class | rbxos (read: timelines, filmstrips) | Polish mode; combat, movement, or interaction changes | feel report against the feel model |
| `art-director` | opus-class (vision) | rbxos.visual_* (read) | Visual diff over threshold; milestone review; polish | critique per shot, prioritized |
| `qa-engineer` | sonnet-class | rbxos.test_*, studio play tools | Writing scenario specs and regression tests | scenario files |
| `security-adversary` | opus-class | rbxos (read), fuzz tools (test DM only) | Changes to remotes, data, purchases, or inventory; security audit | exploit hypotheses and repros |
| `perf-analyst` | sonnet-class | rbxos.perf_* | Budget breach; perf regression detected | root-cause analysis with profiles |
| `researcher` | haiku-class | WebFetch, WebSearch, rbxos.knowledge_*, studio `http_get` | Unknown API or behavior; knowledge-card drafting | cited claims with status |
| `summarizer` | haiku-class | rbxos (read) | Lazy generation of system summaries for the Brain (cached by hash) | summary JSON |
| `persona-playtester` | sonnet-class (vision) | studio input tools, rbxos.observe | Lab persona runs (budgeted) | think-aloud log with confusion events |

"opus-class", "sonnet-class", and "haiku-class" are resolved through `userConfig` (`model_tier_high/mid/low`), so users can trade cost for quality. On Pro plans the defaults shift down one tier.

### S.2 Invocation policy (the orchestrator's rules)
1. **The main session is the orchestrator and synthesizer.** Specialists are tools, not peers.
2. A specialist is invoked only when a **trigger** in the table fires *and* the answer can't be produced from existing evidence. The daemon exposes `rbxos.should_consult(agent)`, which returns false if equivalent findings exist for the same content hashes.
3. **Read-only by default.** Only `luau-engineer` and `qa-engineer` write, and they do it within a changeset.
4. **Independence where it matters.** Critic panels run as a workflow: 3 independent critics, then each finding is adversarially verified by a fresh agent. Only surviving findings are reported. Use this for milestones only.
5. **Budget.** Each invocation states its expected token cost (estimated from history). The main session skips optional specialists once the task budget passes 70%.
6. **Fork vs. fresh.** Use `context: fork` skills when the specialist needs the conversation (rare). Otherwise use fresh agents with an explicit brief, which shares less and costs less.

### S.3 Workflows shipped
| Workflow | Shape | When |
|---|---|---|
| `security-sweep` | list remote clusters → `pipeline(adversary per cluster)` → `parallel(verify each finding)` → rank | `/roblox security audit`, pre-ship |
| `critic-panel` | 3 independent critics (design, feel, visual) → adversarial verification → merge | Milestones |
| `migrate` | discover → transform per module in worktrees → verify each with tests | Large refactors |
| `knowledge-verify` | per stale claim: run probe → classify → update | After a Studio version change (nightly routine) |
| `concept-divergence` | N designers with different genre or constraint seeds → anti-slop filter → critic | `/roblox concept` |

---

## R. Usage efficiency

**Goal:** maximize useful work per token, not minimize tokens.

| # | Lever | Mechanism | Expected effect |
|---|---|---|---|
| 1 | Precomputed project model | Index plus graph plus cached summaries. Claude reads slices, not files. | Largest single saving on large projects (⚠ measure: target ≥ 60% fewer file-read tokens vs. baseline on the eval suite) |
| 2 | Budgeted router | CRITICAL inline, everything else as handles, STALE suppressed | Bounded per-prompt overhead (≤ 3k tokens active, ≤ 600 ambient) |
| 3 | Session dedupe ledger | The router never re-injects an item already in context. The ledger resets at compaction. | Removes repeated injection |
| 4 | Output shaping | Gateway and rbxos tools return summaries plus handles. Defaults: 2k-token result cap and 200-line log cap. Logs are deduplicated by signature with counts. | Prevents 25k-token tool dumps |
| 5 | Failures-only test reporting | Pass counts plus failing cases with a minimal repro | Order-of-magnitude smaller than raw logs |
| 6 | LSP diagnostics | Type errors arrive automatically after edits | Avoids "run, read output, fix" turns |
| 7 | Deterministic analyzers first | UI geometry, perf budgets, guardian metrics, security rules | LLM judgment only on flagged items |
| 8 | Image discipline | Images only for shots that fail deterministic checks, or at milestones. Downscaled to ≤ 1024 px. Filmstrips tiled into one image. | Images are among the most expensive inputs |
| 9 | Model tiering | haiku-class for summarization and classification fallback, sonnet-class for routine specialists, opus-class for design and critique | Lower cost per specialist call |
| 10 | Content-hash caching of LLM artifacts | Summaries and critiques are reused until the source hash changes | Critiques of unchanged systems are never recomputed |
| 11 | Stable prompt prefixes | Skills and agent prompts are static. Dynamic content goes last in a consistent order. | Better prompt-cache hit rate |
| 12 | Event-driven monitoring | The monitor emits only *new* error signatures and gate transitions | No polling turns |
| 13 | Zero-token evidence | In-engine bots, fuzzers, and suites run without Claude | Most evidence is free |
| 14 | Budget governor and stop rule | Per-task budget. Cost preview for expensive steps (persona runs, workflows). Diminishing-returns detector. | Stops polishing when evidence says further gains are marginal |
| 15 | Optional offload to Roblox subagents | `explore`/`playtest` through the built-in server for coarse exploration | ⚠ VERIFY S8 |

**Measurement:**
- The `Stop` hook parses the transcript's usage records (`transcript_path`) for each task and stores tokens by category: context pack, tool results, images, and subagents.
- `rbxos doctor --efficiency` reports trends.
- An evaluation suite (file 15, Phase 1 acceptance) compares RBXOS against the bare built-in MCP on 30 scripted tasks for success rate, tokens, and wall time.
