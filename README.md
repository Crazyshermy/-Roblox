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
Pick **one** method per machine or project. Mixing them loads duplicate skills.

**A. Per project (recommended).** macOS, Linux, or Git Bash on Windows:
```bash
git clone https://github.com/crazyshermy/-roblox roblox-apex
roblox-apex/install/install.sh /path/to/your/game        # → your/game/.claude/skills/roblox*
```
Windows PowerShell:
```powershell
git clone https://github.com/crazyshermy/-roblox roblox-apex
powershell -ExecutionPolicy Bypass -File .\roblox-apex\install\install.ps1 -Project C:\path\to\your\game
```
**B. User-level (all your projects):** `install.sh --user` or `install.ps1 -User` installs to `~/.claude/skills`.

**C. Claude Code plugin** (no scripts, works the same on Windows). Inside Claude Code:
```
/plugin marketplace add crazyshermy/-roblox
/plugin install roblox-apex@roblox-apex
```
Commands also work namespaced (`/roblox-apex:roblox`), and bare `/roblox` works when no other skill uses the name.

Then, in your game project: `/roblox-status` (health check) → `/roblox-init` (creates `.apex/` memory and the CLAUDE.md block).

**Optional but recommended:** enable Roblox Studio's built-in MCP server (Studio → Assistant → ⋯ → Manage MCP Servers → *Enable Studio as MCP server*, then use quick-connect for Claude Code). This lets Claude playtest, read console output and probe the engine (E5 evidence).

**Update:** `git pull` in the clone, then re-run the same install command (it replaces only Apex's own folders). For a plugin install, use `/plugin update`.
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
See [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for numbers and raw results.
- **Discovery and invocation:** real headless Claude Code sessions (v2.1.289) discover all skills in both project and plugin installs. `/roblox`, `/roblox-status` and `/roblox-route` work, and the router loads specialists through the Skill tool.
- **Auto-routing and behavior change:** 9 smoke cases (`tests/smoke.py`) check both *which skills fired* and *behavior markers* in the answer. Examples: the current DataStore budget instead of the stale one, anti-slop reasoning, the respawn bug class, boundary-breaker on "Roblox can't".
- **Benchmark:** in blind pairwise judging on 10 representative tasks, Apex won 9–1 in the final full run (10–0 after a targeted fix to the one loss). Rubric coverage was 0.78 → 0.97, and judge-flagged incorrect or stale claims went from 19 to 3. One sample per arm and an LLM judge, so read the limitations in BENCHMARKS.md.
- **Installers:** the bash installer is tested (install, update, uninstall, conflict refusal). **`install.ps1` has not been executed** because no PowerShell was available in the build environment. On Windows, method C (plugin) is the safest path.
- **Not yet verified:** behavior with a live Roblox Studio MCP connection (no Studio in the build environment), and behavior on models other than the one used in tests.

## Test it yourself
```bash
python3 tests/validate.py            # structure, YAML, routing coverage, budgets (free)
python3 tests/smoke.py               # real sessions, ~$1
python3 benchmarks/run.py            # baseline vs Apex, ~$5
```
The manual procedure for an interactive session is in [tests/SMOKE-TEST.md](tests/SMOKE-TEST.md).

## Repository map
```
.claude/skills/        the skills (single source of truth; also the plugin's skills dir)
.claude-plugin/        plugin.json + marketplace.json
install/               install.sh, install.ps1
tests/                 validate.py, smoke.py, check_api.py, run_case.py, SMOKE-TEST.md
benchmarks/            tasks.json, run.py, results/
docs/                  ARCHITECTURE, SKILL-INDEX, EVIDENCE-POLICY, CONTRIBUTING, BENCHMARKS, RESEARCH
docs/legacy-rbxos/     the earlier RBXOS design (archived; its concepts were folded into the skills)
CHANGELOG.md
```
