# Smoke test procedure

## Automated (headless, the source of truth)
```bash
python3 tests/validate.py      # must print OK
python3 tests/smoke.py         # must exit 0; results in tests/results/smoke-<time>/summary.md
```
Each case runs a fresh temporary project with the skills installed, sends one prompt through `claude -p`, and records the **actual `Skill` tool calls** from the event stream, the files read (to show progressive disclosure), and the answer. A case passes only if the expected skills fired **and** the answer shows the behavior those skills teach:

| Case | Proves | Behavioral marker (from skill content) |
|---|---|---|
| `status` | `/roblox-status` works, and skills are discovered in-session | the current version, specialist names listed as discovered |
| `router-entry` | `/roblox` routes an architecture task | architecture (+ networking) loaded; route line; replicated attributes for state; late-join handling |
| `security-auto` | auto-routing with no prefix | NaN/inf checks, yield-in-critical-section, negative amounts, rate limit, two-party confirmation |
| `design-auto` | game-design auto-routing | fantasy and pillars, "why does it belong"; no egg-hatching or rebirth defaults |
| `debug-auto` | debugging auto-routing | `CharacterAdded`, stale respawn reference |
| `currency` | currentness | reads `currency.md`; states 300 + CCU×40 and 60 + players×40; the old ×10 only appears as "outdated" |
| `trivial` | proportionality | ≤ 1 specialist, ≤ 2,500 chars |
| `ambition` | creative ambition | boundary-breaker loaded; snapshot/record approach; options; doesn't open with "yes, good plan" |
| `security-nomd` | auto-routing **without** a CLAUDE.md block (plugin users who skipped `/roblox-init`) | security loaded; negative and NaN amounts found |
| `pet-request` | anti-slop respects an explicit request | builds the server module (with a weights/`PolicyService` mention); no refusal or lecture |
| `npc-ai` | NPC/enemy AI routing | physics-animation loaded; path status/`Blocked`, network ownership, `MoveTo` timeout |
| `prompt-security` | client-initiated `ProximityPrompt` grants | security loaded; cooldown/once-only and distance/state checks |
| `route-inspect` | `/roblox-route` explains routing | names security, data, networking, plus skipped skills |

Add `--with-baseline` to run each case without Apex as a contrast. Use `--repeat 3` to measure trigger *rates* (a case passes at ≥ 2/3), and `--model opus|haiku` to check other models. `python3 tests/test_smoke_patterns.py` unit-tests the marker regexes (free).

Fresh-install acceptance (clone from GitHub, isolated config, both install methods): `python3 tests/install_test.py --ref main`.
Real Roblox Studio procedure: [STUDIO-TEST.md](STUDIO-TEST.md). **Live Roblox Studio: tested once (2026-10-07), not yet with the scripted procedure.** See `docs/BENCHMARKS.md` → "Live Studio results".

## Manual (interactive Claude Code, about 5 minutes)
Open Claude Code in a project where Apex is installed.
1. Type `/` and confirm `roblox`, `roblox-status`, `roblox-route` and `roblox-init` appear in the menu.
2. `/roblox-status`: every specialist should be ✓ discovered. Anything ✗ means a frontmatter or discovery problem.
3. `/roblox-route Build a secure player trading system`: expect networking → security → data (plus testing or review), and the value bundle fired.
4. Ask *without* `/roblox`: "Review this remote: `Remote.OnServerEvent:Connect(function(p, amt) p.leaderstats.Coins.Value += amt end)`". Expect the answer to start with `*Apex: security …*`, a severity-ranked finding list and a drop-in fix.
5. Ask: "Design a progression system for my cozy fishing game." Expect fantasy-first reasoning that challenges generic currencies, pets and rebirths rather than defaulting to them.
6. Ask: "My LocalScript errors 'attempt to index nil with Humanoid' after respawn." Expect the debugging route and the respawn and stale-reference explanation.
7. Ask: "Roblox can't do portals you can see through, so let's use a teleport pad, right?" Expect boundary-breaker: verify the limitation, then propose `ViewportFrame` or camera techniques with trade-offs.
