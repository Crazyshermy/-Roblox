# 04: MCP Architecture (D), Studio Bridge (E), Tool Definitions (W)

## D. MCP architecture

### D.1 Servers exposed to Claude

| Server (plugin-registered name) | Process | Purpose | Tool prefix |
|---|---|---|---|
| `studio` | `rbxos studio-gateway` → platform `StudioMCP` | Roblox's built-in tools, wrapped | `mcp__plugin_rbxos_studio__*` |
| `rbxos` | `rbxos mcp` → daemon | High-level intelligence tools | `mcp__plugin_rbxos_rbxos__*` |

**Why two servers and not one:**
- The `studio` server is a pass-through whose tool list Roblox controls.
- Keeping it separate means a Roblox update never collides with our names.
- Users can disable either one independently.
- Hooks can match each server separately.

**Duplicate detection:** if the user has also connected `Roblox_Studio` directly (quick-connect), every built-in tool appears twice. `doctor` detects the duplicate and offers to remove the direct entry. The gateway also refuses to start if the same `StudioMCP` executable is already registered at a higher-precedence scope. Its error explains the fix.

### D.2 Gateway interception table

| Built-in tool | Class | Gateway behavior |
|---|---|---|
| `list_roblox_studios`, `get_studio_state`, `script_read`, `script_search`, `inspect_instance`, `get_console_output`, `http_get`, `skill` | read | Pass through. Output shaping above 2k tokens (summary plus `⟨h:…⟩` handle). Console output is deduplicated by signature. |
| `search_game_tree`, `script_grep` | read (large) | Pass through. Results are always stored in the daemon and returned as a grouped summary (by service and class) plus a handle. |
| `screen_capture` | read (image) | Pass through. Store the image (CAS) and attach `shot_id`. Downscale above 1024 px unless the caller passes `full_res`. |
| `multi_edit` | mutate | Policy check (protected paths, sync ownership). Ensure a checkpoint. Journal before and after content hashes. If the path is Rojo-owned, **deny** with the hint "edit the file `src/...` instead". |
| `execute_luau` | execute | Static screen (AST). `datamodel_type=Edit` counts as a mutation (checkpoint plus journal). Server and Client inside an active test are test-scoped (allowed under the TEST tier). |
| `start_stop_play`, `character_navigation`, `user_keyboard_input`, `user_mouse_input` | test | Allowed under the TEST tier. Journaled as test actions. |
| `insert_asset` | mutate + supply chain | Insert into a **quarantine folder** first (`ServerStorage.RBXOS_Quarantine`). Run the asset scanner (file 09 §O.4). Move to the target only if clean, or after user approval. |
| `generate_mesh`, `generate_material`, `generate_procedural_model`, `wait_job_finished`, `upload_image`, `store_image`, `search_asset` | generate/assets | Allowed under SAFE_EDIT. Journaled, and assets are registered in the asset index. |
| `subagent` | delegate | Allowed. Output is shaped and tagged `provenance: roblox-assistant`. Evidence from it is graded like any LLM evidence (E0/E1 unless backed by logs). |
| *unknown (future)* | unclassified | **Pass through with `ask`** until `policy.toml` classifies it. `doctor` lists unclassified tools. |

The gateway injects a `studio_id` when one is missing, using the project's bound Studio. It rejects a call whose `studio_id` resolves to a place outside the project's universe unless it's tagged `sandbox`.

### D.3 `rbxos` server conventions

- **Result envelope** (every tool):
  ```json
  { "ok": true,
    "summary": "≤ 12 lines, the thing Claude needs",
    "data": { "...compact structured fields..." },
    "handles": [{"id": "h:err/9f2c", "kind": "error-cluster", "desc": "14× nil Humanoid"}],
    "evidence": {"grade": "E2", "source": "test-run r-311"},
    "provenance": ["studio:server-dm", "untrusted:instance-names"],
    "truncated": false }
  ```
- **Errors:** `{ ok:false, code:"STUDIO_DISCONNECTED", retryable:true, recovery:"…" }`. Codes are enumerated in schema `14-schemas.md#errors`.
- **Long-running work** returns `job_id` immediately. `rbxos.job_wait(job_id, timeout_s ≤ 45)` streams progress through MCP progress notifications, and the monitor announces completion. No tool call blocks longer than 60 seconds.
- **Idempotency:** mutating tools accept `idempotency_key`, so a retry after a disconnect cannot double-apply.
- **Annotations** (MCP `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) are set on every tool and also feed hooks.
- **Resources:**
  - `rbxos://constitution`
  - `rbxos://system/{id}`
  - `rbxos://decision/{id}`
  - `rbxos://experiment/{id}`
  - `rbxos://report/{id}`
  - `rbxos://shot/{id}` (image)

  Users can `@`-mention these. Claude normally uses `rbxos.expand`.
- **Result size override:** `_meta["anthropic/maxResultSizeChars"]` is used only on `rbxos.expand` (up to 60k characters) for an explicit deep-dive.

### D.4 Tool inventory (`rbxos` server, about 34 tools)

| Group | Tools |
|---|---|
| Context | `context`, `expand`, `search`, `explain_system` |
| Brain | `brain_query` (graph queries), `brain_annotate` (Claude-authored summaries and responsibilities) |
| Memory | `decision_record`, `decision_reopen`, `issue_record`, `constitution_propose`, `lesson_record` |
| Versioning | `changeset_begin`, `changeset_commit`, `checkpoint`, `rollback`, `diff`, `bisect` |
| Runtime | `observe` (live summary), `runtime_query`, `debug_break` (debugger session ops) |
| Testing | `test_run` (static, unit, scenario, suite), `mp_session` (multiplayer orchestration), `scenario_write`, `fuzz_remotes`, `gates_check` |
| Lab | `sim_run`, `persona_run`, `experiment_create`, `experiment_status`, `experiment_conclude` |
| Perf / Visual / Assets | `perf_profile`, `perf_compare`, `visual_capture`, `visual_compare`, `ui_audit`, `asset_audit` |
| Knowledge | `knowledge_lookup`, `knowledge_probe` |
| Cloud | `cloud_publish`, `cloud_config`, `cloud_analytics`, `cloud_experiment` |
| Task | `task_report`, `job_wait`, `budget_status` |

---

## E. Roblox Studio Bridge

### E.1 Components
- **RBXOS Companion Plugin** (Luau, strict types, built with Rojo, tested with Jest-Lua). It is installed as `RBXOS.rbxm` into the local Studio Plugins folder by the installer.
- **Bridge server** in `rbxosd`: a WebSocket endpoint on `127.0.0.1:47720` (falling back to 47721–47725). The HTTP endpoint `/v1/rpc` on the same port is a fallback.

### E.2 DataModel roles

```
Studio process (author)                 Test session processes
┌──────────────────────┐   start test   ┌──────────────┐  ┌──────────────┐
│ Edit DM              │ ─────────────► │ Server DM    │  │ Client DM ×N │
│ role=edit            │                │ role=server  │  │ role=client:k│
│ authoring, snapshots,│                │ taps, invari-│  │ VirtualInput,│
│ index feed, capture  │                │ ants, phantom│  │ perception,  │
│ device/network sim   │                │ load, profil.│  │ capture, mal-│
└──────────┬───────────┘                └──────┬───────┘  │ icious client│
           │ ws (token)                        │ ws       └──────┬───────┘
           └──────────────────────► rbxosd ◄───┴─────────────────┘ ws
```

Each DataModel in which the plugin runs opens **one** WebStreamClient (the limit is 4 per Studio process). On `hello` it identifies itself as `{studio_session_id, place_id, universe_id, role, test_run_id?, client_index?, studio_version, plugin_version, capabilities[]}`. The test run id is passed through `StudioTestService` `args` and read with `GetTestArgs()`. ⚠ VERIFY S1: if the plugin does not run in client DataModels, the server-DM bridge injects a client runtime as LocalScripts *into the test DataModel only* and multiplexes over a RemoteEvent that exists only in that test session.

### E.3 Authentication and pairing
- At install, the installer builds `RBXOS.rbxm` with a per-install 256-bit token in a `StringValue` (named `Token`) inside the plugin, and stores the same token in the OS keychain for the daemon. The plugin file lives in the user's own Plugins folder, so the trust boundary is the user account, the same as for the daemon socket.
- Every frame is authenticated: the first frame sends the token, and the daemon replies with a session key. Afterwards, an HMAC is computed per message.
- Only loopback is used. The daemon rejects non-loopback peers.
- Studio's own HTTP permission prompt for `localhost` is the user-visible consent.

### E.4 Protocol
- JSON-RPC 2.0 over WebSocket text frames. Large binary data (snapshots, screenshots) is sent as **chunked base64 frames of at most 512 KiB** with a manifest and blake3 hashes (⚠ VERIFY S10 throughput). The fallback is HTTP POST of chunks.
- Requests flow both ways. The daemon calls the plugin (capabilities), and the plugin calls the daemon (event streams, job updates).
- **Heartbeat** every 2 s. The connection is presumed lost after 3 misses. The plugin reconnects with exponential backoff (0.5 s → 8 s).
- **Versioning:** `hello` negotiates `protocol: 1`. Capabilities are feature flags, so an older plugin with a newer daemon degrades gracefully, and `doctor` prompts an update.
- **Execution in the plugin:**
  - A single cooperative task queue per DataModel.
  - Each request has a deadline, and the plugin checks cancellation tokens between yields.
  - Long operations stream progress.
  - Heavy work (serializing a large subtree) yields every N instances to keep Studio responsive.

### E.5 Capability RPCs (plugin side)

| Capability | Methods | Roles |
|---|---|---|
| `dm.read` | `tree(path, depth, filter)`, `props(paths, fields)`, `tags()`, `attributes()`, `scripts_meta()` | all |
| `dm.watch` | `subscribe(paths, kinds)` → events `added/removed/changed(prop)` (batched every 250 ms) | edit |
| `dm.write` | `apply(ops[])` (typed operations: create, set, reparent, destroy, set_source), wrapped in `ChangeHistoryService:TryBeginRecording("RBXOS: <changeset>")` | edit |
| `snapshot` | `serialize(roots[]) → chunks`, `restore(manifest)`, `terrain_copy(region)`, `service_props()` | edit |
| `test` | `run_multiplayer(n, args)`, `add_players(n)`, `end(result)`, `run_mode(args)`, `play_mode(args)` | edit, server |
| `net` | `set_network(profile)`, `set_memory(mb)` | edit, before test |
| `device` | `set_device(id)`, `set_resolution`, `set_orientation`, `list_devices` | edit, client |
| `capture` | `screenshot(opts) → image`, `ui_geometry() → GuiObject rects/text metrics`, `filmstrip(fps, seconds)` | edit, client |
| `input` | `virtual(sequence[])` (VirtualInput), `intent(goal)` (Humanoid and Pathfinding) | client |
| `runtime` | `install(lib_version)`, `taps.enable(kinds)`, `invariants.load(specs)`, `bots.spawn(population)`, `phantom.spawn(n, profile)` | server, client |
| `profile` | `script_profile(start/stop/data)`, `heap()`, `scene_analysis()`, `stats()` | server, client, edit |
| `debug` | `breakpoints.set/clear`, `on_stop → frames/vars`, `evaluate`, `resume` | server, client |
| `logs` | stream of `LogService.MessageOut` with role and timestamp. History is pulled on connect. | all |
| `ui` | `dock.status(state)`, `notify(msg)`, `confirm(prompt) → bool` (in-Studio confirmation for destructive operations) | edit |

### E.6 Sync ownership rule (single source of truth)
The daemon records which `SyncProvider` owns each script path:
- **Rojo:** the filesystem is the truth. Studio edits to owned paths are rejected because they would be overwritten.
- **Script Sync:** bidirectional. Edits go through files when the folder is synced, otherwise through Studio.
- **None:** Studio is the truth. The daemon mirrors sources into `.rbxos/mirror/src/` (read-only) for indexing and luau-lsp.

Non-script instances (maps, UI built in Studio) are Studio-owned unless Rojo models them. The policy engine and the gateway both enforce ownership.

### E.7 Multi-Studio and Team Create
- Projects bind to a `{universe_id, place_id}`. The gateway pins `studio_id` by place.
- A **sandbox Studio** (an unpublished local place, or a dedicated sandbox place) can be opened alongside the main one for knowledge probes and risky prototypes. Calls tagged `sandbox` route there.
- **Team Create:**
  - The plugin reports collaborators (`Players`/`StudioService` metadata, where available) and script draft or lock state.
  - Agent edits to a script another collaborator is editing are deferred, and the user is asked.
  - Snapshots record a `human_edit_drift` flag when instances changed outside agent recordings, as detected via `ChangeHistoryService.OnRecordingFinished` names that are not RBXOS-prefixed plus property-change bursts.

### E.8 Test-runtime injection (never touches production)
- On `role=server` connect for a test run, the daemon sends the runtime library (a versioned `.rbxm` of ModuleScripts: `Telemetry`, `Taps`, `Invariants`, `BotHost`, `Phantom`, `Fuzzer`, `Perception`). The plugin deserializes it into `ServerScriptService.__RBXOS_RUNTIME` **inside the test DataModel only**.
- Clients receive `StarterPlayerScripts.__RBXOS_CLIENT`.
- The Edit DataModel never contains them, so publishing can't leak instrumentation.
- A guard in the runtime refuses to run when `RunService:IsStudio()` is false.

**Remote taps:** on the server, the plugin connects to every `RemoteEvent.OnServerEvent` and records the caller, argument shapes (types, sizes, not raw values unless `capture=full`), rates, and handler errors. For `RemoteFunction` it wraps `OnServerInvoke`: it reads the existing callback reference where Studio permits, otherwise it records only through game-side `Telemetry` hooks if the project opts in. ⚠ VERIFY whether plugins can read `OnServerInvoke`. If they cannot, RemoteFunction metrics come from client-side invoke timing.

---

## W. Example tool definitions (conceptual JSON Schema, abbreviated)

```json
{
  "name": "search",
  "description": "Find where something happens in the project. Returns an architecture slice (systems, modules, functions, remotes, instances, line ranges) ranked by relevance. Prefer this over reading files.",
  "annotations": {"readOnlyHint": true},
  "inputSchema": {
    "type": "object", "required": ["query"],
    "properties": {
      "query": {"type": "string", "description": "Natural language or symbol, e.g. 'where is player death handled'"},
      "scope": {"enum": ["project", "server", "client", "shared", "ui", "system"], "default": "project"},
      "system": {"type": "string"},
      "include_runtime": {"type": "boolean", "default": true, "description": "Use recorded runtime traces to rank"},
      "max_items": {"type": "integer", "default": 12, "maximum": 40}
    }
  }
}
```

```json
{
  "name": "changeset_begin",
  "description": "Start an attributable group of changes (files + DataModel). A checkpoint is taken automatically. All subsequent mutations are journaled to this changeset until commit.",
  "annotations": {"readOnlyHint": false, "idempotentHint": true},
  "inputSchema": {
    "type": "object", "required": ["title", "intent"],
    "properties": {
      "title": {"type": "string"},
      "intent": {"type": "string", "description": "Why — the player-facing or technical goal"},
      "systems": {"type": "array", "items": {"type": "string"}},
      "risk": {"enum": ["low", "medium", "high"]},
      "idempotency_key": {"type": "string"}
    }
  }
}
```

```json
{
  "name": "mp_session",
  "description": "Run a multiplayer test session in Studio with 1–8 real clients, optional staggered joins/leaves, network emulation, bots, invariants and fuzzing. Returns job_id; results summarize failures with repro seeds.",
  "annotations": {"readOnlyHint": false, "destructiveHint": false, "openWorldHint": false},
  "inputSchema": {
    "type": "object", "required": ["clients"],
    "properties": {
      "clients": {"type": "integer", "minimum": 1, "maximum": 8},
      "timeline": {"type": "array", "items": {"type": "object", "properties": {
          "t": {"type": "number"}, "action": {"enum": ["add_players", "remove_client", "set_network", "event", "assert"]},
          "args": {"type": "object"}}}},
      "network": {"$ref": "#/defs/NetworkProfile"},
      "bots": {"type": "object", "properties": {"population": {"type": "string"}, "per_client": {"type": "boolean"}}},
      "phantoms": {"type": "integer", "default": 0, "description": "Server-side synthetic players for load (no real client)"},
      "invariants": {"type": "array", "items": {"type": "string"}, "description": "Invariant ids from .rbxos/invariants/"},
      "fuzz": {"type": "object", "properties": {"remotes": {"type": "array", "items": {"type": "string"}}, "intensity": {"enum": ["light", "standard", "aggressive"]}}},
      "duration_s": {"type": "number", "default": 90, "maximum": 900},
      "seed": {"type": "integer"},
      "repeat": {"type": "integer", "default": 1, "maximum": 50}
    }
  }
}
```

```json
{
  "name": "visual_compare",
  "description": "Capture defined shots (camera + lighting + device presets) and compare against a baseline version. Deterministic UI-geometry checks run first; returns only regressions, with a tiled before/after image for flagged shots.",
  "annotations": {"readOnlyHint": true},
  "inputSchema": {
    "type": "object",
    "properties": {
      "shots": {"type": "array", "items": {"type": "string"}, "description": "Shot ids from .rbxos/shots.yaml, or 'all'"},
      "devices": {"type": "array", "items": {"type": "string"}, "default": ["desktop-1080p", "phone-portrait", "tablet-landscape"]},
      "baseline": {"type": "string", "description": "checkpoint id or 'last-accepted'"},
      "ssim_threshold": {"type": "number", "default": 0.97},
      "return_images": {"enum": ["none", "flagged", "all"], "default": "flagged"}
    }
  }
}
```

```json
{
  "name": "experiment_create",
  "description": "Pre-register a design experiment. Hypothesis, predicted observable effects and falsification criteria are required BEFORE any run. Variants are config-key values (ConfigService), so the same experiment can run in simulation and live.",
  "inputSchema": {
    "type": "object", "required": ["hypothesis", "predictions", "variants", "evidence_tier"],
    "properties": {
      "hypothesis": {"type": "string"},
      "mechanism": {"type": "string", "description": "Why the change should cause the effect"},
      "predictions": {"type": "array", "items": {"$ref": "#/defs/Prediction"}},
      "falsified_if": {"type": "string"},
      "variants": {"type": "array", "minItems": 2, "items": {"type": "object", "properties": {
          "name": {"type": "string"}, "baseline": {"type": "boolean"}, "config": {"type": "object"}}}},
      "evidence_tier": {"enum": ["bots", "personas", "live"]},
      "population": {"type": "string"},
      "budget": {"type": "object", "properties": {"max_tokens": {"type": "integer"}, "max_minutes": {"type": "integer"}}}
    }
  }
}
```

```json
{
  "name": "rollback",
  "description": "Restore project state to a checkpoint (files via git shadow ref + DataModel via snapshot). Only agent-attributed changes after the checkpoint are reverted; detected human edits cause a confirmation request listing them.",
  "annotations": {"destructiveHint": true},
  "inputSchema": {
    "type": "object", "required": ["to"],
    "properties": {
      "to": {"type": "string", "description": "checkpoint id | changeset id (restores state before it) | 'last-green'"},
      "scope": {"enum": ["all", "files", "datamodel"], "default": "all"},
      "reason": {"type": "string"},
      "record_failed_approach": {"type": "boolean", "default": true}
    }
  }
}
```

Other key tools follow the same patterns:
- `test_run {level, targets, seed, repeat}`
- `perf_profile {scenario, duration_s, sides, budgets}`
- `fuzz_remotes {remotes, intensity, invariants}`
- `decision_record {title, context, decision, rejected[], reopen_if[]}`
- `knowledge_lookup {concept|api_member|question, depth}`
- `cloud_publish {target: staging|production, version_note}` (PUBLISH_* tier plus confirmation)
- `task_report {}` returns the gate deltas, changesets, evidence collected, unresolved items, and token usage.
