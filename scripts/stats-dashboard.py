#!/usr/bin/env python3
"""stats-dashboard.py — cross-registry download/install stats for the bundle's skills.

Pulls per-skill public stats from the registries that expose them and prints a
combined table + totals. Owner utility (not a skill); Python stdlib only.

  ClawHub    GET https://clawhub.ai/api/v1/search?q=<slug>   -> downloads
  SkillHub   GET https://api.skillhub.cn/api/v1/skills/<slug> -> skill.stats
             (downloads / installs / stars)
  skills.sh  aggregate install total from the public badge SVG (no auth).
             Per-skill detail needs a Vercel OIDC token (401 unauthenticated);
             set SKILLS_SH_TOKEN to add a per-skill column, else only the total.

Usage:
  python3 scripts/stats-dashboard.py                 # markdown table to stdout
  python3 scripts/stats-dashboard.py --json          # machine-readable
  python3 scripts/stats-dashboard.py --out FILE.md   # also write markdown
  python3 scripts/stats-dashboard.py --badges DIR    # write shields.io endpoint JSONs

The --badges mode writes clawhub.json / skillhub.json / skillssh.json in the
shields.io "endpoint" schema so the README can render live-looking badges via
https://img.shields.io/endpoint?url=<raw-github-url>/badges/<platform>.json —
refreshed by a scheduled GitHub Action. A transient fetch failure (total 0)
keeps the previously committed value instead of zeroing the badge.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.parse, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
CLAWHUB_OWNER = "aaron-he-zhu"
SKILLHUB_OWNER = "user_2c0f1e77"
SKILLS_SH_TOKEN = os.environ.get("SKILLS_SH_TOKEN")


def _get(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "stats/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        return None


def clawhub(slug):
    d = _get(f"https://clawhub.ai/api/v1/search?q={urllib.parse.quote(slug)}")
    if not d:
        return None
    for r in d.get("results", []):
        if r.get("slug") == slug and r.get("ownerHandle") == CLAWHUB_OWNER:
            return {"downloads": r.get("downloads", 0)}
    return None


def skillhub(slug):
    d = _get(f"https://api.skillhub.cn/api/v1/skills/{urllib.parse.quote(slug)}")
    if not d or d.get("owner", {}).get("handle") != SKILLHUB_OWNER:
        return None
    st = d.get("skill", {}).get("stats", {}) or {}
    return {"downloads": st.get("downloads", 0), "installs": st.get("installs", 0),
            "stars": st.get("stars", 0)}


def skills_sh(owner, repo, slug):
    if not SKILLS_SH_TOKEN:
        return None
    d = _get(f"https://skills.sh/api/v1/skills/{owner}/{repo}/{slug}",
             headers={"Authorization": f"Bearer {SKILLS_SH_TOKEN}", "User-Agent": "stats/1.0"})
    return {"installs": d.get("installs", 0)} if d else None


def skills_sh_total(owner, repo):
    """Aggregate install count from the public badge SVG (no auth needed).
    Per-skill breakdowns require a Vercel OIDC token; the aggregate does not."""
    import re
    try:
        req = urllib.request.Request(f"https://skills.sh/b/{owner}/{repo}",
                                     headers={"User-Agent": "stats/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            svg = r.read().decode("utf-8", "ignore")
        m = re.search(r"<title>Skills:\s*([\d,]+)</title>", svg)
        return int(m.group(1).replace(",", "")) if m else None
    except Exception:
        return None


def main():
    names = [p[2:].split("/")[-1] for p in
             json.load(open(REPO / ".claude-plugin/plugin.json"))["skills"]]
    rows = []
    for n in names:
        ch = clawhub(n)
        time.sleep(0.2)
        sh = skillhub(n) or skillhub(f"aaron-{n}")
        time.sleep(0.2)
        ssh = skills_sh(CLAWHUB_OWNER, "aaron-marketing-skills", n)
        rows.append({
            "skill": n,
            "clawhub_downloads": (ch or {}).get("downloads", 0),
            "skillhub_downloads": (sh or {}).get("downloads", 0),
            "skillhub_installs": (sh or {}).get("installs", 0),
            "skillhub_stars": (sh or {}).get("stars", 0),
            "skillssh_installs": (ssh or {}).get("installs", 0),
        })
    for r in rows:
        r["total_downloads"] = r["clawhub_downloads"] + r["skillhub_downloads"]
    rows.sort(key=lambda r: r["total_downloads"], reverse=True)

    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    tot = lambda k: sum(r[k] for r in rows)
    ssh_total = skills_sh_total(CLAWHUB_OWNER, "aaron-marketing-skills")
    ssh_line = (f" · skills.sh installs (aggregate): **{ssh_total:,}**" if ssh_total is not None else "")
    out = ["# Skill stats — cross-registry snapshot", "",
           f"ClawHub downloads: **{tot('clawhub_downloads'):,}** · "
           f"SkillHub downloads: **{tot('skillhub_downloads'):,}** "
           f"(installs {tot('skillhub_installs'):,}, stars {tot('skillhub_stars'):,})"
           + ssh_line,
           "", "| Skill | ClawHub ↓ | SkillHub ↓ | SkillHub installs | ★ |",
           "|-------|-----------|------------|-------------------|---|"]
    for r in rows:
        out.append(f"| {r['skill']} | {r['clawhub_downloads']:,} | "
                   f"{r['skillhub_downloads']:,} | {r['skillhub_installs']:,} | {r['skillhub_stars']} |")
    text = "\n".join(out)
    print(text)
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            pathlib.Path(sys.argv[i + 1]).write_text(text + "\n", encoding="utf-8")
            print(f"\n[written to {sys.argv[i + 1]}]", file=sys.stderr)
        if a == "--badges" and i + 1 < len(sys.argv):
            write_badges(pathlib.Path(sys.argv[i + 1]),
                         tot("clawhub_downloads"), tot("skillhub_downloads"), ssh_total)


def _human(n):
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def write_badges(dirpath, clawhub, skillhub, skillssh):
    """Write shields.io endpoint-badge JSONs. A total of 0 (transient fetch
    failure) preserves the previously committed value so the badge never zeroes."""
    dirpath.mkdir(parents=True, exist_ok=True)
    specs = [
        ("clawhub.json", "ClawHub downloads", clawhub, "FF6B35"),
        ("skillhub.json", "SkillHub 下载", skillhub, "00A9A5"),
        ("skillssh.json", "skills.sh installs", skillssh, "0A0A0A"),
    ]
    for fname, label, value, color in specs:
        path = dirpath / fname
        if not value:  # 0 or None → keep prior committed value
            if path.exists():
                print(f"[badge {fname}: fetch was empty, kept existing]", file=sys.stderr)
                continue
            value = 0
        path.write_text(json.dumps({
            "schemaVersion": 1, "label": label, "message": _human(value), "color": color,
        }, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[badge {fname}: {_human(value)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
