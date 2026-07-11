#!/usr/bin/env python3
"""Normalize and validate a Markdown auditor artifact against the v3 contract.

No PyYAML/jsonschema dependency is required: auditor artifacts intentionally use a
small, deterministic YAML subset. The companion JSON Schema documents the
normalized object for other hosts and future tooling.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys


SCHEMA_VERSION = "3.0"
RUNBOOK_VERSION = "3.0.0"
MIN_SCORE_COVERAGE = 100
VETO_CEILING = 59
FRAMEWORKS = {"CORE-EEAT", "CITE", "C3", "ROAS", "SEND", "RAMP", "ECHO", "TALE", "MULTI"}
STATUSES = {"DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_INPUT"}
VERDICTS = {"SHIP", "FIX", "BLOCK", "UNDECIDED"}
SCORE_STATES = {"SCORED", "NOT_SCORED"}
CONFIDENCE = {"high", "medium", "low", "not_scored"}
SEVERITIES = {"veto", "high", "medium", "low"}
PATH_FRAMEWORK = {
    "content": "CORE-EEAT",
    "domain": "CITE",
    "influencer": "C3",
    "ad": "ROAS",
    "email": "SEND",
    "launch": "RAMP",
    "social": "ECHO",
    "narrative": "TALE",
}
TOP_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
PROFILE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_CATALOG = ROOT / "references" / "framework-catalog.json"
FRONTMATTER_FIELDS = {
    "class", "schema_version", "runbook_version", "framework", "profile",
}
BODY_FIELDS = {
    "status", "verdict", "score_state", "objective", "target", "observed_at",
    "key_findings", "evidence_summary", "evidence_coverage", "score_confidence",
    "open_loops", "recommended_next_skill", "veto_count", "cap_applied",
    "raw_overall_score", "final_overall_score",
}
MULTI_PROFILE = "cross-framework-summary"


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except ValueError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def split_document(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines, ["missing YAML frontmatter"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, [], ["unterminated YAML frontmatter"]
    frontmatter = {}
    errors = []
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = TOP_KEY.match(line)
        if not match:
            errors.append("frontmatter line %d is not a scalar key/value" % number)
            continue
        key, value = match.groups()
        if key in frontmatter:
            errors.append("duplicate frontmatter field: %s" % key)
        frontmatter[key] = scalar(value)
    return frontmatter, lines[end + 1:], errors


def parse_findings(lines, start, inline):
    if inline.strip() == "[]":
        return [], start + 1, []
    if inline.strip():
        return [], start + 1, ["key_findings must be [] or a multiline list"]
    findings = []
    current = None
    errors = []
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if TOP_KEY.match(line):
            break
        item = re.match(r"^\s*-\s+title:\s*(.+)$", line)
        field = re.match(r"^\s+(severity|evidence):\s*(.+)$", line)
        if item:
            if current:
                findings.append(current)
            current = {"title": scalar(item.group(1))}
        elif field and current is not None:
            name = field.group(1)
            if name in current:
                errors.append("key_findings item has duplicate %s at line %d" % (name, index + 1))
            current[name] = scalar(field.group(2))
        elif line.strip() and not line.lstrip().startswith("#"):
            errors.append("unrecognized key_findings line %d" % (index + 1))
        index += 1
    if current:
        findings.append(current)
    if not findings:
        errors.append("key_findings is empty but not written as []")
    for pos, finding in enumerate(findings, 1):
        for field_name in ("title", "severity", "evidence"):
            if not str(finding.get(field_name, "")).strip():
                errors.append("key_findings item %d missing %s" % (pos, field_name))
        if finding.get("severity") not in SEVERITIES:
            errors.append("key_findings item %d has invalid severity" % pos)
    return findings, index, errors


def parse_body(lines):
    values = {}
    errors = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        match = TOP_KEY.match(line)
        if not match:
            errors.append("body line %d is not a scalar key/value" % (index + 1))
            index += 1
            continue
        key, inline = match.groups()
        if key in values:
            errors.append("duplicate body field: %s" % key)
        if key == "key_findings":
            findings, index, finding_errors = parse_findings(lines, index, inline)
            values[key] = findings
            errors.extend(finding_errors)
            continue
        values[key] = scalar(inline)
        index += 1
    return values, errors


def as_int(name, value, errors, minimum=0, maximum=None):
    if value is None or not re.fullmatch(r"-?\d+", str(value)):
        errors.append("%s must be an integer" % name)
        return None
    number = int(value)
    if number < minimum or (maximum is not None and number > maximum):
        errors.append("%s must be between %d and %d" % (name, minimum, maximum))
    return number


def as_bool(name, value, errors):
    if value not in ("true", "false"):
        errors.append("%s must be true or false" % name)
        return None
    return value == "true"


def load_framework_profiles():
    try:
        with FRAMEWORK_CATALOG.open(encoding="utf-8") as handle:
            catalog = json.load(handle)
        frameworks = catalog["frameworks"]
        if not isinstance(frameworks, dict):
            raise ValueError("frameworks must be an object")
        return {
            framework: set(specification.get("profiles", {}))
            for framework, specification in frameworks.items()
        }, None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {}, "cannot load framework profiles fail-closed: %s" % exc


def validate(path, relative_path=None):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        return None, ["cannot read artifact: %s" % exc]
    frontmatter, body_lines, errors = split_document(text)
    body, body_errors = parse_body(body_lines)
    errors.extend(body_errors)
    for name in sorted(set(frontmatter) - FRONTMATTER_FIELDS):
        errors.append("unknown frontmatter field: %s" % name)
    for name in sorted(set(body) - BODY_FIELDS):
        errors.append("unknown body field: %s" % name)
    record = dict(frontmatter)
    record.update(body)

    required_frontmatter = ("class", "schema_version", "runbook_version", "framework", "profile")
    required_body = (
        "status", "verdict", "score_state", "objective", "target", "observed_at",
        "key_findings", "evidence_summary", "evidence_coverage", "score_confidence",
        "open_loops", "recommended_next_skill", "veto_count", "cap_applied",
    )
    for name in required_frontmatter:
        if not str(frontmatter.get(name, "")).strip():
            errors.append("missing frontmatter field: %s" % name)
    for name in required_body:
        if name not in body or (name != "key_findings" and not str(body.get(name, "")).strip()):
            errors.append("missing body field: %s" % name)

    if frontmatter.get("class") != "auditor-output":
        errors.append("class must be auditor-output")
    if frontmatter.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be %s" % SCHEMA_VERSION)
    if frontmatter.get("runbook_version") != RUNBOOK_VERSION:
        errors.append("runbook_version must be %s" % RUNBOOK_VERSION)
    framework = frontmatter.get("framework")
    if framework not in FRAMEWORKS:
        errors.append("framework must name one of the eight frameworks")
    profile = frontmatter.get("profile", "")
    if profile and not PROFILE_RE.fullmatch(profile):
        errors.append("profile must be a lowercase hyphenated slug")
    profiles, profile_error = load_framework_profiles()
    if profile_error:
        errors.append(profile_error)
    elif framework == "MULTI":
        if profile != MULTI_PROFILE:
            errors.append("MULTI profile must be %s" % MULTI_PROFILE)
    elif framework in profiles and profile not in profiles[framework]:
        errors.append("profile %s is not declared for framework %s" % (profile, framework))

    status = body.get("status")
    verdict = body.get("verdict")
    score_state = body.get("score_state")
    if status not in STATUSES:
        errors.append("invalid status")
    if verdict not in VERDICTS:
        errors.append("invalid verdict")
    if score_state not in SCORE_STATES:
        errors.append("invalid score_state")
    if body.get("score_confidence") not in CONFIDENCE:
        errors.append("invalid score_confidence")
    try:
        dt.date.fromisoformat(str(body.get("observed_at", "")))
    except ValueError:
        errors.append("observed_at must be an ISO date")

    coverage = as_int("evidence_coverage", body.get("evidence_coverage"), errors, 0, 100)
    veto_count = as_int("veto_count", body.get("veto_count"), errors, 0)
    cap_applied = as_bool("cap_applied", body.get("cap_applied"), errors)
    raw = None
    final = None
    if "raw_overall_score" in body:
        raw = as_int("raw_overall_score", body.get("raw_overall_score"), errors, 0, 100)
    if "final_overall_score" in body:
        final = as_int("final_overall_score", body.get("final_overall_score"), errors, 0, 100)

    if relative_path:
        parts = relative_path.replace("\\", "/").split("/")
        if len(parts) >= 3 and parts[:2] == ["memory", "audits"]:
            if len(parts) == 3:
                if framework != "MULTI":
                    errors.append("only MULTI summaries may be stored directly under memory/audits/")
            else:
                expected = PATH_FRAMEWORK.get(parts[2])
                if expected is None:
                    errors.append("unknown auditor sink: %s" % parts[2])
                elif framework != expected:
                    errors.append("path %s requires framework %s" % (parts[2], expected))
                if framework == "MULTI":
                    errors.append("MULTI summaries belong directly under memory/audits/")

    veto_findings = sum(
        1 for finding in body.get("key_findings", [])
        if isinstance(finding, dict) and finding.get("severity") == "veto"
    )
    if veto_count is not None and veto_findings != veto_count:
        errors.append("veto_count must equal the number of veto key_findings")

    if framework == "MULTI":
        if score_state != "NOT_SCORED" or verdict != "UNDECIDED":
            errors.append("MULTI summaries require verdict UNDECIDED and NOT_SCORED")
        if veto_count not in (None, 0):
            errors.append("MULTI summaries must not aggregate veto_count")
        if cap_applied is not False:
            errors.append("MULTI summaries require cap_applied:false")
        if raw is not None or final is not None:
            errors.append("MULTI summaries must not emit a composite score")

    execution_stopped = status in {"BLOCKED", "NEEDS_INPUT"}
    if execution_stopped:
        if verdict != "UNDECIDED" or score_state != "NOT_SCORED":
            errors.append("execution BLOCKED/NEEDS_INPUT requires verdict UNDECIDED and NOT_SCORED")
        if raw is not None or final is not None:
            errors.append("an incomplete execution must not emit scores")
        if cap_applied is True:
            errors.append("an incomplete execution cannot apply a cap")
    elif score_state == "NOT_SCORED":
        if raw is not None or final is not None:
            errors.append("NOT_SCORED must omit raw/final scores")
        if body.get("score_confidence") != "not_scored":
            errors.append("NOT_SCORED requires score_confidence: not_scored")
        if verdict not in ({"BLOCK"} if veto_count is not None and veto_count >= 2 else {"UNDECIDED"}):
            errors.append("NOT_SCORED verdict is inconsistent with veto_count")
    elif score_state == "SCORED":
        if coverage is not None and coverage < MIN_SCORE_COVERAGE:
            errors.append("SCORED requires evidence_coverage >= %d" % MIN_SCORE_COVERAGE)
        if body.get("score_confidence") == "not_scored":
            errors.append("SCORED requires low/medium/high score_confidence")
        if raw is None:
            errors.append("SCORED requires raw_overall_score")
        if veto_count == 0:
            if cap_applied is not False or final != raw:
                errors.append("zero vetoes require cap_applied:false and final == raw")
            if verdict not in {"SHIP", "FIX"}:
                errors.append("zero vetoes require SHIP or FIX")
        elif veto_count == 1:
            expected_final = min(raw, VETO_CEILING) if raw is not None else None
            if cap_applied is not True or final != expected_final or verdict != "FIX":
                errors.append("one veto requires FIX and final=min(raw, %d)" % VETO_CEILING)
        elif veto_count is not None and veto_count >= 2:
            if cap_applied is not False or final is not None or verdict != "BLOCK":
                errors.append("two or more vetoes require BLOCK, no final score, and no cap")

    if framework != "MULTI":
        expected_status = {
            "SHIP": "DONE",
            "FIX": "DONE_WITH_CONCERNS",
            "BLOCK": "DONE",
        }.get(verdict)
        if expected_status is not None and status != expected_status:
            errors.append("verdict %s requires status %s" % (verdict, expected_status))
        if verdict == "UNDECIDED" and status not in {"BLOCKED", "NEEDS_INPUT"}:
            errors.append("verdict UNDECIDED requires status BLOCKED or NEEDS_INPUT")

    for name in ("objective", "target", "evidence_summary", "open_loops", "recommended_next_skill"):
        if name in body and not str(body[name]).strip():
            errors.append("%s must be non-empty" % name)

    if not errors:
        record["evidence_coverage"] = coverage
        record["veto_count"] = veto_count
        record["cap_applied"] = cap_applied
        if raw is not None:
            record["raw_overall_score"] = raw
        if final is not None:
            record["final_overall_score"] = final
    return record, sorted(set(errors))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact")
    parser.add_argument("--relative-path")
    parser.add_argument("--json", action="store_true", help="Print the normalized record.")
    args = parser.parse_args(argv)
    record, errors = validate(args.artifact, args.relative_path)
    if errors:
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
