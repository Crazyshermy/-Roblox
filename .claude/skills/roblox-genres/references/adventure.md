# RPG, MMO-style, adventure, puzzle, platformer/obby

## RPG
- **Fantasy:** growth of a character and their place in a world. **Keep:** build choices with trade-offs, a world that reacts, combat or skill expression matching the fantasy. **Break:** generic quest boards ("kill 10 X"). Tie quests to world change or character relationships.
- **Failure:** stat bloat, gear treadmills, empty open worlds.

## MMO-style
- **Keep:** shared world moments (world bosses, events), social roles, persistent identity. **Roblox reality:** per-server player counts are small, so "MMO" means a *shared persistent universe* across servers (MemoryStore events, cross-server messaging, shared economy) rather than thousands in one place. Design around that honestly.
- **Failure:** content consumption outpacing production, economies broken by dupes (see `roblox-security`).

## Adventure
- **Fantasy:** discovery and journey. **Keep:** landmarks, environmental storytelling, set-pieces, pacing that alternates traversal, puzzle, threat and rest. **Failure:** corridor with text boxes; unclear objectives.

## Puzzle
- **Keep:** one idea per puzzle, introduced → developed → twisted. Fair information. **Failure:** obscure logic, multiplayer where one player solves everything (split information across players instead).

## Platformer / obby
- **Fantasy:** mastery of movement. **Keep:** readable hazards, fast respawn near the failure point, difficulty ramps with checkpoints, a movement feel worth mastering. **Break:** default-controller-only obbies. Custom movement (wall jumps, dashes, momentum) creates identity.
- **Failure:** ambiguous jumps (depth perception), mobile-hostile precision, unfair blind jumps. Measure gaps against character metrics (default `JumpHeight` 7.2 studs, `WalkSpeed` 16; verify the project's values). Test every jump on touch controls.
