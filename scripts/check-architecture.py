#!/usr/bin/env python3
"""Fail-closed architecture conformance checks for the v17 system catalog."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "system-catalog.json"
FRAMEWORK_PATH = ROOT / "references" / "framework-catalog.json"
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
GROUPINGS_PATH = ROOT / "skills.sh.json"
MARKETPLACE_PATHS = [ROOT / "marketplace.json", ROOT / ".claude-plugin" / "marketplace.json"]
REGISTRY_RUNTIME = ROOT / "scripts" / "registry-events.py"
LEGACY_COMPOSITE = re.compile(r"\b(?:LQS|SQS|NQS)\b|goal-weight(?:ed)? column", re.I)
LEGACY_SCORING = re.compile(r"min\s*\(\s*raw\s*,\s*60\s*\)|\bgoal[- /]?weight(?:s|ed)?\b|\bgoal column\b", re.I)
FAIL_OPEN_GATE = re.compile(r"unmarked.{0,80}(?:pass|allow|放行|通過|통과)", re.I)
MUTABLE_RUNTIME = re.compile(
    r"raw\.githubusercontent\.com/aaron-he-zhu/aaron-marketing-skills/(?:main|master)/references/",
    re.I,
)
AUDIT_WRITE_INTENT = re.compile(
    r"\b(?:write|writes|save|saves|persist|persists|store|stores|storable)\b|ready for",
    re.I,
)
AUDIT_WRITE_NEGATION = re.compile(r"\b(?:never|must not|does not|do not|reserved)\b", re.I)


class ArchitectureError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise ArchitectureError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ArchitectureError("%s has no frontmatter" % path.relative_to(ROOT))
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ArchitectureError("%s has unterminated frontmatter" % path.relative_to(ROOT)) from exc
    values = {}
    for line in lines[1:end]:
        matched = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if matched:
            values[matched.group(1)] = matched.group(2).strip().strip('"\'')
    metadata_line = next((line for line in lines[1:end] if line.startswith("metadata:")), None)
    if metadata_line is None:
        raise ArchitectureError("%s has no metadata" % path.relative_to(ROOT))
    try:
        metadata = json.loads(metadata_line.split(":", 1)[1].strip())
    except ValueError as exc:
        raise ArchitectureError("%s metadata is not strict JSON" % path.relative_to(ROOT)) from exc
    return values, metadata


def expected_skill_paths(catalog, failures):
    paths = []
    logical = catalog.get("logical_order", [])
    disciplines = catalog.get("disciplines", {})
    if logical != ["narrative", "seo-geo", "social", "email", "ad", "influencer", "launch", "protocol"]:
        failures.append("logical_order must preserve the canonical four-layer order")
    for discipline in logical:
        if discipline == "protocol":
            continue
        spec = disciplines.get(discipline)
        if not isinstance(spec, dict):
            failures.append("logical discipline %s is missing" % discipline)
            continue
        phases = spec.get("phase_order", [])
        if set(phases) != set(spec.get("phases", {})) or len(phases) != 4:
            failures.append("%s must declare exactly four ordered phases" % discipline)
        if spec.get("layer") not in {"L1", "L2", "L3"}:
            failures.append("%s has an invalid layer" % discipline)
        for phase in phases:
            slugs = spec["phases"].get(phase, [])
            if len(slugs) != 4 or len(slugs) != len(set(slugs)):
                failures.append("%s/%s must contain four unique skills" % (discipline, phase))
            paths.extend("%s/%s/%s" % (discipline, phase, slug) for slug in slugs)
    protocol = catalog.get("protocol", {}).get("skills", [])
    if len(protocol) != 8 or len(protocol) != len(set(protocol)):
        failures.append("protocol must contain eight unique skills")
    paths.extend("protocol/%s" % slug for slug in protocol)
    if len(paths) != len(set(paths)):
        failures.append("system catalog contains duplicate skill paths")
    return paths


def discover_skill_paths(catalog):
    paths = []
    for discipline in catalog.get("disciplines", {}):
        for skill_file in ROOT.glob("%s/*/*/SKILL.md" % discipline):
            paths.append(str(skill_file.parent.relative_to(ROOT)))
    for skill_file in ROOT.glob("protocol/*/SKILL.md"):
        paths.append(str(skill_file.parent.relative_to(ROOT)))
    return sorted(paths)


def check_catalog_shape(catalog, expected_paths, failures):
    required_top = {
        "$schema", "schema_version", "architecture_version", "bundle_version", "counts",
        "logical_order", "layers", "commands", "disciplines", "protocol", "registries",
        "auditors", "l1_dependency", "distribution_profiles",
    }
    if set(catalog) != required_top:
        failures.append("system catalog top-level keys differ from the strict contract")
    if catalog.get("$schema") != "./system-catalog.schema.json" or catalog.get("schema_version") != "1.0":
        failures.append("system catalog schema identity/version is invalid")
    counts = catalog.get("counts", {})
    actual = {
        "disciplines": len(catalog.get("disciplines", {})),
        "discipline_skills": len([path for path in expected_paths if not path.startswith("protocol/")]),
        "protocol_skills": len([path for path in expected_paths if path.startswith("protocol/")]),
        "total_skills": len(expected_paths),
        "commands": len(catalog.get("commands", [])),
        "registries": len(catalog.get("registries", [])),
        "auditors": len(catalog.get("auditors", [])),
    }
    if counts != actual:
        failures.append("catalog counts do not match catalog contents: expected %s, got %s" % (actual, counts))
    layers = catalog.get("layers", [])
    if [layer.get("id") for layer in layers] != ["L1", "L2", "L3", "L4"]:
        failures.append("layers must be ordered L1 through L4")
    flattened = [discipline for layer in layers for discipline in layer.get("disciplines", [])]
    if flattened != catalog.get("logical_order"):
        failures.append("layer discipline order must equal logical_order")


def check_skills(catalog, expected_paths, failures):
    discovered = discover_skill_paths(catalog)
    if sorted(expected_paths) != discovered:
        failures.append(
            "catalog/filesystem skill mismatch; missing=%s unknown=%s"
            % (sorted(set(expected_paths) - set(discovered)), sorted(set(discovered) - set(expected_paths)))
        )
    discipline_lookup = {}
    for discipline, spec in catalog["disciplines"].items():
        for phase, slugs in spec["phases"].items():
            for slug in slugs:
                discipline_lookup["%s/%s/%s" % (discipline, phase, slug)] = (discipline, phase, slug)
    for slug in catalog["protocol"]["skills"]:
        discipline_lookup["protocol/%s" % slug] = ("protocol", "protocol", slug)
    auditor_slugs = set()
    for path in expected_paths:
        skill_file = ROOT / path / "SKILL.md"
        if not skill_file.is_file():
            continue
        try:
            values, metadata = frontmatter(skill_file)
        except ArchitectureError as exc:
            failures.append(str(exc))
            continue
        discipline, phase, slug = discipline_lookup[path]
        if values.get("name") != slug:
            failures.append("%s frontmatter name does not match directory" % path)
        if metadata.get("discipline") != discipline or metadata.get("phase") != phase:
            failures.append("%s metadata discipline/phase drift" % path)
        if metadata.get("version") != values.get("version"):
            failures.append("%s top-level and metadata versions differ" % path)
        if values.get("class") == "auditor":
            auditor_slugs.add(slug)
    declared_auditors = {auditor["skill"] for auditor in catalog["auditors"]}
    if auditor_slugs != declared_auditors:
        failures.append("class: auditor set differs from catalog auditors")


def check_distribution(catalog, expected_paths, failures):
    plugin = load_json(PLUGIN_PATH)
    expected_plugin = ["./" + path for path in expected_paths]
    if plugin.get("skills") != expected_plugin:
        failures.append("plugin skill list must exactly follow system-catalog logical/phase order")
    if plugin.get("version") != catalog.get("bundle_version"):
        failures.append("system catalog bundle_version differs from plugin version")
    if plugin.get("commands") != ["./commands/"]:
        failures.append("plugin commands declaration must be ./commands/")
    commands = catalog.get("commands", [])
    actual_commands = sorted(path.stem for path in (ROOT / "commands").glob("*.md"))
    if sorted(commands) != actual_commands or len(commands) != len(set(commands)):
        failures.append("command files differ from catalog commands")
    groupings = load_json(GROUPINGS_PATH)
    grouped = [slug for group in groupings.get("groupings", []) for slug in group.get("skills", [])]
    expected_slugs = [path.rsplit("/", 1)[-1] for path in expected_paths]
    if grouped != expected_slugs or len(grouped) != len(set(grouped)):
        failures.append("skills.sh groupings must follow catalog order and cover every skill exactly once")
    for marketplace_path in MARKETPLACE_PATHS:
        marketplace = load_json(marketplace_path)
        plugins = marketplace.get("plugins", [])
        if len(plugins) != 1 or plugins[0].get("skills") != expected_plugin:
            failures.append("%s skill list must exactly follow catalog order" % marketplace_path.relative_to(ROOT))
        if plugins and plugins[0].get("description") != plugin.get("description"):
            failures.append("%s plugin description differs from plugin.json" % marketplace_path.relative_to(ROOT))
    if MARKETPLACE_PATHS[0].read_bytes() != MARKETPLACE_PATHS[1].read_bytes():
        failures.append("marketplace mirrors are not byte-identical")


def check_frameworks(catalog, failures):
    framework_catalog = load_json(FRAMEWORK_PATH)
    declared = {
        framework
        for discipline in catalog["disciplines"].values()
        for framework in discipline.get("frameworks", [])
    }
    actual = set(framework_catalog.get("frameworks", {}))
    if declared != actual or len(actual) != 8:
        failures.append("discipline frameworks and framework catalog differ")
    auditor_frameworks = {auditor["framework"] for auditor in catalog["auditors"]}
    if auditor_frameworks != actual:
        failures.append("every framework must have exactly one catalogued auditor")


def load_registry_runtime():
    spec = importlib.util.spec_from_file_location("registry_events", REGISTRY_RUNTIME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_registries(catalog, failures):
    runtime = load_registry_runtime()
    registries = catalog["registries"]
    keys = [entry["key"] for entry in registries]
    owners = {entry["key"]: entry["owner"] for entry in registries}
    if len(keys) != len(set(keys)) or set(keys) != runtime.REGISTRIES:
        failures.append("system catalog registry keys differ from runtime")
    if owners != runtime.OWNERS:
        failures.append("system catalog registry owners differ from runtime")
    protocol_skills = set(catalog["protocol"]["skills"])
    for entry in registries:
        key = entry["key"]
        owner = entry["owner"]
        if owner not in protocol_skills:
            failures.append("registry owner is not a protocol skill: %s" % owner)
        if entry.get("stream") != "memory/events/%s.ndjson" % key:
            failures.append("registry %s stream path is not canonical" % key)
        if entry.get("projection") != "memory/projections/%s.json" % key:
            failures.append("registry %s projection path is not canonical" % key)
        owner_path = ROOT / "protocol" / owner / "SKILL.md"
        text = owner_path.read_text(encoding="utf-8") if owner_path.is_file() else ""
        for token in (entry["stream"], "registry-events.py", "accept", "reject", "expected_revision", "verify"):
            if token not in text:
                failures.append("%s owner contract is missing %r" % (owner, token))
        machine = entry.get("state_machine")
        runtime_graph = runtime.TRANSITION_GRAPHS.get(key)
        if machine is None and runtime_graph is not None:
            failures.append("registry %s runtime state machine is absent from catalog" % key)
        elif machine is not None:
            expected_initial = {machine["initial"]}
            expected_graph = {state: set(targets) for state, targets in machine["transitions"].items()}
            if runtime_graph is None or runtime_graph.get(None) != expected_initial:
                failures.append("registry %s initial state differs from runtime" % key)
            elif {state: targets for state, targets in runtime_graph.items() if state is not None} != expected_graph:
                failures.append("registry %s transitions differ from runtime" % key)


def check_auditors(catalog, failures):
    seen_skills = set()
    seen_sinks = set()
    for auditor in catalog["auditors"]:
        skill = auditor["skill"]
        path = ROOT / auditor["path"] / "SKILL.md"
        if skill in seen_skills or auditor["sink"] in seen_sinks:
            failures.append("auditor skills and sinks must be one-to-one")
        seen_skills.add(skill)
        seen_sinks.add(auditor["sink"])
        if path.parent.name != skill or not path.is_file():
            failures.append("auditor path is invalid for %s" % skill)
            continue
        text = path.read_text(encoding="utf-8")
        runtime = path.parent / "references" / "auditor-runtime.md"
        for token in (
                "class: auditor", "references/auditor-runtime.md", auditor["sink"],
                "status", "verdict", "explicit", "validate-audit-artifact.py"):
            if token not in text:
                failures.append("%s contract is missing %r" % (skill, token))
        if not runtime.is_file() or "GENERATED FILE" not in runtime.read_text(encoding="utf-8")[:200]:
            failures.append("%s standalone runtime is missing or not generated" % skill)
        sinks = {"memory/audits/%s/" % match for match in re.findall(r"memory/audits/([^/\s`]+)/", text)}
        if sinks - {auditor["sink"]}:
            failures.append("%s references another auditor's write sink: %s" % (skill, sorted(sinks)))
        if MUTABLE_RUNTIME.search(text):
            failures.append("%s contains a mutable-main runtime fallback" % skill)


def check_l1_dependency(catalog, failures):
    dependency = catalog["l1_dependency"]
    required = dependency.get("required_fields", [])
    statuses = dependency.get("dependency_status_values", [])
    if required != ["narrative_canon_id", "narrative_canon_version", "claims_projection_offset", "dependency_status"]:
        failures.append("L1 dependency fields differ from the v17 contract")
    if statuses != ["verified", "approved-fallback", "blocked"]:
        failures.append("L1 dependency statuses differ from the v17 contract")
    builders = dependency.get("builders", [])
    if len(builders) != 7 or len(builders) != len(set(builders)):
        failures.append("L1 dependency must cover seven unique core builders")
    for path in builders:
        skill_path = ROOT / path / "SKILL.md"
        if not skill_path.is_file():
            failures.append("L1 builder path is missing: %s" % path)
            continue
        text = skill_path.read_text(encoding="utf-8")
        for token in required + statuses + [
                "memory/projections/narrative.json", "memory/projections/claims.json"]:
            if token.lower() not in text.lower():
                failures.append("L1 builder %s is missing dependency token %r" % (path, token))


def markdown_files():
    excluded_parts = {".git", ".planning", ".agents", ".codex", "reference-oss"}
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in excluded_parts for part in relative.parts):
            continue
        if re.search(r"(?:^| )\d+\.md$", path.name) or " 2" in path.name:
            continue
        yield path


def check_legacy_and_producers(catalog, failures):
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        if relative != "VERSIONS.md" and "candidates.md" in text:
            failures.append("legacy destructive candidate path remains in %s" % relative)
        if relative != "VERSIONS.md" and re.search(
                r"\bbatch-promote\b|\bday close\b|3\+ candidate", text, re.I):
            failures.append("legacy batch/threshold registry semantics remain in %s" % relative)
    normative = [
        "README.md", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md",
        "commands/ad.md", "commands/email.md", "commands/launch.md", "commands/social.md", "commands/narrative.md",
        "references/ramp-benchmark.md", "references/echo-benchmark.md", "references/tale-benchmark.md",
        "launch/mobilize/launch-readiness-auditor/SKILL.md",
        "social/host/social-quality-auditor/SKILL.md",
        "narrative/evaluate/narrative-quality-auditor/SKILL.md",
    ]
    normative.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / "docs").glob("README.*.md")))
    for relative in normative:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if LEGACY_COMPOSITE.search(text):
            failures.append("obsolete RAMP/ECHO/TALE composite terminology remains in %s" % relative)
        if LEGACY_SCORING.search(text):
            failures.append("obsolete scoring terminology remains in %s" % relative)
    readmes = [ROOT / "README.md", *sorted((ROOT / "docs").glob("README.*.md"))]
    for path in readmes:
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        if "path-triggered fail-closed Artifact Gate" not in text:
            failures.append("%s does not document the path-triggered fail-closed Artifact Gate" % relative)
        if FAIL_OPEN_GATE.search(text):
            failures.append("%s still documents a fail-open unmarked audit path" % relative)
    experiment_contracts = [
        ROOT / "ad" / "orchestrate" / "ad-test-designer" / "SKILL.md",
        ROOT / "email" / "deliver" / "send-experiment-designer" / "SKILL.md",
    ]
    for path in experiment_contracts:
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        for token in ("Calculated", "decision: UNDECIDED", "precommitted", "helper"):
            if token not in text:
                failures.append("%s experiment contract is missing %r" % (relative, token))
    compatibility = ROOT / "docs" / "agent-compatibility.md"
    if MUTABLE_RUNTIME.search(compatibility.read_text(encoding="utf-8")):
        failures.append("agent compatibility still prescribes mutable-main auditor runtime fallback")
    owner_paths = {"protocol/%s/SKILL.md" % entry["owner"] for entry in catalog["registries"]}
    auditor_paths = {auditor["path"] + "/SKILL.md" for auditor in catalog["auditors"]}
    skill_paths = [*ROOT.glob("*/*/*/SKILL.md"), *ROOT.glob("protocol/*/SKILL.md")]
    for skill_path in skill_paths:
        relative = str(skill_path.relative_to(ROOT))
        text = skill_path.read_text(encoding="utf-8")
        if relative not in auditor_paths:
            for line_number, line in enumerate(text.splitlines(), 1):
                audit_path = line.find("memory/audits/")
                prefix = line[max(0, audit_path - 180):audit_path] if audit_path >= 0 else ""
                if (audit_path >= 0 and AUDIT_WRITE_INTENT.search(prefix)
                        and not AUDIT_WRITE_NEGATION.search(prefix)):
                    failures.append(
                        "non-auditor declares an auditor-sink write: %s:%d"
                        % (relative, line_number)
                    )
        if relative not in owner_paths and "memory/events/" in text:
            if "registry-events.py" not in text or "operation: propose" not in text:
                failures.append("event producer lacks runtime/propose boundary: %s" % relative)


def main():
    failures = []
    try:
        catalog = load_json(CATALOG_PATH)
        expected_paths = expected_skill_paths(catalog, failures)
        check_catalog_shape(catalog, expected_paths, failures)
        check_skills(catalog, expected_paths, failures)
        check_distribution(catalog, expected_paths, failures)
        check_frameworks(catalog, failures)
        check_registries(catalog, failures)
        check_auditors(catalog, failures)
        check_l1_dependency(catalog, failures)
        check_legacy_and_producers(catalog, failures)
    except (ArchitectureError, OSError, ValueError, KeyError) as exc:
        failures.append("architecture check aborted safely: %s" % exc)
    if failures:
        print("ARCHITECTURE CONFORMANCE FAILED: %d issue(s)" % len(failures))
        for failure in failures:
            print("- " + failure)
        return 1
    print("architecture conformance clean: 4 layers, 7 disciplines, 120 skills, 8 auditors, 7 registries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
