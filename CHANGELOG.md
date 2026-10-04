# Changelog

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
