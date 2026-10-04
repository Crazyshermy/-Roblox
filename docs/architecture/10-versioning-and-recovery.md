# 10: Versioning (Q) and Failure Scenarios (X)

## Q. Versioning: changesets, checkpoints, rollback, recovery

### Q.1 Two worlds, one history
Roblox project state lives in two places:
- **Files**: Rojo- or Script-Sync-managed sources, `.rbxos/`, and assets on disk. Their native versioning is git.
- **The Studio DataModel**: maps, UI built in Studio, Studio-owned scripts, service properties, and Terrain. It has no git. Its only native history is Studio undo, place versions on publish, and autosave.

RBXOS unifies them:

| Concept | Definition |
|---|---|
| **Operation** | A single journaled mutation: file write, `dm.write` op batch, `multi_edit`, `execute_luau` (Edit), asset insert, or config change. Recorded with before and after content hashes. |
| **Changeset** | An agent-attributed group of operations with a title and intent. It is opened by `changeset_begin` (or automatically by the first mutation in a task) and closed by `changeset_commit` or at `Stop`. It maps 1:1 to a `ChangeHistoryService` recording name `RBXOS:C-<id>:<title>` so it shows in Studio's undo history. |
| **Checkpoint** | A restorable point combining: a git commit on the shadow ref `refs/rbxos/checkpoints/<id>` (the working tree, including untracked project files, captured without touching the user's branch or index, using a temporary index file and `git commit-tree`), a **DataModel snapshot manifest**, and optionally the published place version id. |
| **DataModel snapshot** | A content-addressed store (`.rbxos/cache/objects/`, blake3) of `.rbxm` blobs per *snapshot root*: each top-level child of Workspace, ReplicatedStorage, ServerStorage, ServerScriptService, StarterGui, StarterPlayer, Lighting, SoundService, Teams, and similar. It also holds a property dump of the service objects themselves (from K1 reflection) and Terrain via `CopyRegion` → `TerrainRegion` → `.rbxm`. Snapshots are incremental: only roots marked dirty since the last snapshot (from bridge watch events and journaled operations) are re-serialized, and clean roots reuse the previous hash. |

### Q.2 When checkpoints happen
- Automatically before the first mutation of each changeset (the `PreToolUse` hook calls `checkpoint` with a snapshot barrier).
- Before risky operations: `STRUCTURAL_EDIT`, migrations, mass deletes, or `execute_luau` in Edit with destructive AST signals.
- On demand: `checkpoint {label: "Before combat rewrite"}`.
- At each green gate state, labeled `green-<n>`, which gives `rollback {to: "last-green"}`.

Retention: all named checkpoints, plus the last 50 automatic ones, plus one per day for 30 days. Older CAS objects are garbage-collected.

### Q.3 Diff and inspect
- `rbxos.diff {from, to}` returns:
  - file diffs (git), and
  - a **semantic DataModel diff**: instance added, removed, moved, or renamed (rbx-dom tree comparison with referent matching by path plus a `UniqueId`/attribute fingerprint), property changes grouped by class, and script source diffs.
- The output is summarized for Claude, with the full diff as a handle. A human-readable report goes to `.rbxos/reports/changeset-C-xxx.md`.
- Users can **accept** (mark reviewed), **reject** (roll back the changeset), or **amend**.

### Q.4 Rollback semantics
- `rollback {to}` restores:
  - files through `git checkout <checkpoint-commit> -- <paths touched since>`, and
  - DataModel roots whose hash differs. Each changed root is replaced by deserializing the snapshot blob, destroying the current root, and parenting the restored one, all inside one ChangeHistory recording `RBXOS:rollback`, so a person can undo the rollback.
- **Attribution guard:** before restoring, the daemon computes the drift set of roots changed by non-RBXOS recordings or by file edits not in the journal. If the drift set is non-empty, the rollback asks the user, listing the human changes it would discard. Alternatively it offers a **selective rollback**: only roots touched exclusively by agent changesets.
- **Rojo-owned paths** are restored on the filesystem, and Rojo syncs them back.

### Q.5 Automatic failure recovery
```
mutation(s) ─► verify (T0 diagnostics, targeted tests, perf/visual if relevant)
     │ fail?
     ▼
classify failure: compile │ runtime │ test regression │ perf regression │ visual regression │ architecture
     │
     ├─ if obviously local and first failure → one direct fix attempt (counts toward budget)
     └─ else / repeated → ROLLBACK changeset → record failed approach (what + evidence)
                         → Claude re-plans with the failure context (CRITICAL in router)
                         → if 3 approaches failed → stop and report with evidence + options
```

**Regression attribution (bisect):** when a regression is found after several changesets in a task (or across tasks), `rbxos.bisect {metric|test, good, bad}` binary-searches the changesets. For each midpoint it restores the checkpoint, runs the failing evaluation, and narrows. This costs no tokens, and Claude receives only the culprit changeset and the evidence.

### Q.6 Write-ahead journal (crash consistency)
- Every operation is a state machine:

  `intent recorded → pre-checkpoint ok → applied → verified → committed`, or `→ compensated`.

- The journal is `fsync`ed in the daemon's SQLite (WAL mode).
- After a crash of the daemon, Studio, or Claude, recovery scans for operations in `applied` but not `committed`, compares current hashes with expected *after* hashes, and asks Claude or the user: keep and verify, or compensate with a rollback to the pre-checkpoint.

### Q.7 Relationship to Claude Code's native checkpoints
Claude Code's `/rewind` covers files it edited. RBXOS checkpoints are a superset: they also cover the DataModel and edits made through MCP tools. The two coexist. `rbxos doctor` explains which to use, and rolling back an RBXOS changeset also tells Claude, via `additionalContext`, which files changed.

---

## X. Failure scenarios

| Scenario | Detection | Automatic response | What Claude/user sees |
|---|---|---|---|
| **Studio disconnects** (closed, hung, bridge drop) | Bridge heartbeat misses 3 times. Gateway calls fail with a StudioMCP transport error. | Daemon marks the Studio session `lost`. In-flight operations are marked `uncertain`. Mutating tools return `STUDIO_DISCONNECTED` (retryable). Read tools fall back to the Brain and mirror (stale-flagged). Jobs pause. | One monitor line: "Studio disconnected; 1 operation uncertain (C-212 op 7)". On reconnect, **reconciliation**: hash the snapshot roots, compare with the journal, auto-confirm matching ops, and list mismatches. |
| **Studio crashes** | Same, plus the process is gone | As above. When Studio reopens, the plugin `hello` shows a new session id for the same place. The daemon offers: restore the last checkpoint DataModel, keep Studio's recovered autosave, or diff the two. | Explicit choice with a semantic diff |
| **MCP server fails** (gateway or `rbxos`) | Claude Code shows the server failed. Hooks detect the daemon is unreachable. | The `rbxos mcp` proxy restarts the daemon connection automatically. If the daemon crashed, the next client respawns it and it recovers from the journal. The gateway has an automatic direct-mode fallback suggestion (`doctor`). Hooks fail **open for reads and closed for publishes**: if the policy cannot be evaluated, publish and destructive operations are denied and everything else proceeds. | `PostToolUseFailure` hook injects a recovery hint |
| **Claude makes a bad change** | Gate or verification failure, critic blocker, or user rejection | Rollback of the changeset, a failed-approach record, and re-planning. Rejected changesets inform lessons. | Changeset report with "rolled back because …" |
| **Playtest crashes or hangs** | Test watchdog: no heartbeat from the server DM, or the deadline is exceeded | `StudioTestService:EndTest` from the server if reachable. Otherwise stop through the built-in `start_stop_play`. Last resort: ask the user to stop the test. Collect the last logs and profiles. Mark the run `crashed` with a repro. | Failure report: crash at step X with the last 50 log lines summarized, and a repro command |
| **Scripts fail** (runtime errors) | Log stream error signatures | Deduplicated into clusters (signature = normalized message plus top frame). New clusters → monitor notification. Clusters are linked to systems and recent changesets (suspect ranking). | "New error ×14 in DamageService:88 (introduced by C-212?)" |
| **Performance regresses** | Perf diff on the changeset, or the post-publish live watch | Changeset flagged. Bisect if ambiguous. Profile attribution. For live: alert plus a proposal of kill switch or rollback publish. | Perf report with attribution and options (fix, accept with justification, revert) |
| **Security vulnerability discovered** | Fuzzer or invariant violation, static rule, or adversary agent | Severity classification. Critical or high → publish gates blocked. Known issue plus a regression scenario. Live → kill-switch proposal. | Vulnerability report with a repro, then a fix workflow |
| **Tool timeout** | Deadline exceeded | Operation cancelled through the plugin's cancellation token. The idempotency key allows a safe retry. | Retry or alternative |
| **Asset unavailable** (moderated, private, deleted) | `ContentProvider` failure statuses, insert failures | Asset index marks it. The gap analysis proposes replacements. | Listed in the asset report |
| **Roblox API change** | API dump hash change, then a diff | K1 regenerated. Claims re-verified. Deprecated usages in the project flagged (COMPATIBILITY gate). Gateway tool list changes are forwarded and unclassified tools set to `ask`. | Doctor summary: "Studio updated: 3 APIs used by the project deprecated; 2 claims now outdated" |
| **Open Cloud errors or rate limits** | HTTP 429/5xx | Exponential backoff with jitter. Async operation polling resumes after a restart (operation ids persisted). | Job status |
| **Agent failed halfway through a multi-step operation** | Journal shows ops `applied` but not committed at `SessionEnd`/`Stop` | Changeset marked `incomplete`. The next session's `SessionStart` context lists it and offers to complete or roll back. | No silent half-states |
| **Team Create conflict** | Collaborator editing the same script, or a drift set overlapping the target | Defer and ask. Never overwrite another person's draft. | Prompt naming the collaborator and the script |
