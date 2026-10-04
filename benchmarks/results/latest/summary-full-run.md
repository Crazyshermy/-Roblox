# Benchmark 20261004-042434
Subject model: sonnet · judge: opus · blind pairwise, randomized order

| task | Apex skills used | rubric baseline | rubric apex | winner | apex stale/wrong flags | baseline stale/wrong flags |
|---|---|---|---|---|---|---|
| B01-currency-system | roblox, roblox-security, roblox-data, roblox-networking | 0.92 | 1.00 | apex | 0 | 3 |
| B02-multiplayer-interaction | roblox, roblox-networking, roblox-physics-animation, roblox-security, roblox-game-design | 0.67 | 1.00 | apex | 0 | 3 |
| B03-datastore-debug | roblox, roblox-data | 0.75 | 1.00 | apex | 0 | 2 |
| B04-horror-encounter | roblox, roblox-game-design, roblox-genres, roblox-level-design | 0.75 | 0.92 | apex | 0 | 0 |
| B05-optimize | roblox, roblox-performance, roblox-genres | 0.83 | 0.92 | apex | 0 | 2 |
| B06-mobile-ui | roblox, roblox-ui-ux, roblox-genres | 0.75 | 0.92 | apex | 1 | 4 |
| B07-remote-review | roblox, roblox-security, roblox-networking | 1.00 | 1.00 | apex | 1 | 1 |
| B08-progression | roblox, roblox-game-design | 0.50 | 1.00 | apex | 0 | 0 |
| B09-replication-bug | roblox-debugging | 0.83 | 0.83 | baseline | 0 | 1 |
| B10-combat-feel | roblox, roblox-networking, roblox-game-feel, roblox-security | 0.75 | 0.92 | apex | 1 | 3 |

**Wins:** apex 9 · baseline 1 · tie 0
**Mean rubric coverage:** baseline 0.78 · apex 0.95
**Total cost:** $2.96

## Judge reasons
- **B01-currency-system** (apex): Both answers handle authority, validation and atomic spends correctly, but B delegates session locking to ProfileStore and avoids the subtle problems in A's hand-rolled lock, while staying more concise and adding a concrete exploit test list.
- **B02-multiplayer-interaction** (apex): B covers every rubric item more fully: respawn rebinding, client-side grab prediction for responsiveness, explicit concurrency rules, and concrete multi-client testing with Server & Clients and the Network Simulator; it is more elaborate, but A is thinner on latency and testing and has a release bug in its code.
- **B03-datastore-debug** (apex): A's code really does wait for the lock with backoff, migrates existing data, and waits for every save in BindToClose, and it explains how to test the fix; B's lock-wait does not work as described, it breaks existing saves, and it gives no testing advice.
- **B04-horror-encounter** (apex): A forces the group to split with a two-location objective, lets one player see a scare the others don't, and makes the call-bell lure a real co-op choice. Its threat rules are fully learnable and closely tied to the hospital. B has more useful Roblox implementation notes, but it only partly handles group separation, adds randomness that hurts readability, and never covers mobile readability.
- **B05-optimize** (apex): Both cover the same main architectural fixes, but B puts profiling first with a re-profile step, orders the work by payoff, and explicitly protects visual fidelity, while A's extra code and checklist add small inaccuracies without better prioritization.
- **B06-mobile-ui** (apex): B covers server authority and keeps the HUD more minimal with input-agnostic actions, while A misses server trust entirely and depends on a deprecated selection API, even though A's UIScale responsive approach and starter code are stronger.
- **B07-remote-review** (apex): Both answers cover every rubric item with similar server-authoritative fixes. B is slightly stronger: its code also checks that the target is in workspace, it lists what it did not cover (ownership, XP farming against respawning targets, raycast hit validation), and it hedges unverified engine behaviour instead of asserting it, which outweighs its dubious throttle figure.
- **B08-progression** (apex): A ties progression to verbs, regulars and the stand, explicitly rejects rebirths and extra currencies with reasons, and covers sinks, onboarding and testable hypotheses; B mostly reuses simulator defaults like prestige, premium currency, pets and 2x gamepasses.
- **B09-replication-bug** (baseline): B covers the same diagnosis and fix as A and adds concrete remote-side guidance: send the state in the payload, identify the door by a stable ID, look it up with FindFirstChild or WaitForChild with a timeout, and fire only to nearby players. That outweighs its minor misstatement about Atomic mode.
- **B10-combat-feel** (apex): A gets the replication model right: it drops the server swing broadcast instead of keeping a relay, and it puts latency in the wind-up, mentions Server Authority, and uses the Hit marker in its code, while B keeps a relay that plays other players' swings twice and never says to put latency in the wind-up.
