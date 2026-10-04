# Changelog

## 1.0.0 (2026-10-04)
First release of Roblox Apex, replacing the RBXOS design (archived in `docs/legacy-rbxos/`).
- `/roblox` router with a signal table, mandatory bundles, specialist budgets, a route line, project memory, standards and a working loop.
- 18 specialists: luau, architecture, networking, data, security, performance, testing, debugging, game-design, genres, game-feel, visual-direction, level-design, ui-ux, physics-animation, assets, boundary-breaker, review.
- User-only commands: `/roblox-status`, `/roblox-route`, `/roblox-init` (with `.apex/` templates).
- Version-sensitive facts verified against Roblox creator-docs (2026-10-02 snapshot).
- Packaging: project install, user install, Claude Code plugin and marketplace manifests (validated).
- Verification tooling: `validate.py` (YAML-strict), `check_api.py` (API existence and deprecation), `smoke.py` (real sessions), `benchmarks/run.py` (blind baseline vs Apex).
- Fixes found by the red team before release: 15/22 skills had invalid YAML frontmatter; the stale `Lighting.Technology` advice; a misstated remote throttle scope; a double-played replicated animation; impact feedback delayed to server confirm; meta-jargon leaking into answers; ignored "concise" requests.
