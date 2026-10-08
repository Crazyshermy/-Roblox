# Benchmarks and verification results (live Studio: 2026-10-07; automated runs: v1.2.0, 2026-10-04)

**Live Roblox Studio: tested once (2026-10-07), by one tester on Windows.** See "Live Studio results" below. It was open-ended testing on the Lighthouse fixture, not the scripted procedure in `tests/STUDIO-TEST.md`. Everything after that section comes from headless runs and the Studio-workflow simulator, which is process evidence only.

## Live Studio results (2026-10-07)
**Setup:** Claude Code v2.1.293 · Opus 5.5 at xhigh effort · Roblox Apex 1.2.0 · Rojo 7.7.1 (`rojo serve`) · Roblox Studio's built-in MCP server · Windows · Studio version **not recorded**. The place was tested unpublished, then published as a private experience with Studio API access on, for a real-DataStore pass. Full record: `tests/results-latest/studio/lighthouse-2026-10-07.md`. Resulting code: `tests/fixtures/lighthouse-reference/`.

**Possible answer-key contamination.** During the run, `lighthouse.FLAWS.md` sat **one folder above** the test project, where Claude could have read it. Nothing shows whether it did, so **contamination can't be ruled out for the planted flaws F1–F8**. The ten live-found bugs L1–L10 (`tests/fixtures/lighthouse.FLAWS.md` → "Found live, not planted") aren't in the answer key, so they aren't affected. `STUDIO-TEST.md` now says to keep the answer key out of the test folder.

| Area | Result (observed in live Studio unless noted) |
|---|---|
| Bugs fixed with live evidence | Planted F1, F2, F3, F6 and the data-safety parts of F5, plus live-found L1–L10 (L3 only partly), each re-checked live after the fix. F4, F7, F8 and session locking were deliberately left open (fixture scope decision D-005) |
| Sync discipline | Every edit went through Rojo, and sync was proven (`script_read`/`script_grep`, property reads) before each test. No test ran on stale code |
| Exploits, attacked before and after the fix | Detached-limb touch spoof (77 studs) and corpse limb: got oil before, blocked after, including under Bad 3G. Blink teleport: blocked at zero latency, **got through under Bad 3G**. Teleport-and-stay: **still collects** (needs movement validation). 14 malicious refuel payloads and 50-request spam: rejected or capped after the fix (not testable before it, because the server didn't boot) |
| Multiplayer | Three 2-client `StudioTestService` runs started from the MCP, with mid-session joins, per-player isolation, simultaneous refuels and leave mid-session. Network Simulator at ~56/127/390 ms measured ping. Device Simulator on iPhone 7 and desktop presets |
| Real DataStore | Save → load round trip. A forced load failure didn't overwrite the stored record (same version). `UpdateAsync` merge proven with a planted marker field. Shutdown saves landed (~0.5 s) |
| Visual | Lamp brightness chosen by measuring screenshot pixels (clipped-white ground → 0%). HUD/chat and touch-button/Jump overlap measured at 0 px after the fixes |
| Not verified | Session locking and autosave (not implemented), a `BindToClose`-initiated save (Studio removes players first), real touch/gamepad hardware, real devices, tablets, glancing high-speed pickups |

**Against the `STUDIO-TEST.md` steps:** 3 (HUD respawn fix), 4 (sync confirmed before playtests), 5–6 (console read, then fixed from the evidence), 7 (respawn mid-playtest with probes) and 8 (security with live attacks) were all exercised. Not recorded: steps 1–2 as separate prompts; whether Claude asked before the first data-writing playtest (the tester's memory notes do record that playtests hit the real store); the "stop `rojo serve`" stale-code check. 9 (design review) was not run, because the tester scoped design out. 10 was partial: visuals were measured, `Lighting` was untouched, and the refuel feel wasn't reworked beyond touch and gamepad input.

**What changed in the skills because of it (v1.3.0):** Studio MCP tool behavior and a pre-save place check (`roblox/references/studio-mcp.md`); Rojo project-file pitfalls (architecture); `GetDataStore` throwing at boot and test-client keys (data); MCP multi-client, latency, device and data-fault techniques (testing); touch-spoof probes (security fuzz checklist); explicit `CollisionFidelity` after import (assets); and the new `roblox-blender-modelling` skill from two verified Blender imports (`tests/results-latest/studio/blender-import-2026-10-08.md`).

---

# Automated results

All runs used headless Claude Code v2.1.289, with **Sonnet** as the subject model unless noted (v1.2 adds Opus and Haiku smoke runs) and an **Opus** session as the blind judge. Answers are compared in random A/B order, and the judge never knows which arm is which.

**Limitations:**
- One sample per arm per task, so run-to-run variance is real. The same baseline scored 0.92 and 1.00 on identical runs.
- LLM judges have stale Roblox knowledge. A judge once flagged the correct remote-throttle figure as invented. Judge "incorrect" flags are checked against the docs before acting on them.
- Rubrics were written by the skills' author (teaching-to-the-test risk).
- **No automated result comes from real Roblox Studio.** The Studio-workflow simulator is process evidence only.

These are regression detectors and directional evidence, not science.

## v1.2.0 results (2026-10-04)
| Check | Result |
|---|---|
| Fresh install from GitHub, project + plugin, isolated config (`install_test.py`) | **15/15** |
| Installer matrix (`test_installers.sh`): `install.sh` + `install.ps1` under PowerShell 7 | **12/12** (Windows PowerShell 5.1 not tested) |
| Windows CRLF checkout (simulated `core.autocrlf=true`) | `main` before v1.2: `install.sh` **broken** in Git Bash. With `.gitattributes`: fixed |
| Smoke, Sonnet, 3 runs per case | 12/13 cases 3/3. `security-nomd` 2/3 (no CLAUDE.md block) |
| Smoke, Opus, 1 run | 12/13 (the miss is the "why it belongs" marker on a fantasy-first design answer) |
| Smoke, Haiku, all runs | Routing mostly works. Applies security and NPC checklists less fully (`security-auto` 0/4 on markers, `npc-ai` 1/4, `currency` 2/4). In one run without the CLAUDE.md block it chose Claude Code's built-in `security-review` skill. **Use Sonnet or Opus for security and data work.** |
| Q&A reruns (activation trimming): B02, B05, B06 | Apex 3–0 (coverage 0.78 → 0.97). B05 no longer loads genres, and B02 dropped from 5 specialists to 4 |
| Project benchmark (simulator), P1, P2, P8, P9, P10, full run after harness fix | **Apex 5–0**. Apex playtested and read the console after its last edit in 5/5 tasks; baseline 2/5 (when told playtests are safe) |
| Stale-code trap (`--sim-unsynced`, P1) | Apex detected that Studio lacked its edit (`script_grep`) and refused to count a playtest. Baseline didn't check |
| API check (`check_api.py`) | 53 qualified + 205 bare identifiers, all present and none deprecated |

**Defects found by v1.2 testing, and fixed:**
- **Windows CRLF breaks `install.sh`.** Fixed with `.gitattributes`, and the validator now rejects CRLF.
- **Bare `references/…` paths:** Haiku resolved them against the project root and missed version facts. All links now use `${CLAUDE_SKILL_DIR}`, enforced by the validator.
- **An invented enum** (`Enum.ScreenInsets.CoreUISafe`) crashed a HUD. The UI skill now lists the exact values.
- **A test-harness crash:** a relative `luau-compile` path took the simulator down. The simulator now reports tool errors instead of crashing.
- **Smoke-marker false negatives** on correct answers. Fixed, plus `--rescore` and `test_smoke_patterns.py`.

**Known, not fixed:**
- **Evidence-grade leak:** "(E3)" appeared in about 2.6% of Apex answers (5/189, mostly v1.0-era runs).
- **The P8 rubric expected pathfinding:** both arms built direct server-driven chasers on an open island. That's defensible, so the rubric is arguably over-prescriptive.

---

# v1.1.0 results (history)

## 1. Fresh-install acceptance (`tests/install_test.py`)
The test clones from GitHub (not the dev workspace), installs into a fresh copy of the Lighthouse fixture with an **isolated `CLAUDE_CONFIG_DIR`**, and runs fresh headless sessions. Final result: **all checks pass, for both methods.**

- **Project install (`install.sh`):**
  - all 22 skills discovered
  - `/roblox-status` reports the version and a complete inventory
  - `/roblox-route` names security, data and networking without executing
  - `/roblox-init` creates `.apex/` and the CLAUDE.md block
  - an unprefixed architecture question auto-routes, and `.apex/project.md` and `decisions.md` are read
  - `/roblox` security review loads the security skill and finds the exploit
- **Plugin install** (`claude plugin marketplace add Crazyshermy/-Roblox#<ref>` + `install`):
  - 22 namespaced skills discovered
  - bare `/roblox-status` works
  - unprefixed review auto-routes to `roblox-apex:roblox-security`

Raw logs: `tests/results-latest/`.

## 2. Smoke suite (`tests/smoke.py`): 10/10 pass
These are routing and behavior-marker checks. Each case requires that the expected skills actually fired (real `Skill` tool events) **and** that the answer shows skill-specific behavior. The cases cover status, the router entry, security, design and debug auto-routing, currency (the 2026 DataStore budgets instead of the stale ones), proportionality (a trivial task loads 0 specialists), ambition (boundary-breaker), route inspection and **security without a CLAUDE.md block**.

## 3. Q&A benchmark (`benchmarks/run.py`): baseline vs Apex, 10 tasks
| Task | Apex skills (auto-loaded, no prefix) | Baseline | Apex | Winner |
|---|---|---|---|---|
| B01 secure currency system | security, data, networking | 0.92 | 0.92 | Apex |
| B02 two-player crate carry | networking, physics-animation, security, game-design | 0.67 | 1.00 | Apex |
| B03 DataStore progress loss | data | 0.83 | 1.00 | Apex |
| B04 horror encounter | game-design, genres, level-design | 0.67 | 0.92 | Apex |
| B05 300-enemy TD optimization | performance, genres | 0.83 | 1.00 | Apex |
| B06 cross-device HUD/inventory | ui-ux, genres | 0.83 | 1.00 | Apex |
| B07 remote exploit review | security | 1.00 | 1.00 | Baseline (tie on rubric) |
| B08 progression (ramen stand) | game-design, genres | 0.50 | 0.92 | Apex |
| B09 replication/streaming bug | debugging | 0.83 | 1.00 | Apex |
| B10 combat feel | networking, game-feel, security | 0.75 | 1.00 | Apex |

**Apex 9 – baseline 1.** Mean rubric coverage was **0.78 → 0.98**. Judge-flagged incorrect or stale claims totaled baseline 18 vs Apex 5. Raw data: `benchmarks/results/latest/qa/`.

## 4. Project benchmark (`benchmarks/project_run.py`): real edits in a real Roblox project
The task is real work in the **Lighthouse Keeper fixture** (`tests/fixtures/lighthouse/`), a Rojo game with seeded realistic flaws (`tests/fixtures/lighthouse.FLAWS.md`). Both arms can edit files and both have the **Studio-workflow simulator** connected as an MCP server, with the same tool names as Roblox's Studio MCP.

The simulator plays tests using real Luau syntax checks plus known runtime-error patterns. It cannot run game logic. **This is process evidence, not E5.**

| Task | Baseline | Apex | Winner | Apex: playtest + console after last edit | Baseline: same |
|---|---|---|---|---|---|
| P1 HUD breaks after respawn | 0.80 | 1.00 | Apex | yes | no |
| P2 harden refuel against exploits | 0.83 | 1.00* | Apex* | yes | no |
| P3 players lose oil on rejoin | 0.67 | 0.92 | Apex | yes | no |
| P4 lamp-state sync | 0.80 | 0.90 | Apex | yes | no |
| P5 design: what darkness means | 0.75 | 0.92 | Apex | (no edits) | (no edits) |
| P6 refuel feels flat | 0.42 | 0.92 | Apex | yes | no |
| P7 "creeping darkness is impossible" | 0.50 | 1.00 | Apex | (no edits) | (no edits) |

\*P2 lost in the final full run (Apex rounded a deduction in the player's favor). After two targeted fixes, "round against the player" and "implement the full contract when hardening", it was re-run alone and won 1.00 vs 0.83 (`latest/project/P2-rerun/`). The full run was **6–1**, and after the fix **7–0**.

**Process:** after its last edit, **Apex playtested and read the console in 5 of 5 implementation tasks. The baseline did in 0 of 5.** All arms' edits passed the Luau compiler. Raw data: `benchmarks/results/latest/project/`.

## 5. Routing without a CLAUDE.md block
This case was measured because plugin users may skip `/roblox-init`.

- **Initial:** 10 of 12 runs triggered the right skills, but pasted-snippet security reviews triggered 0 of 2.
- **After rephrasing the security trigger** ("Load BEFORE answering whether Roblox code is safe…"): **4 of 4**.
- **Unprefixed architecture questions:** these missed intermittently. After a "Use when…" lead and a stronger CLAUDE.md line, they routed 4 of 4.

## Red-team log (what testing changed)
| Source | Finding | Fix |
|---|---|---|
| v1.0 Q&A runs | jargon leakage, double-played animations, delayed impact feedback, ignored "concise", non-drop-in fixes, wrong throttle scope | communication rules, feel and latency rules, scope rule, drop-in rule, wording |
| API checker | the skills recommended deprecated `Lighting.Technology` | `LightingStyle` + `PrioritizeLightingQuality` |
| Fresh install, plugin | no CLAUDE.md, so security didn't trigger | trigger rephrasing, plus the `security-nomd` smoke case |
| Project benchmark | **neither arm playtested after editing** despite having Studio tools | a concrete loop-closing protocol plus a `Verified · Not verified` line (Apex 5/5 afterwards) |
| Project benchmark | keyboard-only input, a dropped in-flight save, per-particle Heartbeat loops, rounding in the player's favor, contract items left as suggestions | cross-device input, save coalescing, engine effect primitives, round against the player, implement the full contract |
| Independent Opus red team (13 findings, each verified against the docs) | ProcessReceipt won't retry on a timer; Server Authority "GA" unsupported by docs; InputActions need validation; flinging via ownership; animation permissions; the jump comes from JumpPower 50 (~6.4 studs), not JumpHeight 7.2; per-key DataStore throughput and storage quota; MemoryStore partition scoping; `IsPaidItemTradingAllowed`; a busy-flag leak in the remote skeleton; undocumented `rbx-*` guide names | all fixed in the owning skills |
| Contradiction scan | networking ("client→server RemoteFunction fine") vs security ("prefer events both ways") | one rule: only server→client invokes are dangerous |
| `/roblox-status` | model arithmetic miscounted the inventory | name-based checklist, no counting |

## Not verified
- **Real Roblox Studio, beyond one run.** Live Studio has been tested once (2026-10-07, one tester, one model, Studio version not recorded; see "Live Studio results"). The scripted `tests/STUDIO-TEST.md` procedure hasn't been run as written, and planted-flaw results may be contaminated by the answer key. The live record shows `list_roblox_studios`, `script_read`, `script_grep`, `execute_luau`, `start_stop_play`, `get_console_output`, `screen_capture` and `character_navigation` in use. The other tools in `studio-mcp.md` (assets, generation, `http_get`, `skill`) weren't exercised.
- **`install.ps1`** has never been executed (no PowerShell available).
- **Other subject models** (Opus, Haiku) and long multi-session use on a real game.
- **Variance:** single samples per arm. Repeated-sampling statistics haven't been collected.

Model spend on all verification runs across the whole project: about $33 ($28 tracked in retained result files, plus ad-hoc runs).
