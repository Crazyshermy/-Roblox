---
name: roblox-luau
description: "Modern Luau for Roblox: types and the new type solver, --!strict, modules, task library, buffer, idioms, Parallel Luau, footguns, legacy-pattern modernization, code-level performance."
---

# Modern Luau (Roblox, 2026)

Write code that a strong Roblox engineer would merge. Follow the project's existing style (naming, OOP style, type strictness) over these defaults.

## Defaults
- `--!strict` for new modules unless the project doesn't use it. Annotate public function signatures and exported types (`export type`). Don't fight inference inside function bodies. Luau's **new type solver** is generally released, so validate type errors against current Studio or luau-lsp, not old forum posts.
- `local Service = game:GetService("Service")` at the top. Never index services by name (`game.Players`) in new code.
- **Task library:** `task.wait`, `task.spawn`, `task.defer`, `task.delay`, `task.cancel`. Treat `wait`, `spawn`, `delay` and `coroutine.wrap` for fire-and-forget as legacy. `task.spawn` propagates errors properly.
- **Iteration:** `for i, v in t do` (generalized iteration). `ipairs`/`pairs` are still fine. Use `table.clear`, `table.create(n)`, `table.move`, `table.find`, `table.freeze` for config and constants.
- **Strings:** use string interpolation `` `Hello {name}` `` and `string.format` for formatting. Use `buffer` for binary packing, which helps compact networking and serialization (byte-level control and smaller payloads).
- **Compound ops:** `+=`, `-=`, `..=`. Use `if x then a else b` expressions instead of `x and a or b` when `a` can be falsy.
- `Instance.new(class)` then set properties, **then** set `Parent` last (it avoids redundant replication and change events).
- Prefer `WaitForChild(name, timeout)` on the client. Don't call `WaitForChild` on the server for things that already exist.
- **Attributes** (`SetAttribute`/`GetAttribute`/`GetAttributeChangedSignal`) over Value objects for new per-instance data.

## Footguns
- **`pcall` scope:** wrap only the yielding or external call, and handle the failure branch explicitly. Don't hide logic bugs inside `pcall`.
- **Connections leak:** every `:Connect` tied to a player, character or round needs a disconnect owner. `Destroy()` disconnects the instance's *own* events only.
- **Yield inside a critical section** (check → yield → write) causes races. See `roblox-security` and `roblox-data`.
- `#t` is undefined for tables with holes. Removing from an array while iterating forward skips elements.
- Comparing floats for equality, and `math.random` without considering `Random.new(seed)` for reproducible logic.
- `tostring(number)` and JSON round-trips: NaN/inf break `JSONEncode`. Integers above 2^53 lose precision.
- Module `require` cycles produce partially-initialized tables. Break them with an init/start split or dependency injection.
- `debug.profilebegin`/`profileend` labels need to be paired, or MicroProfiler output gets confusing.

## Code-level performance (measure first; see `roblox-performance`)
- Cache service and instance references outside hot loops. Avoid `FindFirstChild` chains every frame.
- Avoid per-frame table allocation in hot paths (reuse tables, `table.clear`).
- Use `--!native` (native code generation) only for measured numeric-heavy hot modules. It doesn't help yield-heavy or API-bound code.
- **Parallel Luau:** put work in Actors, use `ConnectParallel` / `task.desynchronize`, and `task.synchronize` before writing to the DataModel. Communicate via `SharedTable` or messages. It's worth it only for independent, CPU-bound work with measurable cost.

## Review lens
Readability > cleverness. A single responsibility per module. No dead code, no global state outside module scope, and early returns for validation. Name things after the game domain, not the implementation.
