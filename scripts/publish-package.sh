#!/usr/bin/env bash
# publish-package.sh — publish the whole plugin to ClawHub as an OpenClaw
# bundle-plugin package.
#
# Publishes from the current pushed HEAD via the GitHub source (owner/repo@sha),
# NOT the local folder: `clawhub package publish .` ignores .gitignore and would
# bundle .git, local settings, and any stray worktree. A GitHub source is a
# git-archive of committed files only. Name/version/display come from
# openclaw.plugin.json + .claude-plugin/plugin.json. Dry-run by default.
#
# Usage:
#   bash scripts/publish-package.sh            # dry-run: show the file set + metadata
#   bash scripts/publish-package.sh --live     # publish
#
# Requires: openclaw.plugin.json committed at HEAD, HEAD pushed to origin, and the
# `clawhub` CLI logged in. Owner-run, never CI. See docs/distribution.md.
set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"

LIVE=0
case "${1:-}" in
  --live) LIVE=1 ;;
  ""|--dry-run) LIVE=0 ;;
  -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
  *) echo "usage: $0 [--live]" >&2; exit 1 ;;
esac

command -v clawhub >/dev/null 2>&1 || { echo "FAIL: clawhub CLI not found/logged in" >&2; exit 2; }
[ -f openclaw.plugin.json ] || { echo "FAIL: openclaw.plugin.json missing at repo root" >&2; exit 1; }

REPO_SLUG=$(git remote get-url origin 2>/dev/null | sed -E 's#(git@[^:]+:|https?://[^/]+/)##; s#\.git$##')
OWNER="${REPO_SLUG%%/*}"
COMMIT=$(git rev-parse HEAD)
VER=$(/usr/bin/python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")
NAME=$(/usr/bin/python3 -c "import json;print(json.load(open('openclaw.plugin.json'))['id'])")
DISPLAY=$(/usr/bin/python3 -c "import json;d=json.load(open('openclaw.plugin.json'));print(d.get('name',d['id']))")

# guardrails: manifest committed at HEAD, HEAD pushed, manifest version == bundle
git cat-file -e "HEAD:openclaw.plugin.json" 2>/dev/null || { echo "FAIL: openclaw.plugin.json is not committed at HEAD $COMMIT — commit it first" >&2; exit 1; }
git fetch -q origin 2>/dev/null || true
if ! git merge-base --is-ancestor "$COMMIT" origin/main 2>/dev/null; then
  echo "FAIL: HEAD $COMMIT is not on origin/main — push it first (GitHub source publish needs it live)" >&2; exit 1
fi
mv="$(/usr/bin/python3 -c "import json;print(json.load(open('openclaw.plugin.json'))['version'])")"
[ "$mv" = "$VER" ] || { echo "FAIL: openclaw.plugin.json version $mv != bundle $VER" >&2; exit 1; }

echo "Package : $NAME@$VER  (family bundle-plugin, owner $OWNER)"
echo "Source  : github:$REPO_SLUG@$COMMIT"
echo "Mode    : $([ $LIVE -eq 1 ] && echo LIVE || echo dry-run)"

cmd=(clawhub package publish "$REPO_SLUG@$COMMIT"
     --family bundle-plugin --name "$NAME" --display-name "$DISPLAY"
     --owner "$OWNER" --version "$VER"
     --changelog "aaron-marketing bundle-plugin @ $VER — 120 skills + 8 commands, seven disciplines + protocol layer.")
[ "$LIVE" -eq 0 ] && cmd+=(--dry-run)

"${cmd[@]}"
