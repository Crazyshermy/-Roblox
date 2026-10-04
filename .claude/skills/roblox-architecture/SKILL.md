---
name: roblox-architecture
description: "Roblox code architecture: where scripts and assets live, services and controllers, module boundaries, state ownership, player and character lifecycle, CollectionService components, init order, Rojo vs Script Sync, fitting new systems into existing code."
---

# Roblox architecture

**First, fit the project.** Read the existing structure and `.apex/decisions.md` before proposing anything. A consistent "worse" pattern beats an inconsistent mix of two good ones. Propose a migration only with its cost and a concrete benefit.

## Placement (what can see what)
| Location | Runs or visible to | Put here |
|---|---|---|
| `ServerScriptService` | server only | server Scripts and server-only modules (services, validation, economy, data) |
| `ServerStorage` | server only | server-only assets and templates (loot tables with real odds, NPC templates, maps not yet loaded) |
| `ReplicatedStorage` | both | shared modules (types, constants, pure logic, static catalogs), remotes, client-needed assets |
| `StarterPlayerScripts` / `StarterCharacterScripts` | client | client bootstraps, controllers, per-character client logic |
| `StarterGui` | client (cloned per player) | UI. Disable `ResetOnSpawn` on persistent UI. |
| `Workspace` | both (replicated, streamed) | the world. Scripts here are a smell except deliberate `RunContext` components. |

Anything in `ReplicatedStorage` or `Workspace` is readable by exploiters, so secrets and real odds stay server-side. `Script.RunContext` (`Server`/`Client`/`Legacy`) lets one script type run anywhere. Use it deliberately, not by accident.

## Recommended default (E3; adapt it, don't impose it)
- **One server bootstrap + one client bootstrap** that require services and controllers in an explicit order. Each module exposes `init()` (wire up, no yielding cross-module calls) and `start()` (begin behavior). Explicit order beats implicit `require` side effects.
- **Services (server)** each own one domain (Inventory, Combat, Rounds). A service is the *only* writer of its state, and other code calls its API. **Controllers (client)** own presentation and input for one domain.
- **Shared** modules are pure: types, config, formulas and validation helpers usable on both sides (e.g. "can afford" for UI hints; the server re-checks).
- **Components:** tag instances with CollectionService and attach behavior by tag (`GetInstanceAddedSignal`/`GetInstanceRemovedSignal`, plus handling already-tagged instances, plus cleanup on removal). Streaming makes this the natural client pattern, since instances arrive and leave.
- **State:** each piece of state has exactly one owner. Model rounds, abilities and AI as explicit **state machines** (enum state + transition function) rather than scattered booleans. Replicate state through attributes or values the server sets, so clients render it.
- **Cleanup discipline:** every connection, thread and instance created for a player, round or component has an owner that destroys it (a maid/trove pattern or explicit lists). Leaks are architecture bugs.
- Frameworks (Knit-style, ECS like Matter or jecs) are fine if the project uses them. Don't introduce a framework for a small game. An ECS pays off for many homogeneous simulated entities, not for UI-heavy games.

## Tooling choice
- **Rojo** when the filesystem is the source of truth (git, CI, packages via Wally/pesde, external tooling).
- **Studio Script Sync** (GA 2026) when the project is Studio-first and you just want scripts on disk. It works with Team Create.
- Don't switch a project's toolchain as a side effect of another task.

## Lifecycle checklist (for any new system)
init order and dependencies · existing players and characters at start · join and leave · respawn · round reset · server shutdown (`BindToClose`) · streaming in and out · hot paths and their cost · who can mutate · how it's tested in isolation.

## Scale and ambition
For large or engine-pushing systems, sketch the **authority split** first (server simulation vs client presentation vs precomputed or procedural content), then the data flow, then the module list. Parallel Luau (Actors) suits independent CPU-heavy work (pathing, procedural generation, AI perception). It doesn't make shared-state code faster. See `roblox-luau`.
