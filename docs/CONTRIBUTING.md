# Contributing and update guide

This guide is for a person or a future Claude session improving Roblox Apex.

## Ground rules
- **Quality over quantity.** A new skill must change decisions measurably. Prefer extending an existing specialist or adding a reference file. Every added description costs context in *every* session.
- **One home per rule** (see ARCHITECTURE → Ownership). Point to the owning skill instead of duplicating a rule.
- Specialist `SKILL.md` stays under about 160 lines and about 1.8k tokens. Depth goes in `references/`, linked with an explicit "read when…" condition.
- Descriptions are **quoted YAML strings**: start with what the skill covers, include trigger words, and stay under about 330 chars. Unquoted descriptions containing `: ` break YAML, and the skill then loads with *no description*. This happened in development and is now caught by `validate.py`.
- Never invent APIs. Version-sensitive facts go in `roblox/references/currency.md` with a source and date.
- Write standing instructions ("when X, do Y"), not narration.

## Workflow
0. First time in a fresh environment, run `tests/get_tools.sh`. It fetches `luau-compile`, `rojo`, `pwsh` and a creator-docs clone into `tests/.tools/` (gitignored).
1. Edit skills in `.claude/skills/`.
2. `python3 tests/validate.py`: frontmatter, names, routing coverage, references, size and description budget. Free.
3. `python3 tests/check_api.py <creator-docs clone>`: every engine API mentioned exists and isn't deprecated. Free (clone instructions are in the script header).
4. `python3 tests/smoke.py`: real headless sessions with skill-usage and behavior checks (about $1). Use `--repeat 3` for trigger rates and `--model opus|haiku` for other models. If you change a marker regex, add an example to `tests/test_smoke_patterns.py` (free); past false positives are recorded there.
4b. Installers: `tests/test_installers.sh tests/.tools/pwsh/pwsh` (free) covers `install.sh` and `install.ps1` under PowerShell 7. Windows PowerShell 5.1 isn't covered.
5. For behavioral changes: `python3 benchmarks/run.py` (Q&A, about $3) and `python3 benchmarks/project_run.py --luau-compile <path>` (real edits in the Lighthouse fixture with the Studio simulator, about $3). Use `--only` for the affected tasks. Compare against `docs/BENCHMARKS.md`. Investigate every loss and every "incorrect" flag before changing skills, and check judge claims against the docs.
6. Before a release: `python3 tests/install_test.py --ref <branch>`. It clones from GitHub and installs via the project and plugin methods into an isolated config, then runs fresh sessions for every command (about $1). The first time, push the branch.
7. Bump `metadata.version` in `roblox/SKILL.md`, plus `.claude-plugin/plugin.json` and `marketplace.json`. Add a CHANGELOG entry.

## Refreshing currency (do this at least quarterly)
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Roblox/creator-docs.git /tmp/cd
git -C /tmp/cd sparse-checkout set content/en-us/reference/engine content/en-us/cloud-services content/en-us/projects content/en-us/scripting content/en-us/studio
python3 tests/check_api.py /tmp/cd
```
Then re-check each item in `currency.md` against its listed source path, update the numbers and the snapshot date, and scan the Roblox DevForum "Announcements" and release notes for new Full Releases that change best practice.

## Tools the tests need
- `luau-compile`, from the Luau release zip at `github.com/luau-lang/luau/releases`, for syntax checks in the project benchmark and simulator.
- Optionally `rojo` (`github.com/rojo-rbx/rojo/releases`) to rebuild `tests/fixtures/LighthouseKeeper.rbxl`: `rojo build tests/fixtures/lighthouse/default.project.json -o tests/fixtures/LighthouseKeeper.rbxl`.
- The fixture's seeded flaws are listed in `tests/fixtures/lighthouse.FLAWS.md`, outside the fixture folder so models under test can't read it. If you add a flaw, add it there and to a project-benchmark rubric.

## The Studio simulator is not Studio
`benchmarks/project_run.py --sim-unsynced` runs tasks with Studio *not* receiving file edits, as when Rojo or Script Sync isn't running. Use it to check that Claude detects stale code instead of claiming a playtest verified its change.

`tests/studio_sim/server.py` imitates the Studio MCP *tool surface* over the fixture files. It checks syntax and a few known runtime-error patterns, and it never runs game logic. Use it to test *workflow* behavior (did Claude playtest, read the console and report honestly?). Never cite it as runtime evidence. Real Studio results come only from `tests/STUDIO-TEST.md`.

## Adding a benchmark task
Add an entry to `benchmarks/tasks.json` with a realistic prompt (no `/roblox` prefix) and 5–6 rubric items that an expert would check. Write the rubric from domain knowledge, not from skill text, to limit teaching to the test.
