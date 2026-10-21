# Lighthouse Keeper first minute: baseline and player-pass retest (2026-10-17 and 2026-10-21)

**What this is:** two live Roblox Studio sessions that got the same prompt on the same starting state of the Lighthouse fixture.
- **Baseline (2026-10-17):** Apex 1.2.0 (project install).
- **Retest (2026-10-21):** Apex 1.2.0 + roblox-player-pass v1 draft.

The runs also differed in the answer key, the Studio tools and Rojo (see the table below), so **the comparison is suggestive, not proof**. There was one run of each, by one tester.

**Sources:** both session transcripts (tool calls and their results) and each session's final report. The "What each run did" table comes from the reports. Where a line was checked against the transcript, it says so. Account details, IDs, asset IDs, creator names and file paths were left out.

## Prompt (both runs)
> Before changing anything, make a git commit so we can undo everything later.
>
> /roblox Make the first minute of Lighthouse Keeper great for a brand-new player. Do whatever you think is needed, then tell me when it's done. At the end, give me the usual table: verified live / only checked in code / could not test.

## Setup, and what differed besides the skill
| | Baseline (2026-10-17) | Retest (2026-10-21) |
|---|---|---|
| Skills | Apex 1.2.0 (project install) | Apex 1.2.0 + roblox-player-pass v1 draft |
| Which Apex copy loaded | The project's 1.2.0 copy, every time. The 1.4.0 plugin was also enabled at user level, but none of its skills were loaded. The specialists that loaded are byte-identical to 1.4.0. The router and its `studio-mcp.md` are the 1.2.0 versions. | Same, plus the draft skill from the project folder. A claude.ai-synced copy of the draft was also listed in the session, but the project copy is the one that loaded. |
| Specialists loaded | game-design, ui-ux, game-feel, security, review | player-pass, ui-ux, game-design, visual-direction |
| Answer key | **Read.** `lighthouse.FLAWS.md` was in the test folder, and the session printed it while reading the project. The transcript shows this, and the session's report admits it. Its F8 item is a design flaw in this exact loop (darkness has no consequence, refueling has no feel), so it may have steered the design. | **Not present.** It was moved out of the test folder after the baseline, and its deletion was committed before the retest started. No tool call in the retest touched it or a `*-reference` folder. |
| Studio tools | The Studio MCP server was added at the start of the session, so its tools never loaded. Claude wrote its own small MCP client and drove Studio through the shell. It reported this as it went rather than asking first. | The native Studio MCP tools |
| Rojo | Not running. Claude copied script and world changes into Studio with generated scripts, then checked all 9 scripts byte for byte. | Rojo 7.7.1 serving. Sync was checked with `script_grep` before playtests. |
| New skill available? | No. It first appears in that session's skill list after the baseline's final report. | Yes (the v1 draft) |
| Starting state | The fixture's 2026-10-07 end state, unpublished (PlaceId 0), so saving was disabled | Same files, same place |
| Claude Code · model | 2.1.300 · Opus 5.5 (effort not recorded) | 2.1.302 · Opus 5.5 (effort not recorded) |
| Time to final report | about 30 min | about 28 min |
| Studio version | not recorded | not recorded |

## What each run did (from each session's report)
| Area | Baseline | Retest |
|---|---|---|
| Opening shot | Lamp in frame at spawn in 5 of 5 starts. A 4-second title card. | Lamp visible at spawn in all 4 device presets (camera tilted up on the first spawn) |
| Devices | iPhone 7, iPhone 17 Pro and a laptop preset. The transcript shows no tablet or console preset being set. | iPhone 7, iPad 6th gen, Xbox, 1366×768 and 1080p (each preset set is in the transcript) |
| Multiplayer | 2 clients: co-op message, fuel in sync, per-player markers and hints | 2 clients: OIL tags hide for both clients, teammate credit message, funnel counted per player |
| Gamepad | "Press X" hint written. "A real gamepad" listed under could not test. | Xbox preset checked for bindings and setup, plus a simulated X press that refueled. The X glyph itself was only checked in code. |
| Onboarding funnel | None. The transcript has no `LogOnboardingFunnelStepEvent` call. | 5 steps logged on the server. All 5 fired in a Studio playtest across 3 pickups and 2 refuels. |
| First fun | No time given | "~15 s", estimated from walk distances, not timed |
| 10-second test | Not reported | Not reported. The v1 draft had the check but no line for it in the report. |
| Stuck points | Not counted. Fixes listed (reasons shown for "no oil" and "too far", lamp in frame at spawn, …) | 11 found, 11 fixed, no blockers open. One minor item left: the HUD still shows Health. |
| Sounds | Chosen by name, length and measured loudness, not by ear. Listed under could not test. | Two sounds picked without listening: one labeled CC0, one with an unknown license. Both went into the first hand-off item, without saying the unknown license blocks shipping. |
| Clip moment | Not part of the report | Proposed but not built: a rotating beam that shrinks as fuel drains |
| Hand-off | The "could not test" column | 5 numbered items for the tester |
| Design changes | Recorded as D-007 (for example, Health removed from the HUD, the lamp starts half full) | Recorded as D-007 |
| Console at the end | No errors from the game's scripts | No game errors in any console |

## v1 → v2 (shipped as 1.5.0): what changed and why
Each v2 change answers a gap seen in the retest. **None of these changes has been run live yet.**

| v2 change | Retest gap it answers |
|---|---|
| Time first fun with timestamps in one desktop run. Walk-distance estimates don't count. | First fun was "~15 s, estimated from walk distances" |
| A "10-second test" line in the report | The check was in v1 but never reached the report |
| Check who made each sound or model. An unknown license or creator blocks shipping and goes at the top of the hand-off. | A sound with an unknown license only came up inside the sounds item |
| After changing the Rojo project file, read the properties back in Studio (the rule now lives in `roblox-architecture`) | Lighting added mid-session didn't live-sync (below) |

## Rojo observations (retest, Rojo 7.7.1)
- **Lighting didn't live-sync.** A `Lighting` node (properties plus `Atmosphere` and `Sky` children) was added to the project file mid-session while `rojo serve` was connected. It never reached Studio: about 45 s later, `ClockTime` still read 14 and the new children were missing. `rojo build` of the same file did include them. Claude applied the same values with an `execute_luau` edit and asked the tester to reconnect Rojo and check. This was seen once, and the cause is unconfirmed.
- **Parts without children reset to the origin.** Adding `Color` and `Material` to `Baseplate` and `Tower` moved both to (0, 0, 0). Neither part has children, and both were placed with `Position`. Switching them to an explicit `CFrame` put them back. The 2026-10-07 run had seen this reset only on a part with a child.

Both observations are now in `roblox-architecture` → Rojo project-file pitfalls.

## Not verified or still pending
- **The tester's own checks are pending:** listening to the two sounds, and a run with a real controller (the X glyph, and pressing X to refuel). Neither run used real phone or tablet hardware.
- **Fun:** neither run is evidence that the first minute is fun. An AI playthrough only finds blockers.
- **The v2 skill (Apex 1.5.0)** hasn't been run in Studio.
- **One run per arm**, with the differences listed above. The tables come from each session's own report. They were checked against the transcripts for the device presets, the funnel calls and access to the answer key, but not line by line.
- **Funnel data in Creator Hub** needs a published game, and neither run published one.

## Automated checks on the 1.5.0 skill (headless, not Studio evidence)
- **Smoke (Sonnet, 2026-10-21):** "Polish the first minute…" with no `/roblox` prefix routed to `roblox-player-pass` in 2/2 runs. The full suite passed 15/15.
- **B06-mobile-ui benchmark:** Apex 0.83 vs baseline 0.67, and the player-pass skill correctly didn't load for a HUD design question. **The baseline arm had the tester's claude.ai `game-ui-design` skill loaded, so this isn't a comparison against plain Claude.** One sample, judged by a model.
- **P10-mobile-controls** didn't run: the project benchmark's empty config folder hides a subscription login.
