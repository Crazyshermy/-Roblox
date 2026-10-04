# Action: FPS, fighting, battle royale, racing, sports

## FPS / shooters
- **Fantasy:** precision and dominance under pressure. **Loop:** position → engage → outplay → reposition. Match and round loops sit on top.
- **Keep:** responsive aim (client-side camera and recoil), clear hit confirmation, readable time-to-kill, map sightlines with cover rhythm. **Safe to break:** loadout grind; generic deathmatch-only modes.
- **Failure:** server-delayed hit feedback (feels mushy), hitscan trust exploits, spawn killing, mobile players unable to compete with mouse users.
- **Roblox:** client predicts shots for feel; server validates (origin near character, fire rate, ammo, line of sight with latency tolerance). Consider **Server Authority mode** for movement fairness. Provide mobile aim assist or separate input-based queues. See `roblox-networking`, `roblox-game-feel`.

## Fighting / melee combat
- **Fantasy:** mastery of timing and reads. **Keep:** anticipation → active → recovery frames, hitstop, readable telegraphs, counterplay to every option. **Failure:** spam-optimal (no recovery cost), invisible hitboxes, latency making blocks feel random.
- **Roblox:** server-side hitboxes (spatial queries such as `GetPartBoundsInBox`/`Shapecast` at the active frame) with client-predicted VFX. Telegraph windows must exceed typical latency (~100–250 ms round trip on mobile, E3).

## Battle royale / survival-PvP
- **Keep:** a shrinking pressure source, loot readability, comeback potential. **Failure:** long downtime after death (needs spectating or a quick requeue), lobby waits with low server populations, so support small-lobby modes.

## Racing
- **Fantasy:** speed and mastery of lines. **Keep:** strong speed feedback (FOV, camera shake, wind and particles), forgiving collisions, catch-up tuned subtly. **Failure:** physics jitter of other cars (interpolation or Server Authority with input replication via attributes), ownership-based cheating. Official Server Authority racing template exists (E4).

## Sports
- **Keep:** a shared, predictable ball; clear roles. The ball is the hardest netcode problem; Server Authority with position smoothing is the current official path (Soccer template, E4).
