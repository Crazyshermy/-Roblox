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
1. Edit skills in `.claude/skills/`.
2. `python3 tests/validate.py`: frontmatter, names, routing coverage, references, size and description budget. Free.
3. `python3 tests/check_api.py <creator-docs clone>`: every engine API mentioned exists and isn't deprecated. Free (clone instructions are in the script header).
4. `python3 tests/smoke.py`: real headless sessions with skill-usage and behavior checks. About $1.
5. For behavioral changes: `python3 benchmarks/run.py`, or `--only B03,B07` for affected tasks. About $5 for all ten. Compare against `docs/BENCHMARKS.md`. Investigate every loss and every "incorrect" flag before changing skills, and check judge claims against the docs.
6. Bump `metadata.version` in `roblox/SKILL.md`, plus `.claude-plugin/plugin.json` and `marketplace.json`. Add a CHANGELOG entry.

## Refreshing currency (do this at least quarterly)
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/Roblox/creator-docs.git /tmp/cd
git -C /tmp/cd sparse-checkout set content/en-us/reference/engine content/en-us/cloud-services content/en-us/projects content/en-us/scripting content/en-us/studio
python3 tests/check_api.py /tmp/cd
```
Then re-check each item in `currency.md` against its listed source path, update the numbers and the snapshot date, and scan the Roblox DevForum "Announcements" and release notes for new Full Releases that change best practice.

## Adding a benchmark task
Add an entry to `benchmarks/tasks.json` with a realistic prompt (no `/roblox` prefix) and 5–6 rubric items that an expert would check. Write the rubric from domain knowledge, not from skill text, to limit teaching to the test.
