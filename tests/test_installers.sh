#!/usr/bin/env bash
# Installer matrix for install.sh and (if pwsh is available) install.ps1:
# install, re-install (update), conflict refusal, user-level install, uninstall.
# Usage: tests/test_installers.sh [path-to-pwsh]
# Note: pwsh here is PowerShell 7. Windows PowerShell 5.1 is not covered by this test.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PWSH="${1:-$(command -v pwsh || true)}"
fail=0
check() { if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fail=1; fi; }

run_matrix() {  # $1 = label, $2 = install cmd prefix for project, $3 = user flag, $4 = uninstall flag style
  local label="$1" T H
  T=$(mktemp -d); H=$(mktemp -d)
  mkdir -p "$T/.claude/skills/my-own-skill"
  eval "$2 \"$T\"" >/dev/null 2>&1
  check "$label install: 22 skills + marker" "[ \$(ls -d \"$T\"/.claude/skills/roblox* | wc -l) -eq 22 ] && [ -f \"$T/.claude/skills/.roblox-apex-installed\" ]"
  check "$label install: user's own skill untouched" "[ -d \"$T/.claude/skills/my-own-skill\" ]"
  eval "$2 \"$T\"" >/dev/null 2>&1
  check "$label update (re-install) keeps 22 skills" "[ \$(ls -d \"$T\"/.claude/skills/roblox* | wc -l) -eq 22 ]"
  eval "$4 \"$T\"" >/dev/null 2>&1
  check "$label uninstall removes only Apex" "[ -z \"\$(ls -d \"$T\"/.claude/skills/roblox* 2>/dev/null)\" ] && [ -d \"$T/.claude/skills/my-own-skill\" ]"
  mkdir -p "$T/.claude/skills/roblox"
  eval "$2 \"$T\"" >/dev/null 2>&1
  check "$label refuses to overwrite a foreign 'roblox' folder" "[ ! -f \"$T/.claude/skills/.roblox-apex-installed\" ]"
  HOME="$H" USERPROFILE="$H" eval "$3" >/dev/null 2>&1
  check "$label user-level install" "[ \$(ls -d \"$H\"/.claude/skills/roblox* 2>/dev/null | wc -l) -eq 22 ]"
}

run_matrix "bash" "\"$REPO/install/install.sh\"" "\"$REPO/install/install.sh\" --user" "\"$REPO/install/install.sh\" --uninstall"
if [ -n "$PWSH" ]; then
  P="\"$PWSH\" -NoProfile -File \"$REPO/install/install.ps1\""
  run_matrix "pwsh" "$P -Project" "$P -User" "_u(){ $P -Project \"\$1\" -Uninstall; }; _u"
else
  echo "SKIP  pwsh not found (install.ps1 untested)"
fi
exit $fail
