# Upload or update with the Open Cloud Assets API

Read this only when the user asks for an API upload or update. Otherwise the user imports with the Importer (SKILL.md §4); Roblox's usage guide recommends the Importer for custom 3D models for its preview, error checks and settings. Tags are the same as in SKILL.md. Evidence: one 12-triangle plank, uploaded as a new Model and then updated to a second version, Oct 2026.

## Before the first call
- **Read the current docs** with the Studio MCP's `http_get`: `https://create.roblox.com/docs/cloud/guides/usage-assets.md` and `https://create.roblox.com/docs/en-us/reference/cloud/assets/v1.md`. Create and Update are beta endpoints (`${CLAUDE_SKILL_DIR}/../roblox/references/currency.md` → Assets).
- **API key:**
  - Use only the environment variable the user names.
  - Never print, log or write the key, and never put it on a command line. Check that it's present by its length only.
  - A variable set at Windows *user* scope after the session started isn't in the process environment. Read it at each call with `[Environment]::GetEnvironmentVariable('<NAME>','User')` [verified].
  - The key needs the **assets** API with Read and Write.
- **Creator ID:** ask the user for their user ID (or group ID); never guess it. Use it only inside the request, and keep it out of notes, skills and commits (grep for it before committing). Don't write asset IDs into the skill either.
- **Check the FBX first** (SKILL.md §3 and `fbx-check.md`). The API has no preview and no warning panel.

## Create a Model asset [verified]
```bash
KEY="$(powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('<NAME>','User')" | tr -d '\r\n')"
REQ='{"assetType":"Model","displayName":"<name>","description":"<text, no semicolons>","creationContext":{"creator":{"userId":"<user id>"},"expectedPrice":0}}'
printf 'x-api-key: %s\n' "$KEY" | /c/Windows/System32/curl.exe -sS -X POST "https://apis.roblox.com/assets/v1/assets" \
  -H @- -F "request=$REQ;type=application/json" -F "fileContent=@<asset>.fbx;type=model/fbx" \
  -o "<scratchpad>/create.json" -w 'HTTP %{http_code}\n'
unset KEY
```
- `-H @-` reads the header from stdin, so the key never appears in the process's arguments.
- `expectedPrice: 0` makes the call fail rather than charge a fee. No fee was charged.
- **A `;` anywhere in the request JSON ends the curl form field:** the call returns `400 Unterminated string` and nothing is created. Keep `;` out of names and descriptions.
- Git Bash's curl on the test machine was a debug build, so the Windows system `curl.exe` was used.
- **Poll the operation:**
  - The call returns `{"path":"operations/<id>","done":false}`.
  - Poll `GET https://apis.roblox.com/assets/v1/operations/<id>` every 3 s until `done` (PowerShell `Invoke-RestMethod`, with the key in a header hashtable read from the user scope).
  - Then read `response.assetId`, `revisionId` and `moderationResult.moderationState`. It was done within 3 s and Approved.
  - Mask the creator ID before printing a response.

## Insert into Studio and fix it [verified]
- **Studio MCP `insert_asset`** (by asset ID) inserted it as a **package**: a Model with a `PackageLink`. It landed at the camera's focus with a random yaw (−144° in the test) and carried an `Assistant:<guid>` CollectionService tag.
- **`InsertService:LoadAsset(<asset id>)`** in `execute_luau` returns the **latest revision** as a plain Model with **no** `PackageLink`. It's useful for temporary comparisons.
- **After either one:**
  - `model:PivotTo(CFrame.new(<position>))` stands it upright at the place you want;
  - check overlaps with `workspace:GetPartBoundsInBox`;
  - set Anchored, CollisionFidelity and the fallback `Color` (SKILL.md §5 a–b);
  - then run the §5 checks.

## Compared with the Importer [verified, one plank]
| | Importer (SKILL.md §4) | Open Cloud upload + insert |
|---|---|---|
| Size, scale, pivot at the base | as set | the same, with no settings (behaves like Studs, Front/Top) |
| Axis mapping, UVs, triangle count | — | identical |
| Texture | separate image, byte-identical | the same |
| Anchored | on (import setting) | **off**: set it |
| Rotation | 0,0,0 | **random yaw** from the insert: fix it |
| Package | no (default) | **always** (Model + PackageLink) |
| MeshId for unchanged geometry | reused on re-import | new for a new asset; reused between versions of one asset |
| Preview and warnings | yes | **none** |
| `Color`, `CollisionFidelity` | defaults | defaults |

## Update an existing asset with a new version [verified]
```bash
REQ='{"assetType":"Model","assetId":<asset id>,"creationContext":{"creator":{"userId":"<user id>"},"expectedPrice":0}}'
printf 'x-api-key: %s\n' "$KEY" | /c/Windows/System32/curl.exe -sS -X PATCH "https://apis.roblox.com/assets/v1/assets/<asset id>" \
  -H @- -F "request=$REQ;type=application/json" -F "fileContent=@<asset>.fbx;type=model/fbx" -o "<scratchpad>/patch.json" -w 'HTTP %{http_code}\n'
```
- No `updateMask` is needed for a content-only update; the docs say only Models (FBX) can have their content updated.
- It returns an operation like Create. It was done within 3 s as `revisionId` 2 of the **same** asset ID, Approved, and no new asset was made.
- The new version's texture was a new image with exact pixels; the mesh asset was reused because the geometry hadn't changed.
- **Placed copies don't update by themselves** [verified for ~100 s]:
  - A package copy placed from version 1 kept `PackageLink.VersionNumber` 1 and its old TextureID.
  - The docs say `AutoUpdate` defaults to false when a package is created. `AutoUpdate` and `Status` aren't readable from MCP `execute_luau` (they need RobloxScript), so that cause is inferred, not read. `VersionNumber` is readable.
- **To bring a placed copy up to date** [verified]:
  1. Insert the latest version fresh.
  2. Check that its `VersionNumber` is the new one and that its texture fingerprint matches the new PNG (`studio-checks.md` f).
  3. Only then delete the old copy, and put the new one at the old pivot with the same name and post-import settings.
  - Updating through Studio's package menu, or with AutoUpdate on: [untested].

## Not tested
Group creators, glTF or GLB uploads, metadata-only updates, version rollback, and keys restricted by IP.
