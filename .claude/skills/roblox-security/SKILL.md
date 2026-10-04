---
name: roblox-security
description: "Load BEFORE answering whether Roblox code is safe or exploitable, and before writing or reviewing any RemoteEvent/RemoteFunction handler, value grant, spend, trade or purchase, or inserted free model. Roblox exploit-resistance checklist: validation, server authority, dupes, rate limits, malformed input, movement exploits, text filtering, backdoors."
---

# Roblox security

**Threat model.** Assume every client runs an exploit executor. It can fire any remote with any arguments at any rate, in any order, from any game state. It can read every replicated instance and every client script. It can move its own character and any part it has network ownership of. Through those parts it can also replicate NaN/huge CFrames and velocities to **fling other players**, and forge or suppress `Touched`. It **cannot** run server code or read ServerStorage/ServerScriptService.

Classify each finding by required capability:
- **UI-reachable:** a normal player can do it. That is a design bug, and the most embarrassing kind.
- **Modified client:** that is a security bug.
- **Theoretical:** you couldn't construct an exploit. Say so.

## Remote handler contract (apply to every client→server remote)
1. **Shape:** check `typeof` for every argument. Reject extra or missing args, `NaN` (`x ~= x`), `±inf` (`math.abs(x) == math.huge`), non-integers where integers are expected, absurd string lengths, and tables when you expected scalars. If you do accept tables, bound their depth and size and validate every key. Non-string keys and mixed tables don't survive remote serialization intact.
2. **Identity:** the first parameter (`player`) is the only trusted identity. Never accept a player, userId or "owner" argument from the client as authority.
3. **Authority:** re-derive everything from server state. The client says *what it wants to do*, never *what happened*. "Buy item X" is fine, and the server decides price, affordability and grant. "I hit Y for 50 damage" is not fine, and the server decides the hit and the damage.
4. **Preconditions:** check that the player **owns, unlocked or equipped** the ability, tool or item named, and that they are alive, in range (server positions, with tolerance for latency), off cooldown (server clock), owns the item, is in the right game state and round, and that the target exists and is valid (`IsDescendantOf(workspace)`, not destroyed, not another player's private object).
5. **Rate:** apply a per-player, per-action budget (token bucket). The engine throttle is about 500 calls/s **per client, shared across all RemoteEvents together** (not per remote; E4). It is a network safeguard, not a game-logic rate limit.
6. **Atomicity:** do check-and-mutate without yielding between the check and the write. A yield (DataStore call, `task.wait`, `WaitForChild`) between "has 100 gold" and "subtract 100" is a duplication window. Use a per-player lock or busy flag for multi-step operations.
7. **Failure:** reject quietly, never error on bad input, and log anomalies server-side (a counter, not output spam). Don't kick on the first anomaly, because lag produces false positives.
8. **RemoteFunctions:** client→server `InvokeServer` is fine for requests, as long as the handler validates like any remote. Server→client `InvokeClient` is the danger: a client can hang the server thread forever, or error it. Use a RemoteEvent for server→client, or wrap the invoke in a timeout design.

## Value systems (currency, items, trades, rewards, purchases)
- **Round against the player** whenever converting or scaling value (charge with `math.ceil`, grant with `math.floor`, clamp to the balance). Rounding in the player's favor, repeated, is a free-resource exploit.
- **One writer.** A single server module owns each value type, and all grants and spends go through it. Grep for any other write path. Flag every `leaderstats` value written from multiple places, and never treat a `leaderstats` value as the source of truth.
- **Duplication vectors to check:** a yield between check and write; rejoining or server-hopping during an unsaved trade; two servers holding the same profile (no session lock → see `roblox-data`); replaying a reward remote; claiming the same quest twice in the same frame; dropping an item and leaving before the drop is saved; trading while a purchase is pending.
- **Trades:** gate trading of Robux-purchased items on `GetPolicyInfoForPlayerAsync().IsPaidItemTradingAllowed` for **both** players. Lock both inventories, take server-side snapshots, have both parties confirm the *final* offer (any change resets confirmation), re-validate ownership at commit, commit atomically, and keep an audit log. Cross-server trades need a durable intermediary (see `roblox-data`).
- **Purchases:** `MarketplaceService.ProcessReceipt` is idempotent on `PurchaseId`. Return `PurchaseGranted` **only after** the grant is durably saved, otherwise return `NotProcessedYet`. Record processed IDs in the player's data. Paid random items must respect `PolicyService:GetPolicyInfoForPlayerAsync()` (`ArePaidRandomItemsRestricted`).
- **Economy abuse beyond exploits:** look for farmable AFK loops, alt-account funneling, arbitrage between shops, reward stacking, and negative-price or overflow edges. A design that pays for repetition invites bots.

## Movement and physics
- A client owns its character's physics. Speed, fly, teleport and noclip are all possible unless you use **Server Authority mode** (`Workspace.AuthorityMode = Server`; see `roblox/references/currency.md`), which blocks physics exploits through prediction and rollback. Even then, **validate every `InputAction` value inside the bound simulation** (move vector magnitude ≤ 1, fire rate, aim delta), and remember it does nothing against aimbots or ESP. Without it, follow the official approach: leaky-bucket movement accumulators (project onto XZ for speed; handle vertical separately), raycast for walls on large deltas, and **explicit exemptions for legitimate teleports, vehicles and knockback** (the usual cause of false positives). Reject NaN or huge character velocities. Use player-vs-player collision groups where the design allows, to blunt flinging. Correct the player rather than instantly banning them.
- Don't give clients network ownership of value-bearing or shared-gameplay parts (`SetNetworkOwner(nil)` for those).
- Touch- and proximity-based rewards must be validated server-side by distance and state. Clients can fire `Touched` against anything they own.

## Content and supply chain
- **Free models and Creator Store assets:** before insertion, scan for scripts, `require(<number>)`, `getfenv`/`setfenv`, `loadstring`, string-obfuscated code (`\x`, long `string.char` chains, `string.reverse` tricks), `MarketplaceService:PromptPurchase` calls, `HttpService`, and hidden `Script`s nested in meshes or parts. Insert into an empty place first. Script capabilities (`Sandboxed`, experimental) can contain untrusted models.
- **Text:** user-authored text shown to others (signs, names, pet names, notes) must be filtered via `TextService:FilterStringAsync`. Filter per recipient context where required. `TextChatService` filters chat itself.
- Never put secrets in replicated locations or client scripts. Use `HttpService:GetSecret` on the server.

## Reviewing existing code
Report findings **ranked by severity** (critical → low). For each, give the exploit in one line (which call, which args, what the attacker gains) and the capability class (UI-reachable, modified client, or theoretical). Then give a corrected handler that is a drop-in replacement for the user's code and keeps its intended behavior.

## Verify
- Write the **attack list** for the feature: for each remote, give 3–6 malicious calls and the expected server response. Use `references/fuzz-checklist.md`.
- If Studio is connected, simulate the exploit in a playtest with `execute_luau` in the Client DataModel (fire the remote with malicious args), then check server state and console output. Report findings as reproduced (E5) or theoretical.
- See `references/secure-remote-pattern.md` for a compact validated-remote skeleton (load it only when you're writing handlers).
