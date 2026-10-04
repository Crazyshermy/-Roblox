---
name: roblox-networking
description: "Use when designing or fixing how Roblox state moves between server and clients, or when multiplayer behaves wrong. Covers remotes vs unreliable remotes vs replicated attributes, Server Authority (prediction, rollback), network ownership, latency hiding, races, join, leave and respawn mid-action, and streaming-safe client code."
---

# Roblox networking and multiplayer

The server owns truth. Clients **request**, **predict** and **present**. Validation rules live in `roblox-security`, and this skill decides *how state flows*.

## Choose the channel
| Need | Use |
|---|---|
| Persistent shared state that late joiners must see (door open, round state, health) | **Server-set properties and attributes** on replicated instances. Replication handles late join. Don't re-send it via remotes. |
| A discrete, must-arrive event (purchase result, ability fired, round end) | `RemoteEvent` (reliable, ordered among RemoteEvents) |
| High-frequency, latest-value-wins data (aim direction, cosmetic positions, VFX cues) | `UnreliableRemoteEvent`. Keep payloads ≤ 1,000 B or they're dropped, and expect loss and reordering. |
| A client asking the server for data | `RemoteFunction` (client→server) is fine. **Never** use server→client `InvokeClient` without a timeout design (see the security contract). |
| Many players and objects, server-authoritative competitive physics (FPS, racing, sports, fighting) | **Server Authority mode**. See below. |

Remotes are **not ordered relative to property and attribute replication**. If a remote references an instance or attribute the server just changed, the client may not have it yet. Send the needed values in the payload, or make the client tolerate a missing instance (wait with a timeout and handle `nil`).

## Server Authority mode (announced for all creators July 2026; young system. APIs E4; read `roblox/references/currency.md`)
Use it when movement or physics fairness matters and you want responsiveness without hand-written netcode. Cost: it requires an architecture change, and it is a young system.
- `Workspace.AuthorityMode = Server` turns on NGR, IAS player scripts, Deferred signals, fixed simulation and streaming.
- Put core gameplay in `RunService:BindToSimulation` in a ModuleScript required on **both** sides. Inputs come through `InputAction`s (`InputContext` under the Player). State lives in attributes on predicted instances, written only inside bound functions. Use `time()` and not `tick()` or `os.clock()`.
- Presentation (VFX, sound, animation reactions) runs in `RenderStepped`, reads simulated state, and must undo mispredicted effects.
- **Design for latency:** use slower acceleration, telegraph fuses before big effects, and put the misprediction on the wind-up rather than the payoff. Other players render slightly in the past unless you replicate their inputs through attributes.
- Retrofitting a large existing codebase is a major migration. Present it as an option with its cost. Don't force it.

## Classic model (no Server Authority)
- **Hit detection and fast actions:** the client predicts locally for feel (animation, VFX, sound) and sends *intent* (e.g. `origin`, `direction`, `timestamp`). The server validates against its own state with latency tolerance (cooldown, range, line of sight, rewind window if needed), then applies the result and broadcasts it. Show damage numbers and kills only on server confirm, or reconcile them.
- **Network ownership:** clients own their character and any unanchored parts the engine assigns to them. Set `SetNetworkOwner(nil)` on shared or gameplay-critical physics. Give a player ownership only of what they alone control (their vehicle), and accept the exploit surface that comes with it.
- **Interpolate other entities.** Don't snap. Server-driven NPCs replicate already. For custom-simulated entities, send snapshots at 10–20 Hz unreliably and interpolate with a ~100 ms buffer (E3).

## Multiplayer correctness checklist (the bugs that ship)
- **Join timing:** handle players and characters that already exist (`for _, p in Players:GetPlayers()` after connecting `PlayerAdded`). Handle `CharacterAdded` firing before your script connects. Late joiners need current state, which replication handles if you used state instead of events.
- **Leave mid-action:** `PlayerRemoving` during a trade, carry, round, vote or save. Clean up locks, held objects and per-player tables (otherwise you get memory leaks and stuck locks).
- **Respawn:** the old `Character`, `Humanoid` and `Animator` references are dead. Rebind on `CharacterAdded`. Tools and connections tied to the old character must be disconnected.
- **Concurrency:** two players act on the same object in the same frame. Decide the arbitration rule (first server-received wins) and make the check-and-mutate atomic (no yield between).
- **Deferred signals** (`SignalBehavior.Deferred` is standard): handlers run later in the frame, not immediately. Don't depend on immediate re-entrancy or on reading state "right after" firing.
- **Streaming** (`StreamingEnabled`): client code must not assume distant instances exist. Use `WaitForChild` with a timeout, `ModelStreamingMode` (Atomic/Persistent) for models the client needs whole, and `Player:RequestStreamAroundAsync` before teleporting the camera or character.
- **Bandwidth:** don't fire per-frame reliable remotes. Batch, delta-compress or send unreliably. Don't replicate huge tables; send IDs and let clients look up static data.

## Verify
A solo playtest doesn't prove multiplayer behavior. Use **Server & Clients** (2–3 clients is usually enough, up to 8) with the Network Simulator adding latency. Test: join mid-round, leave mid-action, respawn mid-action, two clients on the same object, and a high-latency client. Report which of these were actually exercised.
