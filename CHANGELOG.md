# Changelog

## 1.5.0 (2026-10-21)
A new-player pass, from a first-minute baseline and retest in live Studio (2026-10-17 and 2026-10-21). The record is in `tests/results-latest/studio/lighthouse-first-minute-2026-10-21.md`.
- **New skill `roblox-player-pass`:** play the first session as a brand-new player on a small phone, a tablet, a console preset and desktop. Covers:
  - a target written before playing (fantasy, first goal, first fun)
  - first fun timed with timestamps, not estimated
  - a stuck-point log
  - onboarding funnel steps (`LogOnboardingFunnelStepEvent`)
  - a hand-off of what Claude can't judge: sounds, asset rights (an unknown license blocks shipping), real hardware, fun
  - a 10-second clarity check and a clip moment
  - a report block
  The motivation is one YouTube creator's account (E1), labeled as such. Only what runs in Studio counts as verified. Routed from the router for polish, the first minute, tutorials, onboarding, the new-player experience, and player-facing work about to be called done or ready to ship.
  - **Evidence so far:** the retest ran a v1 draft. It covered tablet and console presets, funnel calls and a stuck-point count that the baseline didn't. The runs also differed in the answer key, the Studio tools and Rojo, so this is suggestive, not proof. The v2 changes have **not** been run live: timed first fun, the 10-second report line, the asset-rights rule and the Rojo check.
- **Pointers:** `roblox-review` (Experience lens) and `roblox-testing` (Playtesting for experience) point to the new skill. `monetization-liveops.md` says to read funnels split by device. Per the docs, funnel filters include device data and apply at a funnel's first step. A console example is labeled as one creator's account.
- **Rojo (architecture):**
  - Use an explicit `CFrame` for **every** part, not only parts with children. Two childless parts placed with `Position` reset to the origin after a `Color` and `Material` change (seen in testing).
  - Read a service node added to the project file mid-session back in Studio. `Lighting` didn't live-sync once, although `rojo build` included it (seen once, cause unconfirmed).
- **Status lines:** live Studio is now described as three sessions (2026-10-07, 2026-10-17, 2026-10-21), all with the project's Apex 1.2.0 skills.
- **Tests:** a `player-pass-auto` smoke case with pattern examples. `install_test.py` and the `/roblox-status` inventory include the new skill.
  - **Smoke (Sonnet, 2026-10-21): 15/15.** `player-pass-auto` routed to the new skill in 2/2 runs. `currency` first failed only because on Windows the runner decoded `×` with the system code page. It passed with `PYTHONUTF8=1`.
  - **B06-mobile-ui rerun:** Apex 0.83 vs baseline 0.67. Player-pass correctly didn't load. **The baseline arm had the tester's claude.ai `game-ui-design` skill loaded, so this isn't a comparison against plain Claude.** The judge's two flags on Apex trace to existing `roblox-ui-ux` lines, not to this release.
  - **P10-mobile-controls not run:** `project_run.py` gives each session an empty config dir, which hides a subscription login.

## 1.4.0 (2026-10-09)
Blender texture, PBR and Open Cloud lessons from a second round of verified imports (2026-10-08). Records are in `tests/results-latest/studio/blender-import-2026-10-08.md`.
- **`roblox-blender-modelling`:**
  - **New `textures.md`:** baked object-space procedurals → `TextureID` with exact pixels, wood grain UVs that run along the plank, worn stone by decimation, and PBR maps → `SurfaceAppearance` (wiring, normal bake, grayscale PNG writer, `use_tspace=True`).
  - **New `open-cloud.md`:** upload and update a Model with the Open Cloud Assets API, only when the user asks. Covers key handling, the `;` curl gotcha, package, anchor and yaw fixes after insert, and why placed copies don't pick up a new version by themselves.
  - **New §6, visual check from player distance:** in the first texture test every technical check passed, but the user still rejected both models at play distance.
  - Axis mapping, a winding and mirrored-UV check, and Box/Hull results on the new meshes. `studio-checks.md` gains texture fingerprints, captures at the user's pixel density, PBR A/B tests and a tilt-vs-perspective check.
  - A new rule near the top: [verified] means verified in earlier testing, not by Claude in the current session. Claude says "these settings were verified in earlier testing" and claims its own verification only for checks it ran. A smoke answer had said "I verified these settings on a crate" without running anything.
  - Reshaped to stay within the size guidelines: 129 lines, with a 326-character description. The one-color code moved into `palette.md`.
- **`currency.md`:** the texture docs disagree on the maximum size (4096 vs 1024), and Open Cloud asset Create and Update are beta (with the package and `AutoUpdate` defaults).
- Router, `roblox-assets` and `SKILL-INDEX.md` now name textures and Open Cloud uploads as triggers.

## 1.3.0 (2026-10-08)
Lessons from the first live Roblox Studio testing (2026-10-07) and two verified Blender → Studio imports. Details are in `docs/BENCHMARKS.md` → "Live Studio results".
- **New skill `roblox-blender-modelling`:** Blender MCP modelling for Roblox. Covers 1 unit = 1 stud, a base pivot, color carried in an embedded sRGB or palette texture (a plain material color imported wrong), the exact FBX export call and 3D Importer settings, and post-import checks (size, triangles, texture pixels, collision, screenshots). Rules carry [verified]/[file-checked]/[untested] tags. Routed from the router, and pointed to from assets.
- **Studio MCP** (`roblox/references/studio-mcp.md`):
  - multi-client tests started from `execute_luau` via `StudioTestService`
  - one `screen_capture` at a time
  - `execute_luau` edits already sit in one undo recording
  - a probe's `require` gets a separate module instance
  - Output clears on playtest; `character_navigation` limits; CoreGui noise in test clients
  - a new "Before the user saves the place" check: PlaceId, Rojo connection, Save to File, never save over a repo or plugin place file
- **Rojo** (architecture): use an explicit `CFrame` for parts with children (Rojo reset a parent to the origin); set `servePlaceIds` (Rojo synced one game into another place); legacy chat in `rojo build` places.
- **Data:** `GetDataStore` throws in unpublished places, so call it in `pcall`, never at module load. `StudioTestService` clients have negative UserIds.
- **Testing:** reproduce exploits before fixing and re-attack under latency. Network Simulator per client window; device presets carry over to test clients. Forced load failure via the `StandardRead` limit; prove `UpdateAsync` merges with a marker field. `PlayerRemoving` precedes `BindToClose` in Studio.
- **Security fuzz checklist:** touch-spoof probes (detached limb, corpse, teleports). `firetouchinterest` isn't available in Studio.
- **Assets:** set `CollisionFidelity` explicitly after every import, because the importer's choice varied for the same mesh. **Currency:** 20,000-triangle mesh limit, DataStore request types, `StudioTestService`/`StudioDeviceSimulatorService`.
- **Tests and fixtures:**
  - `tests/fixtures/lighthouse-reference/`: the live-verified partial fix, kept outside the fixture like the answer key
  - `lighthouse.FLAWS.md` gains "Found live, not planted" (L1–L10); F1–F8 unchanged
  - live records in `tests/results-latest/studio/`
  - `STUDIO-TEST.md` setup keeps answer keys and the repo's place file out of the test folder
  - a `blender-auto` smoke case (not yet run)
  - `check_api.py` allowlists a DataStore error name and two FBX property names
- The original fixture (`tests/fixtures/lighthouse/`, `LighthouseKeeper.rbxl`) is unchanged.

## 1.2.0 (2026-10-04)
Pre-Studio hardening from a critical review. **Live Roblox Studio: NOT VERIFIED — requires local Windows Roblox Studio validation.**
- **Windows:** added `.gitattributes`, because a Windows (`autocrlf`) checkout broke `install.sh` in Git Bash. `install.ps1` is now tested under PowerShell 7 (`tests/test_installers.sh`).
- **Real-Studio honesty and safety:**
  - confirm Studio has the edited code before trusting a playtest
  - `studio_id`
  - Edit-DataModel probes stay read-only
  - ask once before playtesting a game that saves data (playtests can write real DataStores)
- **Robustness:** all reference links use `${CLAUDE_SKILL_DIR}`, because Haiku resolved bare paths against the project root. The validator enforces this.
- **Skills:**
  - anti-slop builds what the user explicitly asks for, with one suggestion at most
  - `ProximityPrompt`, `ClickDetector` and `Touched` get the remote contract
  - ProcessReceipt single-callback rule; no `PromptProductPurchaseFinished` grants
  - doc-verified Audio API, including acoustic simulation
  - NPC/enemy AI reference
  - monetization and live-ops reference
  - exact `ScreenInsets` values
  - hitstop caveat
  - genres only load for design, feel or level work; bundles count toward the specialist cap
- **Tests:** `--repeat` trigger rates, `--rescore`, `--model`, marker unit tests, `--sim-unsynced`, three new project tasks (NPC chase, developer product, mobile controls), `get_tools.sh`.

## 1.1.0 (2026-10-04)
Driven by fresh-install testing, a real-project benchmark (Lighthouse fixture plus a Studio-workflow simulator) and an independent red team. Details are in `docs/BENCHMARKS.md`.
- **Verification behavior:** the router now prescribes a concrete loop when Studio tools exist (playtest → console → fix → stop after the last edit) and ends code answers with `Verified · Not verified`. Apex playtested in 5/5 implementation tasks vs the baseline's 0/5.
- **Routing:** trigger-first descriptions (security, data, networking, design, performance, architecture), so auto-routing works even without the CLAUDE.md block. The CLAUDE.md block now says to load the `roblox` skill first.
- **Correctness fixes:**
  - ProcessReceipt yields until data loads.
  - Session-lock GUID, expiry and refresh.
  - In-flight saves are coalesced.
  - Per-key DataStore throughput and the storage quota.
  - MemoryStore partition scoping.
  - The default jump comes from JumpPower 50, not JumpHeight 7.2.
  - Animation permissions.
  - Server Authority status (announced; one docs page still says beta).
  - InputAction validation, flinging and the official movement-check approach.
  - `IsPaidItemTradingAllowed`.
  - Round value against the player.
  - Implement the full contract when hardening.
  - Cross-device input in the definition of done.
  - Engine effect primitives for VFX.
  - The RemoteFunction direction rule (contradiction removed).
  - pcall-safe busy flag in the remote skeleton.
- **`/roblox-status`:** name-based inventory instead of counting.
- **Repository:** `main` branch created; README installs pin `#main` and `-b main`.
- **Tests:** `install_test.py` (GitHub clone, isolated config, both methods), `benchmarks/project_run.py`, `tests/studio_sim/` (simulator, never E5), the Lighthouse fixture and `.rbxl`, `STUDIO-TEST.md` (real Studio procedure, not yet run), and the `security-nomd` smoke case.

## 1.0.0 (2026-10-04)
First release of Roblox Apex, replacing the RBXOS design (archived in `docs/legacy-rbxos/`).
- `/roblox` router with a signal table, mandatory bundles, specialist budgets, a route line, project memory, standards and a working loop.
- 18 specialists: luau, architecture, networking, data, security, performance, testing, debugging, game-design, genres, game-feel, visual-direction, level-design, ui-ux, physics-animation, assets, boundary-breaker, review.
- User-only commands: `/roblox-status`, `/roblox-route`, `/roblox-init` (with `.apex/` templates).
- Version-sensitive facts verified against Roblox creator-docs (2026-10-02 snapshot).
- Packaging: project install, user install, Claude Code plugin and marketplace manifests (validated).
- Verification tooling: `validate.py` (YAML-strict), `check_api.py` (API existence and deprecation), `smoke.py` (real sessions), `benchmarks/run.py` (blind baseline vs Apex).
- Fixes found by the red team before release: 15/22 skills had invalid YAML frontmatter; the stale `Lighting.Technology` advice; a misstated remote throttle scope; a double-played replicated animation; impact feedback delayed to server confirm; meta-jargon leaking into answers; ignored "concise" requests.
