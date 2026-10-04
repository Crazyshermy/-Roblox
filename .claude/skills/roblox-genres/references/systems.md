# Systems genres: simulator, tycoon, sandbox, survival, simulation, strategy, tower defense

## Simulator (Roblox-native genre)
- **Fantasy at its best:** becoming absurdly powerful at a *specific, flavorful* activity. **Typical loop:** act → earn → upgrade → reach new zone.
- **Keep:** immediate feedback for actions, visible growth, zone novelty. **Break:** the clicker-plus-pets-plus-eggs-plus-rebirth template. Run the anti-slop protocol. The most distinctive simulators change *how* you act as you progress, not just how much you earn.
- **Failure:** number inflation without new verbs, AFK-optimal play, identical zones with recolors.

## Tycoon
- **Fantasy:** building an empire you can see. **Keep:** spatial growth (the base visibly expands), satisfying build animations, a clear next purchase. **Break:** strict linear button paths. Add layout choice, specialization, or interaction with other players' tycoons.
- **Roblox:** per-plot ownership, server-authoritative purchases, and streaming-friendly plot sizes. Save layout compactly (IDs plus transforms, not instances).

## Sandbox / building
- **Keep:** expressive tools with low friction, sharing and showcasing. **Failure:** griefing (needs ownership and permissions), memory and part-count explosions (needs per-player budgets), save size (compact serialization; budget under the per-key 4 MB/min write throughput, and shard large builds across keys).

## Survival
- **Fantasy:** competence against scarcity. **Keep:** resource pressure, crafting that changes options, day/night or threat cycles. **Failure:** tedious inventory UI on mobile, punishing death that wipes hours, resource farming bots. Death loss needs to be tuned to session length.

## Simulation (vehicles, jobs, life-sim)
- **Keep:** fidelity in the *fantasy-relevant* parts only. **Failure:** realism that adds chores. Choose which details are the fantasy.

## Strategy / tower defense
- **Fantasy:** outthinking the problem. **Keep:** readable enemy and counter relationships, meaningful placement, information before decisions. **Break:** pure stat-upgrade grinds as the only depth. **Failure:** a dominant strategy, unreadable chaos at high waves (perf and visual), co-op where one player carries.
- **Roblox:** many enemies means server-side simulation of positions with client-side rendering (don't use Humanoids for hordes; move with CFrame or lightweight custom movement plus client interpolation), and pooled models. Budget per wave.
