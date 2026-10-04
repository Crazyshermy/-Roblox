---
name: roblox-debugging
description: "Use for ANY Roblox or Luau error message, bug, crash or unexpected behavior (\"attempt to index nil\", works in Studio but not live, only sometimes, after respawn). Systematic diagnosis with competing hypotheses, plus the common bug classes: replication timing, streaming nil, stale respawn refs, deferred signals, races, DataStore throttling, ownership."
---

# Roblox debugging

**Don't guess-and-patch.** Reproduce → observe → hypothesize (several) → discriminate → fix the root cause → verify → check for siblings of the same bug.

## 1. Pin the symptom
- Where does it fail: **server, client, or both**? (Output shows the source. The F9 Developer Console in a live game has separate client and server logs.)
- Is it deterministic? What exact steps reproduce it? Is it solo or only with other players? Studio only, or live only?
- The first error matters most. Later errors are often cascades.

## 2. Generate competing hypotheses, then discriminate
Write 2–4 plausible causes and **what each predicts differently**, then run the cheapest observation that separates them (a print or `execute_luau` probe, inspecting the instance tree at failure time, a second client). Fix only after a hypothesis survives.

## 3. Roblox bug classes to check (by symptom)
| Symptom | Usual suspects |
|---|---|
| `attempt to index nil` on the client | the instance is not replicated yet or was **streamed out**, so use `WaitForChild` with a timeout or `ModelStreamingMode`; the server deleted or renamed it; client code runs before the character loads |
| Works once, breaks after respawn | cached `Character`, `Humanoid`, `Animator` or `HumanoidRootPart` references, or connections bound to the old character |
| Works in solo, breaks with 2+ players | a shared global instead of per-player state; `LocalPlayer` assumptions in server code; `FireAllClients` vs `FireClient`; race on a shared object |
| Works in Studio, fails live | latency (no local round-trip), real DataStore throttling, streaming at real distances, device performance, `RunService:IsStudio()` branches, API access settings |
| Intermittent or "sometimes" | race between `PlayerAdded`/`CharacterAdded` and your connection; deferred signal ordering; remote vs replication ordering; yields inside critical sections; `task.spawn` ordering assumptions |
| Remote arrives but the instance or state it refers to is `nil` or stale (streaming, ordering) | remotes aren't ordered with replication, and streamed-out instances don't exist on the client. Drive clients from replicated state (`GetAttributeChangedSignal`, CollectionService stream-in), or send the state plus a stable ID (an attribute, not an Instance) in the payload and look it up with a timeout. Fire only to players who need it. |
| Remote "does nothing" | the handler errored silently in a `pcall`; it's connected on the wrong side; RunContext or script placement is wrong (a Script in ReplicatedStorage doesn't run); validation rejected it; the instance arg arrived `nil` because it wasn't replicated to the sender |
| Physics jitter or teleport-back | network ownership flipping (`SetNetworkOwner`), server correcting the client, Server Authority mispredictions (use the visualizer, Ctrl/⌘+Shift+F6) |
| Data lost or rolled back | no session lock; save-before-load; `SetAsync` overwrites; `BindToClose` missing; Studio and live sharing a store. See `roblox-data`. |
| Memory or FPS degrade over time | leaked connections, instances or tables. See `roblox-performance`. |
| Animation not playing or stuck | loaded on the wrong Animator; animation priority or weight conflicts; asset ownership or permissions (animation must be owned by the experience owner/group); cached track after Server Authority rollback |

## 4. Tooling
- Studio MCP: `get_console_output` after `start_stop_play`; `execute_luau` (Server/Client) to read live state at the moment of failure; `script_grep` to find every writer of the broken state; and the `skill` tool `rbx-debug` for Roblox's own debugger guidance.
- In-Studio: breakpoints and the Watch window, `debug.traceback()` in error handlers, Server/Client view toggle, Network Simulator for latency bugs.
- Add **temporary** targeted prints with a unique tag (e.g. `[DBG-trade]`) and remove them after.

## 5. After the fix
Explain the root cause in one sentence. Verify with the original repro (E5 if run). Search for the same pattern elsewhere (`script_grep`). Add a regression test or invariant if the bug class can recur.
