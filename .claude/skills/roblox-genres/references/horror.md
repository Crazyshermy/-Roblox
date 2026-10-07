# Horror, psychological horror, mystery, stealth

## Horror
- **Fantasy:** vulnerability. Surviving something you don't fully understand.
- **Loop:** explore → cue (sound, light, trace) → dread → encounter or false alarm → escape or hide → relief → escalate.
- **Keep:** anticipation outweighs the reveal; downtime between peaks (tension needs release); a readable threat language (the player learns tells); limited resources (light, stamina, safe rooms).
- **Safe to break:** "monster chases you down a corridor" as the main beat; jump-scare density; the multiplayer-equals-less-scary assumption (separation mechanics can restore fear).
- **Failure modes:** an overexposed monster (seen too often, so no longer scary); constant tension (numbness); random scares (players stop reading cues); darkness used as difficulty (players crank brightness or quit, especially on mobile); groups of friends trivializing fear.
- **Roblox:** use client-local effects for *per-player realities* (one player sees the figure, the other doesn't), spatial audio as a primary fear carrier: with the wired Audio API, `AcousticSimulationEnabled` on emitter and listener muffles sound through walls and bends it around corners, so players can *locate* a threat by ear, `Atmosphere` density with careful exposure (not pitch black), and AI-director pacing on the server. Mobile screens are small and bright, so test readability. Friends often play together, so design separation (split objectives, proximity voice, isolated rooms).

## Psychological horror
- **Fantasy:** distrust of your own perception or of reality.
- **Tools:** environmental changes when unobserved (check the camera frustum on the client), unreliable UI or narration, slow-burn wrongness, consequences that reference player behavior. Client-local divergence between players is a uniquely strong Roblox-multiplayer tool ("did you see that?").
- **Failure:** randomness without meaning. Wrongness must form a pattern the player can start to decode.

## Mystery
- **Fantasy:** being the clever one. **Loop:** gather clues → form theory → test → reveal.
- **Keep:** fair play (the solution is reachable from shown clues); multiple clue paths. **Failure:** pixel-hunting; one missing clue blocks everything; multiplayer where one player solves it for everyone. Give roles or split clues.

## Stealth
- **Fantasy:** control through information. **Keep:** readable detection states (unaware → suspicious → alert), consistent perception rules, recoverable mistakes. **Failure:** opaque AI vision; instant fail on detection.
- **Roblox:** server-side perception (raycasts plus vision cone on a throttled tick), with client-side presentation of the detection meter. Latency makes "spotted at the corner" disputes common, so add grace windows.
