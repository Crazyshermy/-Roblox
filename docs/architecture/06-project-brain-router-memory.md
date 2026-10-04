# 06: Project Brain (G), Semantic Search, Context Router (H), Memory (P)

## G. Project Brain

### G.1 Layers

| Layer | Contents | Producer | Freshness |
|---|---|---|---|
| **L0 Raw** | Source files, the live DataModel (via bridge), the mirror `.rbxl`, `project.json`/`default.project.json` | Sync providers, bridge, rbx-dom | Real time |
| **L1 Index (facts)** | Instances (path, class, key props, tags, attributes), scripts (run context, `RunContext`, enabled), modules, `require` edges (static string or instance-path resolution), exported symbols and types, function spans, event connections (`X.Event:Connect` sites), remotes (definition plus every `FireServer/OnServerEvent/FireClient/...` site, with argument shapes), DataStore keys/scopes, asset references, UI trees, ConfigService keys, AnalyticsService event names | Deterministic (full-moon AST, rbx-dom, bridge) | Incremental, per content hash |
| **L2 Semantic model** | **Systems** (clusters of modules plus instances plus remotes with a name and responsibility), **boundaries** (client/server/shared), **data flows** (remote contracts as typed edges between client and server code), **lifecycles** (player join → character → death → respawn handlers), **entry points**, **ownership** of state (who writes currency?) | Deterministic clustering plus naming heuristics, then **Claude-authored annotations** (summary, responsibility, invariants) cached by hash | Annotations are marked STALE when member hashes change |
| **L3 Intent** | Constitution, design docs, decisions, priorities, known issues, experiments | Users and Claude, via tools | Explicit edits |
| **Runtime overlay** | Observed call paths (remote → handler → error), event frequencies, perf costs per system, coverage (which handlers ran during tests) | Telemetry from test runs | Per test run |

### G.2 System detection (deterministic first pass)
1. Build the require graph plus the remote edges plus the "same folder / same name stem" affinity.
2. Weighted community detection (Leiden) over modules, with remote edges strongly coupling client and server halves of a feature (`CombatController` ↔ `CombatService` through `Remotes.Combat.*`).
3. Name each cluster by its dominant stem (`Combat`), or by a manual mapping from `.rbxos/systems.yaml` if present.
4. Infer responsibilities from writes: which modules write `leaderstats`, DataStore keys, `Humanoid.Health`, and currency attributes.
5. Claude refines this lazily. On the first `explain_system`, the `summarizer` agent writes a summary, responsibilities, and invariants (≤ 200 tokens). This is stored in `.rbxos/cache/annotations/` keyed by the member hash set, and is user-editable through `.rbxos/systems.yaml`. Edits made by people take precedence.

Example L2 view (what `rbxos.explain_system CombatService` returns):

```
System Combat  [server+client]  health: ⚠ 1 guardian finding
 Server: CombatService (entry), DamageService, HitValidation      Client: CombatController, SwingFX
 Remotes: Combat.Swing (C→S, args: {aimDir: Vector3, t: number}) · Combat.Hit (S→C)
 Writes: Humanoid.Health (via DamageService) · attribute "LastHitBy"
 Depends: WeaponService (stats), EnemyService (targets), Config: combat.* (6 keys)
 Lifecycle hooks: Players.PlayerRemoving → CombatService.cleanup
 Invariants (annotated): damage ≤ weapon.maxDamage×crit; no damage after round end
 Runtime (last suite): Swing 4.1/s/player avg, server cost 0.31 ms/frame p90
 Decisions: D-027 (hit model), D-031 (no friendly fire)   Issues: I-12
```

### G.3 Incremental update
- File change → re-parse the file → diff its L1 facts → mark affected L2 systems → invalidate annotations whose member hash changed (STALE) → reindex FTS → emit `brain.changed` (consumed by the guardian and the router).
- DataModel change (bridge events batched every 250 ms) → update instance facts. Large reparenting batches cause a subtree rescan.
- **Cold start:** the full index of a 2,000-script project takes ≤ 60 s locally (target, ⚠ measure). The mirror `.rbxl` lets headless sessions index without Studio.

### G.4 Storage
- SQLite per project in `.rbxos/cache/brain.db`, with tables `instances`, `scripts`, `symbols`, `edges`, `remotes`, `remote_sites`, `systems`, `system_members`, `annotations`, `runtime_traces`, and `fts_*` (FTS5).
- A graph query layer (`brain_query`) supports a small typed DSL (`systems where writes("Humanoid.Health")`, `path from Remotes.Shop.Buy to DataStore:*`). Claude can use it for precise structural questions.

## G'. Semantic project search

**Query pipeline** (`rbxos.search`):
1. **Parse:** detect symbols (`DamageService.apply`), instance paths, error strings, and natural language.
2. **Expand concepts:** the knowledge lexicon maps phrases to API signals. For "player death": `Humanoid.Died`, `HumanoidStateType.Dead`, `Health <= 0`, `BreakJoints`, `CharacterRemoving`, `LoadCharacter`, `"died"`, `"death"`, `"kill"`, `"respawn"`, `"downed"`. The lexicon is curated (K2) plus project glossary terms learned from names and comments.
3. **Retrieve candidates:** FTS5 BM25 over code, comments, and names; symbol and API-usage index hits; and instance names and tags.
4. **Expand over the graph:** from hit sites, follow connections (`Died:Connect` handler → called functions → remotes fired → client handlers).
5. **Re-rank:** signal strength, graph centrality within the slice, runtime evidence (the handler actually ran in tests), and recency of edits.
6. **Shape:** group by system and return an architecture slice: entities, relations, line ranges, and one-line role descriptions. The `summary` is a 5–10 line answer.

Embeddings are an optional enhancement: `sqlite-vec` plus a local small embedding model (Phase 6). They are added only if the labeled query set (100 "where is X" questions across 3 open-source Roblox games) shows recall@10 below 0.9 for the lexicon-plus-graph approach.

---

## H. Context Router

### H.1 Inputs
- The prompt and intent classification (file 03 §C.5).
- Active task state: plan, changeset, touched systems, failed approaches, open hypotheses.
- The session ledger (items already in context).
- The Brain (systems, API footprint), knowledge (cards via the API footprint and concepts), and memory (decisions, constitution sections, issues, experiments, lessons).
- Runtime: new error clusters, gate failures, and perf regressions since the last prompt.

### H.2 Pipeline
```
classify → seed set (systems/concepts named or inferred)
        → expand (1-hop deps, remotes, API footprint → cards, decisions tagged to systems,
                  constitution sections tagged to systems/intents, recent runtime evidence)
        → score   s = w_rel·relevance + w_int·intent_affinity + w_rec·recency + w_risk·risk
                      + w_bind·binding(decisions/constitution) − w_dup·already_in_context
        → classify each item: CRITICAL | IMPORTANT | OPTIONAL | STALE
        → budget pack (CRITICAL inline summaries until budget; rest → handles)
        → record ledger
```

### H.3 Classification rules (deterministic)

| Class | Rule (any) |
|---|---|
| **CRITICAL** | Binding decision or constitution rule on a touched system. Runtime error cluster in a touched system in the last 30 minutes. Failing blocking gate on a touched system. Security-sensitive context (remote validation card) when the intent touches remotes. The core summary of the seed system. |
| **IMPORTANT** | 1-hop dependency system summaries. Pattern cards for the API footprint. Experiments on the same system. Open known issues. |
| **OPTIONAL** | 2-hop dependencies. Related genre and design cards. Historical perf baselines. |
| **STALE** | An annotation whose source hash changed. A claim with status `outdated`. A superseded decision. An experiment on a removed system. These are never injected as truth. If relevant, they are *listed* with a regeneration handle. |

### H.4 Budgets

| Mode / intent | Inline budget | Handles max |
|---|---|---|
| ambient | 600 tokens | 6 |
| active, local scope | 1.5k | 10 |
| active, system scope | 3k | 15 |
| active, cross-system / project | 4k | 25 |
| concept / new-game | 2.5k (design-heavy: constitution, genre, anti-slop) | 15 |

### H.5 Dedupe ledger and compaction
- Each injected item is recorded as `{item_id, content_hash, turn}`. Re-injection happens only if the hash changed (with a "changed since" flag).
- `PostCompact`/`SessionStart(compact)` clears the ledger, and the next pack re-injects the task's CRITICAL set.

### H.6 Learning the router
- The daemon logs which handles Claude expands, and which systems or files Claude reads that the router *didn't* supply (misses).
- Weights are tuned per project by a simple bandit on the miss rate and expand rate. No LLM is involved.
- `doctor --router` shows the miss rate.

---

## P. Memory

### P.1 Files (git-tracked under `.rbxos/`)

```
.rbxos/
├── project.toml              # ids (universe/place), sync provider, phase, ambient mode, budgets
├── constitution.md           # vision, core fantasy, principles, art direction, audience, refusals…
├── systems.yaml              # optional human overrides of system map/names/owners
├── decisions/D-027-hit-validation-model.md
├── issues/I-012-ragdoll-desync.md
├── experiments/X-041-hit-window.md
├── lessons/L-009-streaming-waitforchild.md
├── invariants/*.luau         # property checks run in tests (currency conservation etc.)
├── scenarios/*.yaml          # playtest scenarios (DSL)
├── shots.yaml                # visual shots (camera, lighting, devices)
├── gates.yaml                # quality-gate profile overrides
├── personas/*.yaml           # project-specific archetype tweaks / population mix
├── knowledge/                # project knowledge overrides/additions
├── journal/2026-10-04-t0192.md   # human-readable task logs (auto)
├── reports/                  # baselines, audits, task reports (auto)
└── cache/                    # (gitignored) brain.db, CAS objects, screenshots, telemetry
```

### P.2 Constitution
Its sections are tagged so the router can select only the relevant parts:

```markdown
## Vision {#vision tags=[design,concept]}
## Core fantasy {#fantasy tags=[design,feel,concept]}
## Player target & population mix {#audience tags=[design,lab]}
## Design principles {#design-principles tags=[design,improve,polish]}
## Technical principles {#tech tags=[build,debug,refactor]}   (e.g. Tech-3: server authority for damage & currency)
## Art direction {#art tags=[visual,polish,assets]}
## Audio direction {#audio tags=[polish,assets]}
## Naming & code conventions {#conventions tags=[build,refactor]}
## Refusals (things this game will not do) {#refusals tags=[design,concept,improve]}
## Known limitations {#limitations tags=[*]}
## Current priorities {#priorities tags=[*]}
## Phase & quality-gate profile {#phase tags=[test,ship]}
```

**Ownership:** the user owns this file. Claude amends it only through `constitution_propose`, which writes a diff and requires user approval (permission tier `CONSTITUTION_EDIT`, default *ask*). Low-risk sections (`priorities`, `limitations`) can be configured as auto-approved.

### P.3 Decisions (ADR with reopen conditions)

```markdown
---
id: D-027
title: Hit detection — client-proposed, server-validated with 250 ms rewind
status: accepted        # proposed | accepted | superseded | reopened
date: 2026-09-12
systems: [Combat]
relies_on_claims: [k.engine.network-ownership#c2, k.pattern.lag-compensation#c1]
evidence: [X-038, perf:combat-baseline-2026-09-10]
reopen_if:
  - "p90 server cost of HitValidation > 0.5 ms/frame at 12 players"
  - "exploit found that bypasses rewind validation"
  - "claim k.engine.network-ownership#c2 changes status"
supersedes: [D-011]
---
## Context …  ## Decision …  ## Rejected alternatives (server raycast polling: +latency feel; pure client authority: exploitable) …  ## Consequences …
```

**Enforcement:**
- The router injects binding decisions for touched systems as CRITICAL.
- `decision_reopen` requires an evidence reference that satisfies a `reopen_if` condition, or user approval.
- The daemon evaluates `reopen_if` conditions automatically from perf, security, and knowledge events and *notifies* when a decision becomes reopenable. Decisions don't silently rot.

### P.4 Lessons and the "failed approaches" list
- Within a task, a rollback with `record_failed_approach` writes `{approach, failure_evidence}` to the task journal. The router injects it as CRITICAL for the remainder of the task, so Claude doesn't retry the same thing.
- A failed approach generalizes to a lesson when Claude records one (`lesson_record`). Lessons are routed by system and concept.

### P.5 Journal
- Every task produces a readable log: the prompt, the plan, changesets, evidence, decisions, and unresolved items.
- Journals are the long-term audit trail and the source for weekly summaries. The daemon compacts older journals into monthly digests.
