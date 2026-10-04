# 14: Data Schemas (AA)

The canonical form is JSON Schema 2020-12 in `schemas/`, from which Rust and Luau types are generated. The schemas are shown here in TypeScript notation for readability.

**Conventions:**
- `Id` values are prefixed strings (`C-219`, `D-027`, `X-184`, `cp_…`).
- `Hash` = blake3 hex.
- `Ts` = RFC 3339.
- `EvidenceGrade` = `"E0"|"E1"|"E2"|"E3"|"E4"|"E5"`.

## AA.1 Project state

```ts
// .rbxos/project.toml (shown as type)
interface ProjectConfig {
  schema: 1;
  name: string;
  universe_id?: number; place_ids: { main: number; staging?: number; sandbox?: number; others?: Record<string, number> };
  sync: { provider: "rojo" | "script-sync" | "none"; project_file?: string; roots?: string[] };
  phase: "prototype" | "vertical-slice" | "alpha" | "beta" | "live";
  mode: { ambient: boolean };
  budgets: { task_tokens_soft: number; images_per_task: number; persona_minutes_per_run: number };
  policy: { tiers: Partial<Record<Tier, "allow" | "ask" | "deny">>; protected_paths: string[] };
  model_tiers?: { high?: string; mid?: string; low?: string };
}

// Brain (SQLite rows; selected)
interface InstanceFact { path: string; class: string; parent: string | null; tags: string[];
  attributes: Record<string, unknown>; key_props: Record<string, unknown>; hash: Hash; owner: "studio" | "rojo" | "script-sync" }
interface ScriptFact { path: string; kind: "Script" | "LocalScript" | "ModuleScript"; run_context: "Server" | "Client" | "Legacy" | "Shared";
  file?: string; source_hash: Hash; loc: number; exports: SymbolRef[]; requires: string[]; api_usage: string[] /* "Humanoid.Died" */ }
interface RemoteFact { path: string; class: "RemoteEvent" | "RemoteFunction" | "UnreliableRemoteEvent" | "BindableEvent";
  sites: { script: string; line: number; op: "FireServer" | "OnServerEvent" | "FireClient" | "FireAllClients" | "OnClientEvent" | "InvokeServer" | "OnServerInvoke" | "InvokeClient"; arg_shape?: TypeShape }[];
  inferred_contract?: TypeShape[]; validation: "none" | "partial" | "full" }
interface SystemNode { id: string; name: string; sides: ("server" | "client" | "shared")[];
  members: string[]; member_hash: Hash; remotes: string[]; writes: string[]; depends_on: string[];
  annotation?: { summary: string; responsibilities: string[]; invariants: string[]; author: "claude" | "human"; for_hash: Hash; stale: boolean };
  runtime?: { cost_ms_p90?: number; calls_per_s?: number; last_run?: Id } }
```

## AA.2 Knowledge

```ts
interface KnowledgeCard {
  id: string;                       // "k.engine.remote-event"
  kind: "api-concept" | "pattern" | "antipattern" | "studio" | "design" | "genre" | "rule" | "boundary" | "lesson";
  title: string; summary: string;   // ≤120 tokens
  concepts: string[]; api: string[]; related: string[]; intents: Intent[];
  claims: Claim[];
  sections?: Record<string, string[] | string>; // when_to_use, when_not_to_use, security, performance, mistakes, alternatives…
  pack: { name: string; version: string } | { project: true };
}
interface Claim {
  id: string; text: string;
  status: "documented" | "observed" | "inferred" | "convention" | "uncertain" | "outdated";
  sources: { type: "docs" | "api-dump" | "probe" | "community" | "experiment"; ref: string; version?: string }[];
  probe?: string;                   // path to probe
  last_verified?: { status: "pass" | "fail" | "error"; studio_version: string; at: Ts; evidence: Id };
  replaced_by?: string;             // when outdated
}
interface EvidenceRecord { id: Id; claim?: string; probe?: string; env: "lune" | "edit" | "server" | "client" | "multiplayer" | "headless";
  studio_version?: string; result: "pass" | "fail" | "error"; observed: unknown; at: Ts }
```

## AA.3 Decisions

```ts
interface Decision {
  id: `D-${number}`; title: string; status: "proposed" | "accepted" | "superseded" | "reopened";
  date: Ts; systems: string[];
  context: string; decision: string;
  rejected: { option: string; reason: string }[];
  relies_on_claims: string[];       // claim ids
  evidence: Id[];                   // experiments, perf runs, test runs
  reopen_if: string[];              // human-readable + machine conditions below
  reopen_conditions?: { kind: "metric" | "claim-status" | "security-finding"; expr: string }[];
  supersedes?: Id[]; superseded_by?: Id;
  approved_by: "user" | "auto(low-risk)";
}
```

## AA.4 Experiments

```ts
interface Experiment {
  id: `X-${number}`; title: string; created: Ts; status: "draft" | "running" | "analyzed" | "concluded" | "promoted-live";
  hypothesis: string; mechanism: string;
  predictions: { observable: string; direction: "up" | "down" | "none"; archetypes?: string[]; min_effect?: string }[];
  falsified_if: string;
  decision_rule: string;            // keep/revert/iterate rule, declared up front
  variants: { name: string; baseline: boolean; config: Record<string, unknown> }[];
  evidence_tier: "bots" | "personas" | "live";
  population?: string; seeds?: number; runs?: number;
  live?: { open_cloud_experiment_id: string; goal_metric: string; guardrails: string[]; min_days: number };
  results?: { grade: EvidenceGrade; per_segment: Record<string, { effect: number; ci: [number, number]; n: number }>;
              sensitivity?: { stable: boolean; notes: string }; artifacts: Id[] };
  conclusion?: { survived: boolean | "partial"; summary: string; new_hypotheses: Id[]; scope: "project" | "generalizable-candidate" };
}
```

## AA.5 Player models

```ts
interface Archetype {
  id: string;                        // "explorer"
  description: string;
  params: Record<PlayerParam, Dist>; // each param a distribution
  calibration: { status: "prior" | "calibrated"; source?: string; error?: number; at?: Ts };
}
type PlayerParam = "curiosity" | "competition" | "cooperation" | "exploration" | "collection" | "mastery" | "creativity"
  | "social" | "status" | "fear_tolerance" | "humor_pref" | "grind_tolerance" | "complexity_tolerance" | "attention"
  | "patience" | "quit_threshold" | "friend_dependence" | "risk_tolerance" | "roblox_experience" | "skill";
type Dist = { kind: "beta"; a: number; b: number } | { kind: "normal"; mu: number; sigma: number; clamp: [number, number] } | { kind: "fixed"; v: number };
interface Population { id: string; mixture: { archetype: string; weight: number }[]; party_size_dist?: Dist; fidelity: "intent" | "input" | "mixed" }
interface BotTimeline { bot: string; archetype: string; seed: number; events: { t: number; kind: string; data: unknown }[];
  affect: { t: number; curiosity: number; boredom: number; frustration: number; confusion: number; fear: number; satisfaction: number }[];
  quit?: { t: number; reason: string } }
```

## AA.6 Changesets and operations

```ts
interface Changeset {
  id: `C-${number}`; task: Id; title: string; intent: string; systems: string[]; risk: "low" | "medium" | "high";
  status: "open" | "committed" | "rolled-back" | "incomplete" | "accepted" | "rejected";
  opened: Ts; closed?: Ts; checkpoint_before: Id; checkpoint_after?: Id;
  operations: Id[]; scope_reduced?: { what: string; reported_to_user: boolean }[];
  gates_after?: Record<GateName, GateResult>; perf_delta?: Record<string, number>;
}
interface Operation {
  id: Id; changeset: Id; seq: number; at: Ts;
  kind: "file.write" | "dm.apply" | "studio.multi_edit" | "studio.execute_luau" | "asset.insert" | "config.change" | "generate";
  target: string[];                  // paths / instance paths
  before: Hash[]; after?: Hash[];
  state: "intent" | "pre-checkpointed" | "applied" | "verified" | "committed" | "compensated" | "uncertain";
  tool_call?: { server: string; tool: string; input_digest: Hash; output_digest?: Hash };
  idempotency_key?: string; actor: "agent" | "agent:subagent:<name>";
}
```

## AA.7 Checkpoints and snapshots

```ts
interface Checkpoint {
  id: `cp_${string}`; label?: string; at: Ts; reason: "auto" | "pre-risky" | "manual" | "green";
  git: { ref: string; commit: string };
  dm?: SnapshotManifest; place_version?: number; studio_version?: string;
  drift_at_creation: { human_roots: string[] };
}
interface SnapshotManifest {
  id: Id; roots: { path: string; blob: Hash; size: number; reused: boolean }[];
  service_props: { service: string; props_blob: Hash }[];
  terrain?: { region_blob: Hash; extents: [number, number, number, number, number, number] };
  plugin_version: string; serializer: "SerializationService@v1";
}
```

## AA.8 Permissions and policy

```ts
type Tier = "READ_ONLY" | "SANDBOX" | "TEST" | "SAFE_EDIT" | "STRUCTURAL_EDIT" | "CONSTITUTION_EDIT"
  | "DATA_MIGRATION" | "LIVE_CONFIG" | "PUBLISH_STAGING" | "PUBLISH_PRODUCTION";
interface ToolPolicy {               // policy.toml entries (built-in & rbxos tools)
  tool: string;                      // "studio:execute_luau" | "rbxos:cloud_publish" | glob
  class: "read" | "test" | "mutate" | "execute" | "generate" | "delegate" | "publish" | "unclassified";
  requires: Tier; conditions?: { when: string; requires: Tier }[]; // e.g. when "datamodel_type == 'Edit'"
  output_shaping?: { max_tokens: number; strategy: "summary+handle" | "dedupe-logs" | "image-downscale" };
}
interface PolicyDecision { decision: "allow" | "ask" | "deny"; reason: string; tier_needed: Tier; checkpoint?: Id; confirmation_token?: string }
```

## AA.9 Runtime observations

```ts
interface LogEvent { run: Id; t: number; dm: "edit" | "server" | `client:${number}`; level: "output" | "info" | "warning" | "error";
  message: string; stack?: string; script?: string; line?: number; provenance: "untrusted:game-output" }
interface ErrorCluster { signature: Hash; normalized: string; top_frame: string; count: number; first: Ts; last: Ts;
  dms: string[]; system?: string; suspect_changesets: Id[] }
interface RemoteTapSample { run: Id; remote: string; dir: "C2S" | "S2C"; t: number; caller?: number;
  arg_shape: TypeShape; bytes_est: number; handler_ms?: number; error?: string }
interface PerfSample { run: Id; t: number; dm: string; fps?: number; heartbeat_ms?: number; physics_ms?: number;
  script_ms?: number; mem_mb?: Record<string, number>; net_kbps_in?: number; net_kbps_out?: number; instances?: number }
interface FeelEvent { run: Id; action: string; instance: string; phase: "input" | "anticipation" | "action" | "impact" | "feedback" | "recovery";
  channel?: "anim" | "sfx" | "vfx" | "camera" | "ui" | "hitstop" | "haptic"; t_ms: number; dm: string }
interface Shot { id: Hash; shot: string; device: string; checkpoint: Id; image: Hash; ui_geometry: Hash; at: Ts }
interface GateResult { status: "pass" | "fail" | "unknown"; grade: EvidenceGrade; evidence: Id[]; findings: Id[]; computed_at: Ts; inputs_hash: Hash }
```

## AA.10 Context pack and errors

```ts
interface ContextPack {
  task: Id; intent: Intent; confidence: "high" | "medium" | "low"; budget: { used: number; max: number };
  critical: PackItem[]; important: Handle[]; optional: Handle[]; stale: Handle[];
}
interface PackItem { id: string; kind: string; text: string; hash: Hash; binding?: boolean }
interface Handle { id: string; kind: string; desc: string }
type ErrorCode = "STUDIO_DISCONNECTED" | "STUDIO_NOT_BOUND" | "POLICY_DENIED" | "CONFIRMATION_REQUIRED"
  | "SYNC_OWNERSHIP" | "TIMEOUT" | "TEST_CRASHED" | "SNAPSHOT_FAILED" | "CLOUD_RATE_LIMITED" | "CLOUD_AUTH"
  | "HEADLESS_UNAVAILABLE" | "BUDGET_EXCEEDED" | "INVALID_INPUT" | "INTERNAL";
```
