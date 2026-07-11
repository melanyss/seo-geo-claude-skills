#!/usr/bin/env bash
# check-versions.sh — version-sync guard for the 10-surface tracking contract.
#
# CONTRIBUTING.md §6 requires the bundle version and every skill version to
# stay in sync across the typed system catalog, VERSIONS.md, plugin.json, both
# marketplace mirrors, root/localized README badges, and CLAUDE.md. Keeping
# these release surfaces aligned by
# hand is exactly the kind of mechanical step that drifts, so CI enforces it:
#
#   1. Bundle version (plugin.json) == every "version" field in both
#      marketplace.json mirrors == README + zh badge == "current bundle"
#      lines == CLAUDE.md declaration == VERSIONS.md "Current release" line,
#      and the changelog has a `### v<bundle>` entry.
#   2. Every SKILL.md: top-level `version` == `metadata.version` == its row
#      in the VERSIONS.md table (per-skill last-changed versioning means
#      rows may differ from the bundle — they must only match their skill).
#   3. VERSIONS.md has exactly one row per skill directory, none extra.
#   4. The GitHub About SSOT (.github/repo-about.json) leads with the current
#      skill count — the About is not a versioned file, so it silently drifted
#      on the v13/v14 discipline bumps; this keeps its count honest offline, and
#      scripts/sync-about.sh + about-drift.yml handle projecting/verifying it on GitHub.
#
# Bash + grep/sed/awk only (repo dependency policy). Exit 0 clean, 1 on any
# mismatch, with one FAIL line per finding.

set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"

fail=0
err() { echo "FAIL: $*" >&2; fail=1; }

# ---- 1. bundle-level sync ---------------------------------------------------
BUNDLE=$(sed -n 's/^  "version": "\([0-9][0-9.]*\)",$/\1/p' .claude-plugin/plugin.json | head -1)
if [ -z "$BUNDLE" ]; then
  err "cannot read bundle version from .claude-plugin/plugin.json"
else
  for f in marketplace.json .claude-plugin/marketplace.json; do
    vers=$(sed -n 's/.*"version": "\([0-9][0-9.]*\)".*/\1/p' "$f")
    # Fail CLOSED: a missing/renamed "version" key extracts nothing — that must
    # FAIL, not silently pass (a `grep -qv` on empty input returns no-match).
    if [ -z "$vers" ]; then
      err "$f has no readable \"version\" key (bundle-sync cannot verify)"
    else
      while read -r v; do
        [ "$v" = "$BUNDLE" ] || err "$f carries version $v != bundle $BUNDLE"
      done <<< "$vers"
    fi
  done
  catalog_bundle=$(sed -n 's/.*"bundle_version": "\([0-9][0-9.]*\)".*/\1/p' references/system-catalog.json | head -1)
  [ "$catalog_bundle" = "$BUNDLE" ] || err "references/system-catalog.json bundle_version $catalog_bundle != bundle $BUNDLE"
  grep -q "version-$BUNDLE-orange" README.md || err "README.md badge != $BUNDLE"
  grep -q "version-$BUNDLE-orange" docs/README.zh.md || err "docs/README.zh.md badge != $BUNDLE"
  # Full version-lock over the localized README set (owner decision 2026-07-05):
  # every translated README carries the machine-checkable version badge; the count
  # words in prose are human-maintained per release.
  for lf in docs/README.de.md docs/README.es.md docs/README.fr.md docs/README.it.md \
            docs/README.ja.md docs/README.ko.md docs/README.pt.md docs/README.zh-Hant.md; do
    [ -f "$lf" ] || { err "$lf missing (localized README set is version-locked)"; continue; }
    grep -q "version-$BUNDLE-orange" "$lf" || err "$lf badge != $BUNDLE"
  done
  grep -q "current bundle: \`$BUNDLE\`" README.md || err "README.md 'current bundle' line != $BUNDLE"
  grep -q "当前包：\`$BUNDLE\`" docs/README.zh.md || err "docs/README.zh.md 当前包 line != $BUNDLE"
  grep -q "Current bundle version: \`$BUNDLE\`" CLAUDE.md || err "CLAUDE.md bundle declaration != $BUNDLE"
  grep -q "^\*\*Current release\*\*: \`$BUNDLE\`" VERSIONS.md || err "VERSIONS.md 'Current release' line != $BUNDLE"
  grep -q "^### v$BUNDLE " VERSIONS.md || err "VERSIONS.md changelog entry '### v$BUNDLE …' missing"
  # openclaw.plugin.json is the OpenClaw bundle-plugin manifest (ClawHub package publish).
  # It carries the bundle version too — keep it in the version-lock so it can't drift.
  [ -f openclaw.plugin.json ] && { grep -q "\"version\": \"$BUNDLE\"" openclaw.plugin.json || err "openclaw.plugin.json version != $BUNDLE"; }
fi

# ---- 2. per-skill sync ------------------------------------------------------
skill_count=0
for f in seo-geo/*/*/SKILL.md influencer/*/*/SKILL.md ad/*/*/SKILL.md \
         email/*/*/SKILL.md launch/*/*/SKILL.md social/*/*/SKILL.md \
         narrative/*/*/SKILL.md protocol/*/SKILL.md; do
  [ -f "$f" ] || continue
  skill_count=$((skill_count + 1))
  name=$(sed -n 's/^name: *//p' "$f" | head -1)
  top=$(sed -n 's/^version: *"\([0-9][0-9.]*\)".*/\1/p' "$f" | head -1)
  # metadata is a single-line JSON object (OpenClaw parser requirement) —
  # pull its "version" member off the metadata: line
  meta=$(sed -n 's/^metadata: .*"version": *"\([0-9][0-9.]*\)".*/\1/p' "$f" | head -1)
  if [ -z "$name" ] || [ -z "$top" ]; then
    err "$f: missing name or top-level version"
    continue
  fi
  [ "$top" = "$meta" ] || err "$f: version \"$top\" != metadata.version \"$meta\""
  rowver=$(awk -F'|' -v s=" $name " '$2 == s {gsub(/ /,"",$4); print $4; exit}' VERSIONS.md)
  if [ -z "$rowver" ]; then
    err "$name: no row in VERSIONS.md"
  elif [ "$rowver" != "$top" ]; then
    err "$name: SKILL.md $top != VERSIONS.md row $rowver"
  fi
done

# ---- 3. row count -----------------------------------------------------------
rows=$(grep -cE '^\| [a-z0-9-]+ \| [a-z-]+ \| [0-9][0-9.]* \| ' VERSIONS.md)
[ "$rows" -eq "$skill_count" ] || \
  err "VERSIONS.md has $rows skill rows but the tree has $skill_count skills"

# ---- 4. GitHub About SSOT tracks the skill count ----------------------------
# The repo About (sidebar description + topics) is not a versioned file, so it is
# invisible to the checks above and drifted on the v13/v14 bumps. Its SSOT is
# .github/repo-about.json; its description MUST lead with the current skill count.
# Offline assertion (no network — the live projection/verify is sync-about.sh +
# about-drift.yml): the leading integer of the description == skill_count.
ABOUT=".github/repo-about.json"
if [ ! -f "$ABOUT" ]; then
  err "$ABOUT missing — the GitHub About SSOT (see scripts/sync-about.sh)"
else
  about_n=$(sed -n 's/.*"description":[[:space:]]*"\([0-9][0-9]*\).*/\1/p' "$ABOUT" | head -1)
  if [ -z "$about_n" ]; then
    err "$ABOUT: description must lead with the skill count (so this check can read it)"
  elif [ "$about_n" != "$skill_count" ]; then
    err "$ABOUT says $about_n skills but the tree has $skill_count — update it, then run: bash scripts/sync-about.sh --live"
  fi
fi

# ---- 5. auto-routing scenarios cover every command discipline ---------------
# references/auto-routing-scenarios.md is the runtime routing data commands/auto.md
# consults. It silently froze at the v12 four-discipline era (launch/social/narrative
# shipped with ZERO expected_route scenarios) — assert every command discipline keeps
# at least one routing scenario so a new discipline cannot ship uncovered again.
ROUTING="references/auto-routing-scenarios.md"
if [ ! -f "$ROUTING" ]; then
  err "$ROUTING missing — the /aaron-marketing:auto routing contract"
else
  for cmd in seo-geo influencer ad email launch social narrative; do
    grep -q "expected_route: \"/aaron-marketing:$cmd" "$ROUTING" \
      || err "$ROUTING has no expected_route scenario for /aaron-marketing:$cmd (auto routing coverage gap)"
  done
fi

# ---- 6. every discipline command Route names all its own skills -------------
# commands/<disc>.md is the human-facing skill catalog for its discipline. ad.md
# and email.md once listed only 2 of 4 skills per phase (and ad.md's Rules even
# claimed 3 real skills were "not separate skills"). Assert every skill physically
# under a discipline dir is named in that discipline's command, so a new skill
# cannot ship unlisted. (Protocol skills have no dedicated command — exempt.)
for disc in seo-geo influencer ad email launch social narrative; do
  cmd="commands/$disc.md"
  if [ ! -f "$cmd" ]; then err "$cmd missing — the $disc command"; continue; fi
  while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    grep -qw "$skill" "$cmd" \
      || err "$cmd Route does not name skill '$skill' (command coverage gap)"
  done < <(find "$disc" -name SKILL.md 2>/dev/null | sed 's#/SKILL.md##; s#.*/##' | sort -u)
done

if [ $fail -eq 0 ]; then
  echo "version-sync clean — bundle $BUNDLE, $skill_count skills consistent across the 10 tracking surfaces + localized badges + OpenClaw manifest + About SSOT; auto-routing covers all 7 disciplines; every discipline command lists its full skill set"
fi
exit $fail
