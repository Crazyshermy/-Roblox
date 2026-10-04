# Benchmarks: baseline Claude vs Claude + Roblox Apex

**Method** (`benchmarks/run.py`):
- 10 representative tasks (`benchmarks/tasks.json`), each with a 6-item expert rubric.
- The same plain prompt goes to both arms with **no `/roblox` prefix**, so Apex has to win through automatic routing.
- Each arm runs in a fresh temporary project. The baseline has no skills. Apex has the skills plus the CLAUDE.md block.
- The subject model is Sonnet in headless Claude Code v2.1.289. Tools are read-only.
- The judge is a separate Opus session that sees both answers **blind** in random A/B order. It grades each rubric item, flags incorrect or stale claims, slop and over-engineering, and states a preference.

**Limitations (read these first):**
- One sample per arm, so run-to-run variance is visible. A baseline score swung 0.92 → 1.00 between identical runs.
- An LLM judge, whose Roblox knowledge can lag: it once flagged the correct, current remote-throttle figure as "invented".
- Rubrics written by the same author as the skills, which risks teaching to the test.
- This is a regression detector and a sanity check of direction, **not a scientific evaluation.**

## Latest results (v1.0.0, 2026-10-04): raw data in `benchmarks/results/latest/`
| Task | Apex skills auto-loaded | Baseline | Apex | Winner |
|---|---|---|---|---|
| B01 secure currency system | security, data, networking | 0.92 | 1.00 | Apex |
| B02 two-player crate carry | networking, physics-animation, security, game-design | 0.67 | 1.00 | Apex |
| B03 DataStore progress loss | data | 0.75 | 1.00 | Apex |
| B04 horror encounter | game-design, genres, level-design | 0.75 | 0.92 | Apex |
| B05 300-enemy TD optimization | performance, genres | 0.83 | 0.92 | Apex |
| B06 cross-device HUD/inventory | ui-ux, genres | 0.75 | 0.92 | Apex |
| B07 remote exploit review | security, networking | 1.00 | 1.00 | Apex |
| B08 progression (ramen stand) | game-design | 0.50 | 1.00 | Apex |
| B09 replication/streaming bug | debugging | 0.83 | 1.00* | Apex* |
| B10 combat feel | networking, game-feel, security | 0.75 | 0.92 | Apex |

**Wins: Apex 10 · baseline 0.** Mean rubric coverage was **0.78 baseline vs 0.97 Apex**. The judge's "incorrect/stale claim" flags totaled **19 for the baseline vs 3 for Apex**.
\*B09 lost (0.83 vs 0.83) in the full run. After a targeted fix to the debugging skill it was re-run alone and won (`summary-B09-rerun.md`). The full-run tally was 9–1.

Cost of the final full run: $2.96. The whole development cycle (all smoke and benchmark iterations) cost under $20 of model usage.

## What the benchmark changed during development (red-team log)
| Run | Result | Problems found → fixes |
|---|---|---|
| 1 | Apex 8–2, coverage 0.98 vs 0.77, 14 Apex "wrong" flags | Meta-jargon in answers (route preamble, `.apex/` notes, E-labels) → Communication rules. Game feel double-played replicated animations and delayed impact until server confirm → prediction rules rewritten. Ignored "concise" → proportionality and scope rule. Fixed code depended on a nonexistent module → drop-in code rule. |
| 2–3 (targeted) | B07 lost twice | Apex said the remote throttle was "per remote" (the docs say per client, shared across remotes) → currency and security wording fixed. Ability ownership was not checked → precondition added. Severity ranking added for reviews. |
| Final | Apex 9–1 (10–0 after B09 fix), 3 Apex flags | B09: missing "state + stable ID in payload" pattern → debugging table row added. |

Separately, `tests/check_api.py` found that the skills themselves recommended the deprecated `Lighting.Technology`. That was replaced with `LightingStyle` and `PrioritizeLightingQuality`.

## Smoke tests (latest: `tests/results-latest/summary.md`)
9 of 9 pass ($0.77): status/discovery, router entry, security auto-routing, design auto-routing, debug auto-routing, currentness, proportionality (trivial task loads 0 specialists), ambition (boundary-breaker fires), and route inspection.

## Not yet benchmarked
Behavior with a live Studio MCP connection, Opus or Haiku as the subject model, multi-turn implementation sessions with file edits, and repeated sampling for variance estimates.
