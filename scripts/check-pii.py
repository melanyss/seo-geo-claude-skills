#!/usr/bin/env python3
"""PII / secret scanner — Python 3 stdlib only.

Ported (the detection half only) from common pre-commit secret scanners; the
vendor-attribution / CTA-block half is deliberately NOT included. Fails closed
on high-confidence secrets and non-allowlisted emails so credentials can't be
committed into this public skill library.

Scans repo text files (a filesystem walk minus SKIP_DIRS, by extension). Phone/IPv4
detection is intentionally omitted — a content/SEO repo is full of numbers and they
produce false positives. Allowlists are token/anchored, never whole-line, so a real
secret on a line that also contains a placeholder word is still caught.

Usage:
  python3 scripts/check-pii.py                 # scan the repo (CI gate; exit 1 on finding)
  python3 scripts/check-pii.py path [path ...] # scan specific paths
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_EXTS = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".txt", ".js", ".ts"}
SKIP_DIRS = {".git", "reference-oss", "node_modules", "__pycache__", ".agents", ".claude"}

# High-confidence secret patterns (name, regex).
PATTERNS = [
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained PAT", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{24,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("URL-embedded credentials", re.compile(r"\b[a-z][a-z0-9+.\-]*://[^/\s:@]+:[^/\s:@]+@")),
    ("US SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]

EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
# Email allowlist is ANCHORED, not substring: a full placeholder local-part OR an allowlisted domain.
# (A substring test would leak a real address whose local-part merely ENDS in user/name/test/you.)
EMAIL_LOCAL_ALLOW = {"user", "name", "test", "you", "noreply", "example", "email"}
EMAIL_DOMAIN_ALLOW = ("example.com", "example.org", "example.net", "anthropic.com",
                      "your-domain.com", "yourdomain.com", "zhuhe.io")  # zhuhe.io = project public contact
# Exact-address allowlist — the strongest anchor: the WHOLE address must match.
# For fixture placeholders whose domains can't be domain-allowed (gmail.com /
# outlook.com carry real mail — a domain allow would exempt real addresses) and
# for third parties' own published public contacts.
EMAIL_FULL_ALLOW = {
    # connector test/docstring fixtures (tests/, scripts/connectors/resend.py,
    # email/deliver/inbox-placement-monitor/) — provider domains are the point
    # of seed-list examples, so they can't be rewritten to example.com
    "me@x.dev", "a@y.com", "me@my.dom", "r@my.dom", "me@my.domain",
    "s1@gmail.com", "s2@outlook.com", "seed1@gmail.com", "seed2@outlook.com",
    # published public contact of agentskills.me (docs/registry-submissions.md)
    "hi@evergreenai.cn",
    # Product Hunt's own published API-terms contact (their ToS requires naming
    # it for business-use requests — quoted in producthunt.py + CONNECTORS.md)
    "hello@producthunt.com",
}
# Placeholder fragments that exonerate a matched SECRET-LIKE TOKEN — applied to the matched token ONLY,
# never the whole line (whole-line skipping would let a real key on a "placeholder"/"example" line slip).
TOKEN_PLACEHOLDER = ("xxxx", "redacted", "placeholder", "example", "akiaiosfodnn7example", "your-token")


def _email_allowed(email):
    lowered = email.lower()
    if lowered in EMAIL_FULL_ALLOW:
        return True
    local, _, domain = lowered.partition("@")
    return local in EMAIL_LOCAL_ALLOW or domain in EMAIL_DOMAIN_ALLOW


def _token_allowed(tok):
    t = tok.lower()
    return any(frag in t for frag in TOKEN_PLACEHOLDER)


def scan_file(path):
    findings = []
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        # Fail-closed visibility: a file we cannot read must not silently pass the
        # gate. Surface it on stderr so the skipped file is visible in CI logs.
        print("WARN  could not read %s: %s" % (os.path.relpath(path, ROOT), e), file=sys.stderr)
        return findings
    for n, line in enumerate(text.splitlines(), 1):
        for name, pat in PATTERNS:
            for m in pat.finditer(line):
                if _token_allowed(m.group(0)):
                    continue
                findings.append((n, name, line.strip()[:120]))
        for m in EMAIL.finditer(line):
            if not _email_allowed(m.group(0)):
                findings.append((n, "email address", m.group(0)))
    return findings


def iter_targets(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in SCAN_EXTS:
                    yield os.path.join(dirpath, fn)


def main():
    paths = sys.argv[1:] or [ROOT]
    total = 0
    for f in iter_targets(paths):
        for n, name, snippet in scan_file(f):
            total += 1
            print("FAIL  %s:%d  %s  ::  %s" % (os.path.relpath(f, ROOT), n, name, snippet))
    if total:
        print("\nPII/SECRET SCAN FAILED — %d finding(s). Redact or add to the allowlist if a false positive." % total)
        return 1
    print("PII/secret scan clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
