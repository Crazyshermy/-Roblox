#!/usr/bin/env bash
# Roblox Apex installer (macOS / Linux / Git Bash on Windows)
#
#   install/install.sh <project-dir>     install into <project-dir>/.claude/skills   (recommended)
#   install/install.sh --user            install into ~/.claude/skills (all projects on this machine)
#   install/install.sh --uninstall <project-dir> | --uninstall --user
#
# Re-running is the update path: previously installed Apex skills are replaced.
# Only directories recorded in the marker file are ever removed.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.claude/skills"
MARKER=".roblox-apex-installed"
VERSION="$(grep -m1 -E '^\s+version:' "$SRC/roblox/SKILL.md" | awk '{print $2}')"

usage() { sed -n '2,10p' "$0"; exit 1; }

uninstall=0
if [[ "${1:-}" == "--uninstall" ]]; then uninstall=1; shift; fi
case "${1:-}" in
  --user) DEST="$HOME/.claude/skills" ;;
  "") usage ;;
  *) [[ -d "$1" ]] || { echo "error: '$1' is not a directory" >&2; exit 1; }
     DEST="$(cd "$1" && pwd)/.claude/skills" ;;
esac

remove_previous() {
  if [[ -f "$DEST/$MARKER" ]]; then
    while IFS= read -r d; do
      [[ "$d" =~ ^roblox(-[a-z-]+)?$ ]] && rm -rf "${DEST:?}/$d"
    done < <(sed -n '2,$p' "$DEST/$MARKER")
    rm -f "$DEST/$MARKER"
  fi
}

if [[ $uninstall -eq 1 ]]; then
  [[ -f "$DEST/$MARKER" ]] || { echo "Roblox Apex is not installed in $DEST"; exit 0; }
  remove_previous
  echo "Removed Roblox Apex from $DEST (project files such as .apex/ and CLAUDE.md were left untouched)."
  exit 0
fi

if [[ "$(cd "$SRC/.." && pwd)" == "$(cd "$(dirname "$DEST")" 2>/dev/null && pwd || true)" ]]; then
  echo "This repository already contains the skills in .claude/skills; nothing to install here."; exit 0
fi

mkdir -p "$DEST"
remove_previous
for d in "$SRC"/roblox "$SRC"/roblox-*; do
  name="$(basename "$d")"
  if [[ -e "$DEST/$name" ]]; then
    echo "error: $DEST/$name exists and was not installed by Roblox Apex; move it and retry." >&2; exit 1
  fi
done
{ echo "$VERSION"; } > "$DEST/$MARKER"
for d in "$SRC"/roblox "$SRC"/roblox-*; do
  cp -R "$d" "$DEST/"
  basename "$d" >> "$DEST/$MARKER"
done
echo "Installed Roblox Apex $VERSION ($(($(wc -l < "$DEST/$MARKER") - 1)) skills) into $DEST"
echo "Next: open Claude Code in your project and run /roblox-status, then /roblox-init."
