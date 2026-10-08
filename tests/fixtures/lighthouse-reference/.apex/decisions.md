# Decisions

Settled decisions override generic best practice. To reopen one, cite new evidence or meet its reopen condition.

<!-- Template:
## D-001: <title>  (YYYY-MM-DD, status: accepted)
- Context: <why a decision was needed>
- Decision: <what was chosen>
- Rejected: <alternative> (reason); <alternative> (reason)
- Consequences: <trade-offs accepted>
- Reopen if: <condition>
-->

## D-001: Rojo file tree is the source of truth  (2026-10-07, status: accepted (inferred))
- Context: Scripts, remotes and the test world are all declared in `default.project.json`.
- Decision: Edit files under `src/` and the project file; sync to Studio with `rojo serve`.
- Consequences: Edits made directly in Studio to Rojo-managed instances will be overwritten on sync.
- Reopen if: the team moves to Script Sync or Studio-only editing.

## D-002: Server-authoritative refuel  (2026-10-07, status: accepted; range confirmed by user 2026-10-07)
- Context: The original `RefuelLamp` handler trusted a client-sent amount, which allowed negative-amount oil gains and over-spending.
- Decision: The client fires `RefuelLamp` with **no arguments**. The server requires: no extra args, a 0.5s per-player cooldown, a living character, loaded data, oil > 0, and being within `Config.RefuelRange` (20 studs, measured horizontally) of the lamp. It uses only as much oil as the lamp has room for.
- Rejected: client-sent amount with validation (no benefit; the server already knows the oil); ProximityPrompt in place of the remote (larger change).
- Consequences: Refueling from anywhere on the map is no longer possible. The user confirmed the 20-stud server-enforced range is intended.
- Reopen if: the design wants refueling from a distance, or the lamp gets a tower or another access point.
- Note (2026-10-07): the lamp now sits on a 4×27×4 `Tower` part, which meets the "lamp gets a tower" reopen condition. The user deliberately kept the range unchanged: still 20 studs measured horizontally from the lamp, so players refuel standing on the ground around the tower. Reopen if the tower becomes climbable or the lamp gets a gallery/access point.

## D-003: Player data degrades to "no saving" instead of failing  (2026-10-07, status: accepted (inferred))
- Context: `GetDataStore` throws in unpublished places, which used to crash the whole server boot.
- Decision: If DataStores are unavailable, or a player's load fails after 3 tries, that player plays with saving disabled. Saving is one `UpdateAsync` per player on leave or `BindToClose`.
- Consequences: No session locking or autosave yet (see `debt.md`). Players aren't told when saving is disabled.
- Reopen if: the place is published or more value types are added. Then move to session-locked profiles.
- Note (2026-10-07): **the "published" reopen condition is now met** (private experience; PlaceId omitted from this public copy). Real save/load, the failed-load no-overwrite guard and `UpdateAsync` merging were verified live. Session locking is still not implemented; under D-005 it stays in `debt.md` unless a data test needs it.

## D-004: Refuel input via ContextActionService  (2026-10-07, status: accepted (inferred))
- Decision: `ContextActionService` binding with keyboard E, gamepad ButtonX, and an on-screen touch button.
- Consequences: Touch and gamepad paths haven't been tested. Desktop is the primary test target; keep gamepad and touch where practical.
- Reopen if: the project adopts the Input Action System, or target devices change.

## D-005: Lighthouse Keeper stays a small test fixture  (2026-10-07, status: accepted, user decision)
- Context: The project validates Roblox Apex, Claude Code, Rojo and Studio MCP. It is not a game to ship.
- Decision: Fix identified bugs, but don't add systems. The fixture must stay small, easy to understand, easy to reset, and useful for testing networking, security, UI, data handling and Studio playtesting.
- Rejected: building out the dangerous-night system or other major gameplay (scope growth would make it a worse test fixture).
- Consequences: Publishing-grade work (session locking, autosave) stays in `debt.md` unless a test specifically needs it.
- Reopen if: the user specifically requests a new system.

## D-006: Players spawn at a SpawnLocation away from the lamp  (2026-10-07, status: accepted, user decision)
- Context: With no SpawnLocation, players spawned on top of the lamp, already in refuel range.
- Decision: A SpawnLocation on the ground 30 studs from the lamp, outside the 20-stud refuel range, so players walk to the lamp normally. Declared in `default.project.json`.
- Reopen if: the world layout changes.
- Note (2026-10-07): enlarged from 6×6 to **12×1×12** (explicit `CFrame`) after two players spawned stacked. Its nearest edge is 24 studs from the lamp, still outside refuel range.
