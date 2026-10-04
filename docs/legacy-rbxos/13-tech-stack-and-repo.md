# 13: Technology Stack (Y) and Repository Structure (Z)

## Y. Technology stack

| Component | Choice | Why this, not the obvious alternative |
|---|---|---|
| Daemon, CLI, MCP servers, gateway, hooks | **Rust** (tokio, serde, `rmcp` official MCP Rust SDK) | (1) **rbx-dom** (`rbx_binary`, `rbx_xml`, `rbx_reflection`) and **full-moon** (Luau AST) are Rust, the definitive libraries for Roblox files and Luau parsing. (2) Hooks run on every tool call, and a Rust binary starts in about 5 ms versus 50–150 ms for Node or Python. (3) It ships as a single static binary per platform, with no runtime to install, which matters for one-installation. (4) Roblox's own reference MCP server was Rust. TypeScript was considered for its MCP-SDK maturity, but losing native rbx-dom and full-moon plus the startup cost decided it. |
| Storage | **SQLite** (rusqlite, WAL, FTS5), optional **sqlite-vec** | Embedded, transactional, zero-ops, per-project files. A server database adds operations burden with no benefit at this scale. |
| Blob store | Content-addressed files (blake3) under `.rbxos/cache/objects` | Dedupe for snapshots and screenshots. Simple garbage collection. |
| Graph algorithms | `petgraph` plus a Leiden implementation | Clustering for system detection |
| Image analysis | `image`, `image-compare` (SSIM), `img_hash` (pHash) | Deterministic visual diffs without Python |
| Studio companion plugin | **Luau**, `--!strict`, built with **Rojo**, tested with **Jest-Lua** (in Studio via `run-in-roblox`-style harness and in Lune for pure modules) | Native. Strict types catch plugin bugs early. |
| Test runtime library | Luau (strict), versioned `.rbxm` | Injected into test DataModels only |
| Static analysis toolchain | luau-lsp, `luau-analyze`, selene, StyLua | Mature community and official tools |
| Offline Luau execution | **Lune** | Roblox file I/O, task scheduler port, fast unit tests on Linux and CI |
| Headless engine | **Open Cloud Luau Execution** | Real engine without Studio |
| Workflows | JavaScript (Claude Code workflow runtime) | Required format |
| Skills and agents | Markdown | Required format |
| Schemas | **JSON Schema 2020-12** as source of truth → codegen to Rust (`typify`) and Luau type definitions (custom generator) | One contract for daemon, plugin, and MCP tools |
| Knowledge pack | Markdown plus YAML frontmatter, compiled to SQLite at build time | Human-reviewable, diffable, and fast at runtime |
| Signing and supply chain | Sigstore (cosign keyless) or minisign signatures. Reproducible builds via `cargo-dist`. SBOM. | Binaries are downloaded at install, so they must be verifiable |
| Secrets | OS keychain (`keyring` crate) plus Claude Code `userConfig` `sensitive` | No secrets in files |
| Local embedding model (optional) | ONNX Runtime small text embedder, run locally | Code never leaves the machine for embeddings |
| Release tooling | `cargo-dist`, GitHub Actions, Rojo build for `.rbxm` artifacts | Cross-platform builds for Windows, macOS, and Linux on x64 and arm64 |

**Language boundary rule:** Rust owns state and determinism. Luau owns in-engine behavior. Markdown and JavaScript own Claude-facing orchestration. No Python in the shipped product, which avoids a second runtime to install.

## Z. Repository structure (the RBXOS product monorepo)

```
rbxos/
├── .claude-plugin/
│   └── marketplace.json                 # marketplace listing → plugin/
├── plugin/                              # ── the Claude Code plugin (shipped)
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   │   ├── roblox/SKILL.md
│   │   ├── roblox-{build,debug,test,inspect,improve,concept,experiment,polish,ship,init}/SKILL.md
│   │   ├── luau-engineering/SKILL.md   (+ reference/*.md)
│   │   ├── roblox-ui/SKILL.md
│   │   └── design-reasoning/SKILL.md   (+ reality-check.md, boundary-breaker.md, scope-options.md,
│   │                                      anti-slop.md, creative-risk.md, fun-model.md, feel-model.md)
│   ├── agents/                          # 13 specialist definitions (see file 03 §S)
│   ├── hooks/hooks.json
│   ├── .mcp.json                        # studio → `rbxos studio-gateway`, rbxos → `rbxos mcp`
│   ├── .lsp.json                        # luau-lsp config (sourcemap from daemon)
│   ├── monitors/monitors.json
│   ├── workflows/{security-sweep,critic-panel,migrate,knowledge-verify,concept-divergence}.js
│   ├── bin/rbxos                        # tiny shim (sh + cmd) → verified binary in CLAUDE_PLUGIN_DATA
│   └── release-manifest.json            # pinned versions + checksums of binary/rbxm/knowledge
├── crates/                              # ── Rust workspace
│   ├── rbxos-cli/                       # main binary: subcommands, wiring
│   ├── rbxos-daemon/                    # actor runtime, project registry, job scheduler
│   ├── rbxos-proto/                     # generated types from schemas/, JSON-RPC envelopes
│   ├── rbxos-store/                     # SQLite access, migrations, CAS blob store
│   ├── rbxos-index/                     # full-moon + rbx-dom indexers, incremental pipeline
│   ├── rbxos-brain/                     # L2 model, clustering, graph query DSL
│   ├── rbxos-search/                    # lexicon expansion, BM25, graph re-rank
│   ├── rbxos-router/                    # classification, scoring, budgets, ledger
│   ├── rbxos-knowledge/                 # pack loader, K1 generator (API dump), verifier, probes
│   ├── rbxos-memory/                    # constitution/decisions/issues/lessons/journal I/O
│   ├── rbxos-policy/                    # tiers, AST screening, protected paths, confirmations
│   ├── rbxos-gateway/                   # StudioMCP proxy, interception, output shaping
│   ├── rbxos-mcp/                       # rbxos MCP server (rmcp), tool handlers
│   ├── rbxos-bridge/                    # WebSocket server, auth, capability RPC, chunking
│   ├── rbxos-versioning/                # changesets, checkpoints, snapshots, semantic diff, bisect, WAL
│   ├── rbxos-qa/                        # static rules engine, test orchestration, scenario compiler, gates
│   ├── rbxos-lab/                       # experiments, populations, analysis (bootstrap, sensitivity, ABC)
│   ├── rbxos-perf/                      # budgets, profile attribution, regressions
│   ├── rbxos-visual/                    # shots, SSIM/pHash, UI geometry audit, tiling
│   ├── rbxos-assets/                    # asset index, coverage, supply-chain scanner
│   ├── rbxos-cloud/                     # Open Cloud client (Luau Exec, publish, analytics, configs, experiments)
│   ├── rbxos-offline/                   # Lune runner, mirror .rbxl builder
│   ├── rbxos-hooks/                     # hook handlers (fast path, daemon client)
│   └── rbxos-doctor/                    # install/bootstrap/diagnostics
├── studio-plugin/                       # ── Companion plugin (Luau, Rojo project)
│   ├── default.project.json
│   ├── src/
│   │   ├── Bridge/       (WebStreamClient transport, auth, RPC dispatcher, chunking, reconnect)
│   │   ├── Capabilities/ (DmRead, DmWatch, DmWrite, Snapshot, Test, Net, Device, Capture,
│   │   │                  Input, Runtime, Profile, Debug, Logs, Ui)
│   │   ├── Policy/       (tier mirror, confirmations)
│   │   ├── Widget/       (dock status UI)
│   │   └── init.server.luau
│   └── tests/            (Jest-Lua specs)
├── runtime-lib/                         # ── injected into test DataModels only
│   ├── src/{Telemetry,Taps,Invariants,Feel,Perception,BotHost,Bots/*,Phantom,Fuzzer,DataStoreGuard,
│   │        ScenarioRunner,ConfigOverride}.luau
│   └── tests/
├── knowledge/                           # ── knowledge packs (source)
│   ├── engine/  studio/  luau/  patterns/  antipatterns/  rules/  boundary/
│   ├── design/{principles,fun-proxies,feel,slop,genres/,interactions/}
│   ├── probes/  (Luau probes referenced by claims)
│   └── lexicon/ (concept → API signal mappings for search)
├── schemas/                             # ── JSON Schema source of truth (see file 14)
├── sandbox/                             # Rojo projects for sandbox places used by probes/spikes
├── evals/                               # ── evaluation harness
│   ├── tasks/          (30+ scripted tasks across 3 reference games)
│   ├── search-queries/ (labeled "where is X" set)
│   ├── games/          (open-source Roblox games as fixtures, pinned)
│   └── plugin-evals/   (claude plugin eval cases: triggering, routing)
├── tests/
│   ├── fake-studio/    (simulated bridge + StudioMCP for CI without Studio)
│   └── e2e/            (requires Studio; run on self-hosted Win/mac runners)
├── docs/ (architecture/, user guide, contributor guide)
└── .github/workflows/ (build, test, release, knowledge-pack CI, nightly e2e)
```

### Per-game project layout added by RBXOS
Covered in file 06 §P.1 (`.rbxos/`). The only other changes are:
- ≤ 6 lines in `CLAUDE.md`
- `.claude/skills/roblox/SKILL.md` (the shim)
- a `.gitignore` entry
