---
name: roblox-genres
description: "Genre intelligence: fantasies, loops, conventions to keep or break, failure modes and Roblox constraints for horror, FPS, fighting, RPG, MMO, survival, sandbox, simulator, tycoon, strategy, tower defense, social, racing, puzzle, obby, mystery, stealth, and hybrids."
---

# Genre intelligence

Genres are **player expectation contracts**. Know which expectations to honor (so players feel competent) and which to break (so the game has identity). Breaking a convention is a design choice: name it and give it a reason.

## Procedure
1. Identify the genre(s) and read **only** the matching card file:
   - `references/horror.md`: horror, psychological horror, mystery, stealth
   - `references/action.md`: FPS/shooter, fighting/combat, battle royale, racing, sports
   - `references/systems.md`: simulator, tycoon, sandbox, survival, simulation, strategy, tower defense
   - `references/adventure.md`: RPG, MMO-style, adventure, puzzle, platformer/obby
   - `references/social.md`: social/hangout, roleplay, party games, social deduction
2. Extract: the fantasy the genre promises, the loops, the **conventions to keep**, the **conventions safe to break**, the **failure modes**, and the Roblox constraints.
3. For **hybrids**, find where the genres' needs **conflict** and design the resolution *through mechanics*. Example: horror needs isolation and social deduction needs communication, so proximity-limited voice or chat creates isolation through the rules. Example: tycoon's idle accumulation vs survival's scarcity becomes a base that produces only while defended.
4. Pass the result to `roblox-game-design` reasoning. Genre knowledge informs the design; it doesn't dictate it.

## Roblox-wide genre realities (E3)
- The audience is mobile-heavy and skews young. Many sessions start with friends. Average sessions are shorter than on PC/console, so first-session clarity outweighs depth that unlocks at hour 3.
- Server sizes are often small (many games run with fewer than 30 players per server), and matchmaking is shallow outside top games. Design modes that work with **2 players** and with **full servers**.
- Players arrive mid-session through friend-joins, so the join-in-progress experience matters in every genre.
- Default avatar, controls and camera are the baseline the game must exceed to feel premium. See `roblox-game-feel` and `roblox-visual-direction`.
