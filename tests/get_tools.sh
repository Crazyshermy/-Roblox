#!/usr/bin/env bash
# Fetch the external tools the test suite uses into tests/.tools/ (gitignored), Linux x64.
#   luau-compile  syntax checks (simulator, project benchmark)
#   rojo          rebuild tests/fixtures/LighthouseKeeper.rbxl
#   pwsh          run install.ps1 in tests/test_installers.sh (PowerShell 7; NOT Windows PowerShell 5.1)
#   creator-docs  sparse clone for tests/check_api.py
# Usage: tests/get_tools.sh   then e.g.  python3 tests/check_api.py tests/.tools/creator-docs
set -euo pipefail
T="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.tools"
mkdir -p "$T" && cd "$T"
LUAU_VER=0.650 ROJO_VER=7.4.4 PWSH_VER=7.5.3
[ -x luau-compile ] || { curl -sSfL -o luau.zip "https://github.com/luau-lang/luau/releases/download/$LUAU_VER/luau-ubuntu.zip" && unzip -oq luau.zip && rm luau.zip; }
[ -x rojo ] || { curl -sSfL -o rojo.zip "https://github.com/rojo-rbx/rojo/releases/download/v$ROJO_VER/rojo-$ROJO_VER-linux-x86_64.zip" && unzip -oq rojo.zip && rm rojo.zip; }
[ -x pwsh/pwsh ] || { mkdir -p pwsh && curl -sSfL "https://github.com/PowerShell/PowerShell/releases/download/v$PWSH_VER/powershell-$PWSH_VER-linux-x64.tar.gz" | tar xz -C pwsh && chmod +x pwsh/pwsh; }
if [ ! -d creator-docs ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Roblox/creator-docs.git creator-docs
  git -C creator-docs sparse-checkout set content/en-us/reference/engine content/en-us/cloud-services \
    content/en-us/projects content/en-us/scripting content/en-us/studio content/en-us/audio content/en-us/production
else
  git -C creator-docs pull -q --depth 1 || true
fi
chmod +x luau luau-compile luau-analyze rojo 2>/dev/null || true
echo "Tools ready in $T:"
./rojo --version; ./luau-compile --help >/dev/null 2>&1 && echo "luau-compile $LUAU_VER"; ./pwsh/pwsh -NoProfile -Command '"pwsh " + $PSVersionTable.PSVersion'
echo "creator-docs snapshot: $(git -C creator-docs log -1 --format=%cd)"
