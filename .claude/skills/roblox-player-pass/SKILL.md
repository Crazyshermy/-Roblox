---
name: roblox-player-pass
description: "Play a game's first session as a brand-new player on phone, tablet, console and desktop: stuck points, unclear goals, prompts that don't fire, missing feedback, onboarding funnel steps, a 10-second clarity check. Use for polish, the first minute, tutorials, onboarding, new-player experience, or before shipping."
---

# Player pass

A game can pass every technical check and still lose players in the first minute. Before calling player-facing work done, **play it as a kid who has never seen it**, on every kind of device, and fix what blocks or confuses them.

Where this comes from: a creator with a top-100 Roblox game (2026) said copies of hit games flop mainly from weak polish (broken prompts, unclear UI, developers who never play their own game), and that one of their own AI-built games flopped for having no polish at all. That is one creator's account (E1). Everything below is a procedure, and only what you run in Studio counts as verified.

## When to run it
- After building or changing anything a new player meets in their first ~5 minutes.
- Before saying "done" or "ready to ship" on player-facing work, and when asked to polish the first minute, a tutorial or onboarding.
- Skip it for pure backend work that changes nothing a player sees.

## 0. Preflight
- **Tools:** prefer the Studio MCP tools (`${CLAUDE_SKILL_DIR}/../roblox/references/studio-mcp.md`). If they aren't loaded, tell the user how to load them (restart Claude Code with Studio's MCP server on) before starting. Work around a missing tool only with the user's OK, and say what the workaround can't prove.
- **Sync:** confirm edits reached Studio (Rojo connected, or `script_grep` for a changed line) before any playtest. If you change the Rojo project file itself, read the changed properties back in Studio (`roblox-architecture` → Rojo project-file pitfalls).
- **New-player state:** empty data (a test store, or saving disabled with the reason stated), a fresh character, default settings. A returning player's state hides first-time problems.
- **Don't open answer keys** or files marked test-only (for example `*.FLAWS.md`, `*-reference/`). If you read one by accident, say so in the report.

## 1. Write the target before playing
Three lines, in the report:
- **Fantasy:** what the player is, in one sentence ("You keep a lighthouse lit through the night with friends").
- **First goal:** the one thing the player must do first.
- **First fun:** the moment they first feel the game working, and when it should land (aim for under ~60 s; designer judgment, E1).

## 2. Play the first session on every device
Switch presets from a probe (`roblox-testing` → Live Studio techniques → Devices).

| Run | Preset | Input | Extra checks |
|---|---|---|---|
| Small phone | smallest phone | touch only | thumb zones, nothing under the thumbstick or jump button, text readable |
| Tablet | any tablet | touch only | layout doesn't stretch or float oddly |
| Console | console / 10-ft | gamepad | every action has a gamepad binding, every menu works by selection (`GuiService.SelectedObject`), B closes, button glyphs not key letters, text readable from a couch |
| Desktop | 1080p desktop | keyboard and mouse | key hints match the real keys |

For each run, walk **spawn → first goal → first action → first reward → first failure → recovery.** Take a `screen_capture` at each step. Read `get_console_output` after each run.

**Time it, don't estimate it.** In one desktop run, record timestamps at spawn, first goal done and first fun (a client probe with `os.clock()`, or the game's own funnel calls), moving the character the way a player would. Report the measured seconds. Walk-distance estimates don't count.

Gamepad input can't be fully simulated through the MCP. Check bindings, `ProximityPrompt.GamepadKeyCode` and selection setup by probe, call that "config-checked", and hand the real-controller run to the user (step 5).

## 3. Log every stuck point
At each step ask, and write down any "yes":
- **Don't know what to do?** No clear goal, hint or marker; too much text; the goal is off-screen.
- **Can't do it?** A prompt out of range, behind a wall (`RequiresLineOfSight`), overlapping another prompt, hidden by UI, or a hold too long (`HoldDuration`). A touch target too small or under default controls. An action with no binding on this device.
- **Did it, but can't tell?** No sound, visual or text feedback. A failure with no reason ("Too far", "No oil", "Already full").
- **Dead end?** A state the player can't get out of (resources gone, stuck in geometry, a lost tool).
- **Two players at once?** Run the first session with 2 clients if the game is multiplayer: shared objects, whose hint shows, who gets credit.

Fix blockers, re-run the same step, and record each as fixed or open.

## 4. Make it measurable: onboarding funnel steps
If the first session has steps, log them on the server with `AnalyticsService:LogOnboardingFunnelStepEvent` (step numbers in order from 1, a short name per step, once per player per step).
- Keep the step list short: the 4–8 moments from step 2.
- Check the calls fire in a Studio playtest (a temporary `print` beside each call, removed after). Real numbers only exist after publishing; say so.
- Tell the user to read the funnel split by device once real players arrive (`${CLAUDE_SKILL_DIR}/../roblox-game-design/references/monetization-liveops.md` → Instrument).

## 5. Hand off what you can't judge
List at most five items for the user, each with exact steps:
- **Sounds:** you can't hear them. Never choose final sounds alone. List each one (asset ID, where it plays, why chosen) and ask the user to listen and approve or swap.
- **Sound and asset rights:** before adding audio or models, check who made them (`roblox-assets` → Sourcing). Prefer Roblox-made assets or the user's own uploads. An asset with an unknown license or creator blocks shipping: list it at the top of the hand-off, not as a footnote.
- **Visuals the screenshot tool doesn't draw** (some `BillboardGui` markers, effects), and anything judged only by pixel stats.
- **A real controller, a real phone, and the console run.**
- **Fun.** An AI playthrough finds blockers; it is never evidence of fun (the router's evidence standard).

## 6. Clarity and clip checks (designer judgment, E1)
- **10-second test:** from the opening shot alone, could a young player say what the game is about?
- **One clear action with a clear result** in the first minute; depth, shops and secondary systems come after the first fun (`roblox-ui-ux` → Onboarding UX).
- **Clip moment:** is there a moment a player would record, screenshot or retell? If not, *propose* one in the report.
- **Design changes made during the pass** go in `.apex/decisions.md` with how to reverse them.

## 7. Report
Add this block before the usual verified / code-only / not tested table:
```
Player pass
Target: <fantasy> · first goal: <...> · first fun at <N> s (timed | estimated)
10-second test: pass/fail — <why>
Devices: phone ✓/✗ · tablet ✓/✗ · console preset ✓/✗ · desktop ✓/✗ · real gamepad: config-checked only
Stuck points: <n> found → <n> fixed, <n> open (list open ones)
Funnel steps: <n> logged (<names>) · fire in Studio: yes/no
Clip moment: <exists: ... | proposed: ...>
Please check (you): 1. ... (≤ 5)
```

## Rules
- Polish before features. Propose new systems; don't add them during a pass.
- Each device run is separate evidence. A phone run says nothing about console.
- "Could not test" is fine. Claiming a check you didn't run is not.
