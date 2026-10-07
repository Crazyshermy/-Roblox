# Fresh-install test (ref `claude/modest-knuth-iewvlg`, model sonnet)

| check | result | detail |
|---|---|---|
| project: install.sh | PASS | Installed Roblox Apex 1.2.0 (22 skills) into /tmp/apex-game-12ba0tc_/.claude/skills |
| project: all 22 skills discovered in fresh session | PASS | 22 discovered |
| project: /roblox-status reports version + complete inventory | PASS | ``` Roblox Apex 1.2.0 Inventory: complete   (install: project)   roblox: disk ✓, discovered ✓   roblox-architecture: dis |
| project: /roblox-route names security+data+networking | PASS |  |
| project: /roblox-route does not execute (no specialist loaded) | PASS | [] |
| project: /roblox-init created .apex/ memory | PASS | ['project.md', 'decisions.md', 'debt.md'] |
| project: /roblox-init added CLAUDE.md block | PASS |  |
| project: auto-routing (no prefix) loads an architecture/networking specialist | PASS | ['roblox', 'roblox-architecture', 'roblox-networking'] |
| project: CLAUDE.md + .apex memory consulted | PASS | ['.apex/project.md', '.apex/decisions.md', 'src/server/Main.server.luau', 'src/server/LampService.luau', 'src/shared/Config.luau', 'src/client/HUD.client.luau'] |
| project: /roblox routes security review to roblox-security | PASS | ['roblox-security'] |
| project: security review finds negative/untrusted amount | PASS |  |
| plugin: marketplace add + install from GitHub | PASS | e: roblox-apex (declared in user settings) Installing plugin "roblox-apex@roblox-apex"...√ Successfully installed plugin: roblox-apex@roblox-apex (scope: user)  |
| plugin: skills discovered (namespaced) | PASS | 22 |
| plugin: bare /roblox-status works and reports complete inventory | PASS | ``` Roblox Apex 1.2.0 Inventory: complete   (install: plugin)   roblox: disk ✓, discovered ✓   roblo |
| plugin: auto-routing reaches namespaced security skill | PASS | ['roblox-apex:roblox-security'] |

Session cost: $0.75
