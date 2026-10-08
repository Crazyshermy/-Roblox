---
name: roblox-data
description: "Use for anything Roblox saves, loads, purchases or shares across servers, and for lost or duplicated progress. Covers DataStore player data (session locking, UpdateAsync, budgets, migrations, BindToClose), purchase receipts, MemoryStore, MessagingService, TeleportService and leaderboards."
---

# Roblox data and cross-server services

Data loss and duplication are the most damaging bugs a Roblox game can ship. Both are usually caused by **concurrency**, not by syntax. Current limits are in `${CLAUDE_SKILL_DIR}/../roblox/references/currency.md`. The budgets changed in 2026, so don't quote old numbers.

## Choose the store
| Data | Store |
|---|---|
| Player progress, inventory, settings | **DataStore**, one profile key per player (split by access pattern only if near limits) |
| Leaderboards | `OrderedDataStore` (periodic writes, cached reads) |
| Ephemeral, shared, fast: matchmaking queues (queue or sorted map), live events, server lists and counters (hash map, avoiding one hot sorted map), cross-server trade escrow | **MemoryStore** (sorted maps and queues; everything expires ≤ 45 days) |
| Fire-and-forget cross-server notifications (announcements, "refresh your cache") | **MessagingService**, which is **best effort, so never use it for value** |
| Moving players between places and servers | **TeleportService** (`TeleportAsync` with `TeleportOptions`, reserved servers via `ReserveServer` or the options) |

## Player data: the non-negotiables
1. **Session locking.** Only one server may own a player's profile at a time. Without it, a fast server hop lets server A save stale data over server B's, which causes rollbacks and dupes. Use the project's existing profile library if there is one (e.g. ProfileStore). Otherwise implement a lock via `UpdateAsync` with a GUID, an expiry timestamp, and a **refresh on every autosave**. A server that finds its lock taken must stop writing (official pattern: `creator-docs: cloud-services/data-stores/player-data-purchasing.md`). Don't hand-roll a third approach if the project already has one.
2. **`UpdateAsync` for read-modify-write.** `SetAsync` blindly overwrites. The `UpdateAsync` transform must be pure: it may run multiple times, must not yield, and may return `nil` to cancel.
3. **Load before play.** Don't let a player act or earn before their data has loaded. If loading fails after retries, **never** start fresh with defaults that later overwrite real data. Either kick with a clear message, or let them play with saving disabled for that session and tell them. This is the #1 data-wipe pattern. `GetDataStore` itself throws in an unpublished place or with Studio API access off. Call it inside `pcall` and run with saving disabled, not at module load where the throw takes down the whole server boot (seen in live Studio, 2026-10).
4. **Save points:** autosave on an interval (respecting budgets), on `PlayerRemoving`, and in `game:BindToClose` (which has ~30 s; save all players in parallel with `task.spawn` and wait). Don't save on every change.
5. **Save serialization:** keep one save in flight per player, and **queue** (coalesce) a save requested meanwhile, never drop it. The final save on leave or shutdown, which releases the session lock, must always run after any in-flight save.
6. **Retries:** wrap calls in `pcall` with exponential backoff and a cap. Check `DataStoreService:GetRequestBudgetForRequestType` before bursts.
7. **Schema version** field in every profile. Write migrations as pure functions `vN → vN+1`, run them on load, test them against fixture snapshots of old data, and never delete fields in the same release that stops using them.
8. **Store canonical state, not derived or UI state.** Serialize only JSON-safe values (no Instances, no non-string dictionary keys, no NaN/inf). Size-check against the 4,194,304-char limit for unbounded collections (logs, inventories).
9. **Studio caution:** with "Enable Studio Access to API Services" on, Studio playtests hit **real** DataStores. Use a separate test place or universe, or a dev-scoped store name, for destructive tests. A solo playtest runs as the developer's own account, so a UserId-keyed store reads and writes their real record. `StudioTestService` test clients have negative UserIds (`-1`, `-2`, …), so their records are easy to find and delete after testing. Data-safety test techniques are in `roblox-testing`.

## Purchases
`ProcessReceipt`: there is **no time-based retry**. It re-fires only when the player buys again or rejoins, and a rejoin fires before their data loads. So if the player is in the server, **yield until their profile loads** (the callback has no timeout), and return `NotProcessedYet` only if they left or loading failed. The callback can run on two servers at once, which the session lock makes safe. Exactly **one** script may set `ProcessReceipt`. Like any callback, a second assignment silently replaces the first (E3; documented for Bindable/RemoteFunction callbacks), so route every product through one handler table. Never grant from `PromptProductPurchaseFinished`, which the docs explicitly forbid (E4). If `PurchaseId` is already in their processed list, return `PurchaseGranted`. Otherwise grant, record the `PurchaseId`, **save**, and only then return `PurchaseGranted`. Bound the processed-ID list (keep recent IDs). Game passes: check `UserOwnsGamePassAsync` (cached) plus `PromptGamePassPurchaseFinished`, and never trust the client's claim.

## Cross-server patterns
- **Global trade or mail:** escrow through a durable store (DataStore record or MemoryStore with a durable fallback), with idempotent claim IDs. MessagingService only *nudges* the recipient's server to check.
- **Matchmaking:** MemoryStore queue or sorted map → `ReserveServer` → `TeleportAsync`. Handle teleport failure (`TeleportInitFailed`) with retry, and return players to the lobby on final failure.
- **Teleport data:** `TeleportOptions:SetTeleportData` is **client-visible and client-tamperable**. Never put value or authority in it. Re-load from the DataStore on arrival, and make sure the source server's save finished first (session lock release) before the destination loads.

## Debugging data bugs
Ask: Can two servers hold this profile? Is there a yield between check and write? Can a save run before the load finished? Does `BindToClose` cover shutdown? Do Studio and live share the store? Did a migration run twice? Reproduce with two Studio sessions or a forced rejoin. Use the DataStores Manager and versioning (`ListVersionsAsync`, `GetVersionAtTimeAsync`) to inspect and restore.
