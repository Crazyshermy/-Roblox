# NPC and enemy AI

Read this when building enemies, companions, monsters, crowds or hordes.

## Authority and cost
- AI decisions run on the **server** (anti-cheat, consistency). Clients only present (animation polish, VFX, sound).
- Give gameplay NPCs server ownership: `BasePart:SetNetworkOwner(nil)` on the root. Otherwise the engine may hand physics to a nearby player's client, which causes jitter at ownership changes and lets an exploiter control the NPC.
- **Tick budget:** don't run one `while true` loop per NPC. Use one manager on `Heartbeat` that updates NPCs round-robin, with perception at 5–10 Hz and decisions slower (E3). Scale the tick rate by distance to the nearest player, and sleep NPCs nobody can see.
- **Hordes** (dozens or hundreds): drop Humanoids. Move CFrame-driven or anchored models along precomputed paths on the server, replicate compact state, and let clients interpolate and animate. Pool models instead of creating and destroying them. See the performance skill.

## Behavior structure
- Use an explicit **state machine** (Idle → Patrol → Suspicious → Chase → Search → Return) with entry and exit actions, kept in one module per NPC type. Avoid scattered booleans. For complex agents, a small behavior tree or utility scoring is fine. Pick one style per project.
- **Perception** is a server raycast within a vision cone and range, from eye height, using `RaycastParams` that ignore the NPC itself, plus hearing (events with positions, not polling). Add memory: the last known position decays over time. That makes stealth and horror readable.
- **Telegraph intent.** Show state changes to players (sound sting, animation, light) before the dangerous action. Fairness comes from readable states, not from hidden dice rolls.

## Pathfinding (`PathfindingService`, E4)
- Create with agent parameters that match the NPC's real size and abilities: `CreatePath({AgentRadius = …, AgentHeight = …, AgentCanJump = …, AgentCanClimb = …, WaypointSpacing = …, Costs = {…}})`. A mismatch causes "path found but the NPC gets stuck".
- `path:ComputeAsync(start, goal)` yields and can error, so wrap it in `pcall`. Check `path.Status`. Values other than `Enum.PathStatus.Success` (`NoPath`, `ClosestNoPath`, `ClosestOutOfRange`, …) need a fallback: wait and retry, move to the closest reachable point, or change state.
- Follow `path:GetWaypoints()` one at a time. Handle `Enum.PathWaypointAction.Jump`. **`Humanoid:MoveTo` times out after 8 seconds** if the goal isn't reached (E4), so re-issue for long legs and treat repeated timeouts as "stuck" (recompute or teleport-unstick).
- Listen to `path.Blocked` (a dynamic obstacle appeared on the remaining route) and recompute. Recompute when the target moves more than a threshold, not every frame. Rate-limit `ComputeAsync` per NPC.
- Shape navigation with `PathfindingModifier` (area costs, passable doors) and `PathfindingLink` (ladders, jumps, teleporters), not by adding hacks to the AI code.
- Chasing a player: path to their position at a capped rate, and switch to direct `MoveTo` when there's line of sight within a short range. This avoids the "zig-zag on recompute" look.

## Multiplayer and edge cases
Choose and record the target-selection rule (nearest, threat, last attacker). Handle the target leaving, dying or respawning (clear references on `CharacterRemoving`), the NPC being streamed out on clients (state lives on the server), and NPCs in parts of the map with no players (sleep them).

## Verify
Watch paths in Studio (Show Navigation Mesh, waypoint debug parts), and test the stuck cases: doorways, stairs, dynamic obstacles, unreachable targets. Test with 2+ clients so target switching and ownership behave. Measure server frame time with the expected NPC count.
