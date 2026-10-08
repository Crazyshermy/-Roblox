# Roblox Apex

**A Roblox development intelligence layer for Claude Code.** It is a set of skills that changes *how Claude reasons* about Roblox work: engineering, security, performance, testing, game design, game feel, art, levels and UI. It doesn't restrict Claude, and it doesn't replace Roblox's own tools.

```
Claude → CLAUDE.md block → /roblox router → relevant specialists → verified knowledge + .apex/ project memory
       → Claude reasons → Roblox Studio MCP / your files / tests let Claude act
```
The skills provide expertise and judgment. The MCP and tools provide the ability to act. The two stay separate.

## What it does differently
- **Routes, doesn't dump.** A ~2.3k-token router loads only the 0–4 specialists a task needs (~1k tokens each). Mandatory bundles stop the expensive misses: anything touching value loads security + data.
- **Current, not tutorial-era.** Version-sensitive facts are verified against Roblox's official docs (snapshot 2026-10-02): Server Authority (announced for all creators July 2026), the 2026 DataStore limits, IAS, the new type solver, the `LightingStyle` replacement for `Lighting.Technology`. Every engine API named in the skills is machine-checked against the official reference.
- **Challenges slop.** Pets, eggs, rebirths, generic coins and battle passes need a reason to exist *in this game*. The verdicts are justified, transform or remove.
- **Protects ambition.** "Roblox can't do that" triggers a verified-limitation and technique search (client illusion, simulation split, precomputation, procedural generation…), not a quiet downgrade.
- **Honest about evidence.** It separates facts from recommendations. Simulated players are never treated as real-player evidence. There are no fake "fun = 92" scores.
- **Project-aware.** `.apex/decisions.md` records your decisions, the alternatives you rejected and the conditions for reopening them. Those override generic best practice.

## Install
Pick **one** method per machine or project. Mixing them loads duplicate skills. Everything installs from the **`main`** branch.

**A. Per project (recommended).** macOS, Linux, or Git Bash on Windows:
```bash
git clone -b main https://github.com/Crazyshermy/-Roblox.git roblox-apex
roblox-apex/install/install.sh /path/to/your/game        # → your/game/.claude/skills/roblox*
```
Windows PowerShell:
```powershell
git clone -b main https://github.com/Crazyshermy/-Roblox.git roblox-apex
powershell -ExecutionPolicy Bypass -File .\roblox-apex\install\install.ps1 -Project C:\path\to\your\game
```
**B. User-level (all your projects):** `install.sh --user` or `install.ps1 -User` installs to `~/.claude/skills`.

**C. Claude Code plugin** (no scripts, works the same on Windows). Inside Claude Code:
```
/plugin marketplace add Crazyshermy/-Roblox#main
/plugin install roblox-apex@roblox-apex
```
The `#main` pins the branch, so it works whichever branch GitHub shows as default. Commands also work namespaced (`/roblox-apex:roblox`). Bare `/roblox` works when no other skill uses the name.

Then, in your game project, run `/roblox-status` (health check), then `/roblox-init` (creates `.apex/` memory and the CLAUDE.md block). With the plugin, `/roblox-init` matters: the CLAUDE.md block makes automatic routing more reliable.

**Strongly recommended:** enable Roblox Studio's built-in MCP server (Studio → Assistant → ⋯ → Manage MCP Servers → *Enable Studio as MCP server*, then use quick-connect for Claude Code). With it connected, Apex makes Claude playtest and read the console after every code change.

**Update:** `git pull` in the clone, then re-run the same install command (it replaces only Apex's own folders). For a plugin install, use `/plugin marketplace update roblox-apex`, then `/plugin update`.
**Remove:** `install.sh --uninstall <project>` / `--uninstall --user`, `install.ps1 ... -Uninstall`, or `/plugin uninstall roblox-apex`. Your `.apex/` and `CLAUDE.md` are never touched.

## Use
| You type | What happens |
|---|---|
| `/roblox <anything>` | Router classifies the task, loads the specialists, prints `*Apex: a → b*`, and works through understand → plan → implement → verify. |
| Just ask normally | Roblox requests auto-trigger the router or a specialist (verified for security, design, debugging and ambition prompts). |
| `/roblox-route <task>` | Dry run: which skills would load, which bundles fire, what's skipped, and why. |
| `/roblox-status` | Version, skills on disk vs actually discovered, knowledge freshness, project memory, Studio MCP. |
| `/roblox-init [description]` | Creates `.apex/project.md`, `decisions.md`, `debt.md` and the CLAUDE.md block. |

Skills: see [docs/SKILL-INDEX.md](docs/SKILL-INDEX.md). Design: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Verified so far
**Live Roblox Studio: tested once** (2026-10-07, Apex 1.2.0, one tester on Windows, Opus 5.5, Rojo 7.7.1, Studio's MCP server). Claude fixed the fixture's bugs and re-checked each in live playtests: multi-client runs, simulated latency, device presets, real DataStore saves, and exploits attacked before and after each fix. Answer-key contamination can't be ruled out for the planted flaws. The run was open-ended, so the scripted [tests/STUDIO-TEST.md](tests/STUDIO-TEST.md) procedure hasn't been run as written. Details and limits: [docs/BENCHMARKS.md](docs/BENCHMARKS.md) → "Live Studio results".

**Automated results (v1.2.0).** Numbers, method and raw data are in [docs/BENCHMARKS.md](docs/BENCHMARKS.md). All of these are single-sample or small-sample runs judged blind by an LLM.
- **Fresh install from GitHub:** 15/15 checks for the project and plugin methods in isolated configs. That covers discovery, `/roblox`, `/roblox-status`, `/roblox-route`, `/roblox-init`, the CLAUDE.md block, `.apex/` memory and specialist auto-routing.
- **Installers:** `install.sh` and `install.ps1` pass install, update, uninstall, conflict and user-level tests (PowerShell 7). `.gitattributes` keeps Windows checkouts working in Git Bash; before v1.2, a Windows checkout broke `install.sh`. **Windows PowerShell 5.1 is untested.**
- **Q&A benchmark (10 tasks, full run):** Apex beat baseline Claude **9–1**, with rubric coverage 0.78 → 0.98.
- **Real-project benchmark** (a Rojo game with a simulator standing in for Studio's tools, *not* real Studio): full run **6–1** at v1.1. The v1.2 run on five tasks went **5–0**. After editing, Apex playtested and read the console in every implementation task, and it detected unsynced code instead of claiming a stale playtest proved anything.
- **Models:** Sonnet passes 13/13 smoke cases and Opus 12/13. **Haiku routes correctly but applies security and data checklists less fully, so use Sonnet or Opus for that work.**
- **Knowledge:** every engine API named in the skills exists and isn't deprecated in Roblox's official reference (`tests/check_api.py`).

## Test it yourself
```bash
tests/get_tools.sh                   # one-time: luau-compile, rojo, pwsh, creator-docs into tests/.tools/
python3 tests/validate.py            # structure, YAML, CRLF, reference paths, routing coverage, budgets (free)
tests/test_installers.sh tests/.tools/pwsh/pwsh   # installer matrix, bash + PowerShell 7 (free)
python3 tests/smoke.py               # real sessions, ~$1
python3 tests/install_test.py --ref main   # fresh clone + both install methods, ~$1
python3 benchmarks/run.py            # Q&A baseline vs Apex, ~$3
python3 benchmarks/project_run.py --luau-compile <path>   # real edits in the fixture, ~$3
```
The manual procedure for an interactive session is in [tests/SMOKE-TEST.md](tests/SMOKE-TEST.md).

## Repository map
```
.claude/skills/        the skills (single source of truth; also the plugin's skills dir)
.claude-plugin/        plugin.json + marketplace.json
install/               install.sh, install.ps1
tests/                 validate.py, check_api.py, smoke.py, install_test.py, run_case.py,
                       SMOKE-TEST.md, STUDIO-TEST.md, studio_sim/ (Studio-workflow simulator),
                       fixtures/lighthouse/ (Rojo test game) + LighthouseKeeper.rbxl,
                       fixtures/lighthouse-reference/ (live-verified partial fix; an answer key, like lighthouse.FLAWS.md),
                       results-latest/studio/ (live Studio and Blender import records)
benchmarks/            tasks.json + run.py (Q&A), project_run.py (real edits in the fixture), results/latest/
docs/                  ARCHITECTURE, SKILL-INDEX, EVIDENCE-POLICY, CONTRIBUTING, BENCHMARKS, RESEARCH
docs/legacy-rbxos/     the earlier RBXOS design (archived; its concepts were folded into the skills)
CHANGELOG.md
```
