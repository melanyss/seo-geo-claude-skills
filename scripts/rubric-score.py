#!/usr/bin/env python3
"""Deterministic scorer for the eight advisory marketing frameworks.

Input follows ``references/audit-run.schema.json``. No score is emitted until
every applicable item is observed. Unknown and missing items remain visible as
coverage gaps; N/A is accepted only for catalog-declared conditional items.
"""
from __future__ import annotations

import argparse
import datetime as dt
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import json
import math
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATALOG = os.path.join(ROOT, "references", "framework-catalog.json")
OBSERVED_STATES = {"pass", "partial", "fail"}
ALL_STATES = OBSERVED_STATES | {"unknown", "na"}
EVIDENCE_TYPES = {"measured", "user-provided", "calculated", "estimated", "proxy"}
CONFIDENCE = {"high", "medium", "low"}
RUN_FIELDS = {"framework", "profile", "target", "observed_at", "context", "items"}
ITEM_FIELDS = {"id", "state", "reason", "evidence"}
EVIDENCE_FIELDS = {"type", "source", "observed_at", "confidence"}


class RubricError(ValueError):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(
                handle,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: %s" % value)
                ),
            )
    except (OSError, ValueError) as exc:
        raise RubricError("cannot load %s: %s" % (path, exc)) from exc


def canonical_json_value(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError):
        return None


def item_ids(dimension):
    prefix = dimension["item_prefix"]
    width = int(dimension.get("id_width", 1))
    return [prefix + str(index).zfill(width) for index in range(1, int(dimension["item_count"]) + 1)]


def framework_item_ids(framework):
    result = set()
    for dimension in framework["dimensions"].values():
        result.update(item_ids(dimension))
    return result


def validate_catalog(catalog):
    errors = []
    if not isinstance(catalog, dict):
        return ["catalog must be an object"]
    frameworks = catalog.get("frameworks", {})
    expected_names = {"CORE-EEAT", "CITE", "C3", "ROAS", "SEND", "RAMP", "ECHO", "TALE"}
    if not isinstance(frameworks, dict) or set(frameworks) != expected_names:
        errors.append("catalog must contain exactly the eight frameworks")
        if not isinstance(frameworks, dict):
            return errors
    semantics = catalog.get("semantics", {})
    if not isinstance(semantics, dict):
        return errors + ["catalog semantics must be an object"]
    if semantics.get("score_states") != ["pass", "partial", "fail", "unknown", "na"]:
        errors.append("catalog score_states differ from the v17 contract")
    if semantics.get("item_points") != {"pass": 10, "partial": 5, "fail": 0}:
        errors.append("catalog item_points differ from the v17 contract")
    evidence_types = semantics.get("evidence_types", {})
    if not isinstance(evidence_types, dict) or set(evidence_types) != EVIDENCE_TYPES:
        errors.append("catalog evidence types differ from the v17 contract")
    confidence_factors = semantics.get("confidence_factors", {})
    if not isinstance(confidence_factors, dict) or set(confidence_factors) != CONFIDENCE:
        errors.append("catalog confidence factors differ from the v17 contract")
    if semantics.get("required_coverage") != 100:
        errors.append("v17 comparable scoring requires required_coverage=100")
    if semantics.get("veto_ceiling") != 59:
        errors.append("v17 universal veto ceiling must be 59")
    for name, framework in frameworks.items():
        if not isinstance(framework, dict):
            errors.append("%s framework must be an object" % name)
            continue
        required_context = framework.get("required_context", [])
        valid_context_keys = (
            isinstance(required_context, list) and bool(required_context)
            and all(isinstance(key, str) and key for key in required_context)
        )
        if not valid_context_keys or len(required_context) != len(set(required_context)):
            errors.append("%s required_context is invalid" % name)
            required_context = []
        dimensions = framework.get("dimensions", {})
        if not isinstance(dimensions, dict) or not dimensions:
            errors.append("%s has no valid dimensions" % name)
            continue
        known_ids = set()
        for dimension_name, dimension in dimensions.items():
            if not isinstance(dimension, dict):
                errors.append("%s/%s dimension must be an object" % (name, dimension_name))
                continue
            count = dimension.get("item_count")
            width = dimension.get("id_width", 1)
            prefix = dimension.get("item_prefix")
            if (not isinstance(count, int) or isinstance(count, bool) or count < 1
                    or not isinstance(width, int) or isinstance(width, bool) or width < 1
                    or not isinstance(prefix, str) or not prefix):
                errors.append("%s/%s has invalid item identity fields" % (name, dimension_name))
                continue
            ids = set(item_ids(dimension))
            if known_ids & ids:
                errors.append("%s dimensions produce duplicate item IDs" % name)
            known_ids.update(ids)
        profiles = framework.get("profiles", {})
        if not isinstance(profiles, dict) or not profiles:
            errors.append("%s has no profiles" % name)
            continue
        for profile, spec in profiles.items():
            if not isinstance(spec, dict):
                errors.append("%s/%s profile must be an object" % (name, profile))
                continue
            weights = spec.get("dimensions", {})
            if not isinstance(weights, dict) or not weights:
                errors.append("%s/%s has no dimensions" % (name, profile))
                continue
            if any(dimension not in dimensions for dimension in weights):
                errors.append("%s/%s references an unknown dimension" % (name, profile))
            numeric_weights = all(
                isinstance(weight, (int, float)) and not isinstance(weight, bool)
                and math.isfinite(weight) and weight > 0
                for weight in weights.values()
            )
            if not numeric_weights or abs(sum(weights.values()) - 1.0) > 1e-9:
                errors.append("%s/%s weights do not sum to 1" % (name, profile))
            context_equals = spec.get("context_equals", {})
            if not isinstance(context_equals, dict) or any(
                    key not in required_context for key in context_equals):
                errors.append("%s/%s has invalid context_equals" % (name, profile))
            for selector in ("include_items", "exclude_items"):
                selected = spec.get(selector, {})
                if not isinstance(selected, dict) or any(key not in weights for key in selected):
                    errors.append("%s/%s has invalid %s dimensions" % (name, profile, selector))
                    continue
                for ids in selected.values():
                    if (not isinstance(ids, list)
                            or not all(isinstance(item_id, str) for item_id in ids)
                            or len(ids) != len(set(ids))):
                        errors.append("%s/%s %s must contain unique item arrays" % (name, profile, selector))
                        continue
                    for item_id in ids:
                        if item_id not in known_ids:
                            errors.append("%s/%s %s has unknown item %s" % (name, profile, selector, item_id))
        context_allowed = framework.get("context_allowed", {})
        valid_allowed = isinstance(context_allowed, dict)
        if valid_allowed:
            for key, values in context_allowed.items():
                encoded = [canonical_json_value(value) for value in values] if isinstance(values, list) else []
                if (key not in required_context or not isinstance(values, list) or not values or None in encoded
                        or len(encoded) != len(set(encoded))):
                    valid_allowed = False
                    break
        if not valid_allowed:
            errors.append("%s has invalid context_allowed" % name)
        veto_items = framework.get("veto_items", [])
        if (not isinstance(veto_items, list)
                or not all(isinstance(item_id, str) for item_id in veto_items)
                or len(veto_items) != len(set(veto_items))):
            errors.append("%s veto_items must be a unique array" % name)
            veto_items = []
        for item_id in veto_items:
            if item_id not in known_ids:
                errors.append("%s veto item %s is unknown" % (name, item_id))
        policies = framework.get("item_policies", {})
        if not isinstance(policies, dict):
            errors.append("%s item_policies must be an object" % name)
            policies = {}
        for item_id, policy in policies.items():
            if item_id not in known_ids:
                errors.append("%s item policy %s is unknown" % (name, item_id))
            if not isinstance(policy, dict):
                errors.append("%s item policy %s must be an object" % (name, item_id))
                continue
            applicable_when = policy.get("applicable_when", {})
            if not isinstance(applicable_when, dict) or any(
                    key not in required_context for key in applicable_when):
                errors.append("%s item policy %s has invalid applicable_when" % (name, item_id))
        definitions = framework.get("item_definitions", {})
        if not isinstance(definitions, dict):
            errors.append("%s item_definitions must be an object" % name)
            definitions = {}
        for item_id in definitions:
            if item_id not in known_ids:
                errors.append("%s item definition %s is unknown" % (name, item_id))
    return errors


def expected_items(framework, profile):
    spec = framework["profiles"][profile]
    result = {}
    for dimension_name in spec["dimensions"]:
        ids = item_ids(framework["dimensions"][dimension_name])
        include = spec.get("include_items", {}).get(dimension_name)
        exclude = set(spec.get("exclude_items", {}).get(dimension_name, []))
        if include is not None:
            ids = list(include)
        result[dimension_name] = [item_id for item_id in ids if item_id not in exclude]
    return result


def parse_date(value, label, errors):
    if not isinstance(value, str):
        errors.append("%s must be an ISO date" % label)
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        errors.append("%s must be an ISO date" % label)
        return None


def evidence_strength(evidence, semantics):
    return (semantics["evidence_types"][evidence["type"]]
            * semantics["confidence_factors"][evidence["confidence"]])


def confidence_label(strengths):
    if not strengths:
        return "not_scored"
    average = sum(strengths) / len(strengths)
    if average >= 0.85:
        return "high"
    if average >= 0.65:
        return "medium"
    return "low"


def floor_cube_root(value):
    """Integer-corrected cube root, immune to float underflow at perfect cubes."""
    root = int(round(value ** (1.0 / 3.0)))
    while (root + 1) ** 3 <= value:
        root += 1
    while root ** 3 > value:
        root -= 1
    return root


def score_run(run, catalog):
    errors = validate_catalog(catalog)
    if errors:
        raise RubricError("invalid catalog: " + "; ".join(errors))
    if not isinstance(run, dict):
        raise RubricError("audit run must be an object")
    extra_run_fields = sorted(set(run) - RUN_FIELDS)
    if extra_run_fields:
        raise RubricError("unknown audit run fields: %s" % ", ".join(extra_run_fields))
    framework_name = run.get("framework")
    framework = catalog["frameworks"].get(framework_name)
    if framework is None:
        raise RubricError("unknown framework: %r" % framework_name)
    profile = run.get("profile")
    if profile not in framework["profiles"]:
        raise RubricError("unknown profile %r for %s" % (profile, framework_name))

    errors = []
    target_value = run.get("target")
    target = target_value.strip() if isinstance(target_value, str) else ""
    if not target:
        errors.append("target is required")
    observed_at = parse_date(run.get("observed_at", ""), "observed_at", errors)
    context = run.get("context")
    if not isinstance(context, dict):
        errors.append("context must be an object")
        context = {}
    for key in framework.get("required_context", []):
        if key not in context or context[key] in (None, "", []):
            errors.append("missing required context: %s" % key)
    for key, expected_value in framework["profiles"][profile].get("context_equals", {}).items():
        if context.get(key) != expected_value:
            errors.append(
                "context.%s must be %r for profile %s" % (key, expected_value, profile)
            )
    for key, allowed_values in framework.get("context_allowed", {}).items():
        if context.get(key) not in allowed_values:
            errors.append("context.%s must be one of %s" % (key, allowed_values))
    try:
        json.dumps(context, allow_nan=False)
    except (TypeError, ValueError):
        errors.append("context must contain finite JSON values")

    expected_by_dimension = expected_items(framework, profile)
    expected = {item_id for ids in expected_by_dimension.values() for item_id in ids}
    supplied = {}
    raw_items = run.get("items")
    if not isinstance(raw_items, list):
        errors.append("items must be an array")
        raw_items = []
    for position, item in enumerate(raw_items, 1):
        if not isinstance(item, dict):
            errors.append("items[%d] must be an object" % position)
            continue
        extra_item_fields = sorted(set(item) - ITEM_FIELDS)
        if extra_item_fields:
            errors.append(
                "items[%d] has unknown fields: %s" % (position, ", ".join(extra_item_fields))
            )
        item_id = item.get("id")
        if item_id not in expected:
            errors.append("item %r is not part of %s/%s" % (item_id, framework_name, profile))
            continue
        if item_id in supplied:
            errors.append("duplicate item: %s" % item_id)
            continue
        supplied[item_id] = item

    semantics = catalog["semantics"]
    points = semantics["item_points"]
    policies = framework.get("item_policies", {})
    veto_ids = set(framework.get("veto_items", []))
    normalized = {}
    strengths = []
    gaps = []
    veto_failures = []
    flags = []
    run_date = observed_at

    for item_id in sorted(expected):
        item = supplied.get(item_id, {"id": item_id, "state": "unknown", "reason": "not supplied"})
        state = item.get("state")
        if state not in ALL_STATES:
            errors.append("%s has invalid state %r" % (item_id, state))
            continue
        policy = policies.get(item_id, {})
        conditional = (
            policy.get("applicability") == "conditional"
            or bool(policy.get("applicable_when"))
            or profile in policy.get("na_profiles", [])
        )
        raw_reason = item.get("reason", "")
        if not isinstance(raw_reason, str):
            errors.append("%s reason must be a string" % item_id)
            reason = ""
        else:
            reason = raw_reason.strip()
        evidence = item.get("evidence")
        applicable_when = policy.get("applicable_when")
        context_applies = True
        if applicable_when:
            context_applies = all(context.get(key) == value for key, value in applicable_when.items())

        if state == "na":
            if not conditional:
                errors.append("%s cannot be N/A under the catalog" % item_id)
            if applicable_when and context_applies:
                errors.append("%s is applicable under the declared context and cannot be N/A" % item_id)
            if not reason:
                errors.append("%s N/A requires a reason" % item_id)
            if evidence is not None:
                errors.append("%s N/A must not carry evidence" % item_id)
            normalized[item_id] = {"state": state, "reason": reason}
            continue
        if applicable_when and not context_applies:
            errors.append("%s must be N/A outside its applicable context" % item_id)
        if state == "unknown":
            if item_id in supplied and not reason:
                errors.append("%s Unknown requires a gap reason" % item_id)
            if evidence is not None:
                errors.append("%s Unknown must not carry evidence" % item_id)
            gaps.append({"id": item_id, "reason": reason or "applicable evidence not observed"})
            normalized[item_id] = {"state": state, "reason": reason or "applicable evidence not observed"}
            continue

        if not isinstance(evidence, dict):
            errors.append("%s %s requires evidence" % (item_id, state))
            continue
        extra_evidence_fields = sorted(set(evidence) - EVIDENCE_FIELDS)
        if extra_evidence_fields:
            errors.append("%s evidence has unknown fields: %s" % (
                item_id, ", ".join(extra_evidence_fields)
            ))
        evidence_type = evidence.get("type")
        evidence_confidence = evidence.get("confidence")
        source_value = evidence.get("source")
        source = source_value.strip() if isinstance(source_value, str) else ""
        evidence_date = parse_date(evidence.get("observed_at", ""), "%s evidence.observed_at" % item_id, errors)
        if evidence_type not in EVIDENCE_TYPES:
            errors.append("%s has invalid evidence type" % item_id)
        if evidence_confidence not in CONFIDENCE:
            errors.append("%s has invalid evidence confidence" % item_id)
        if not source:
            errors.append("%s evidence source is required" % item_id)
        if run_date and evidence_date and evidence_date > run_date:
            errors.append("%s evidence date is after the audit observation date" % item_id)
        if evidence_type in EVIDENCE_TYPES and evidence_confidence in CONFIDENCE:
            strengths.append(evidence_strength(evidence, semantics))
        normalized[item_id] = {
            "state": state,
            "points": points[state],
            "evidence": evidence,
        }
        if state == "fail" and item_id in veto_ids:
            veto_failures.append(item_id)
        if state == "fail" and policy.get("fail_flag"):
            flags.append({"id": item_id, "flag": policy["fail_flag"]})

    if errors:
        raise RubricError("; ".join(sorted(set(errors))))

    dimension_scores = {}
    dimension_coverage = {}
    dimension_intervals = {}
    empty_dimensions = []
    total_expected = 0
    total_observed = 0
    for dimension_name, ids in expected_by_dimension.items():
        applicable = [item_id for item_id in ids if normalized[item_id]["state"] != "na"]
        observed = [item_id for item_id in applicable if normalized[item_id]["state"] in OBSERVED_STATES]
        total_expected += len(applicable)
        total_observed += len(observed)
        coverage = 0 if not applicable else math.floor(100 * len(observed) / len(applicable))
        dimension_coverage[dimension_name] = coverage
        observed_points = sum(normalized[item_id].get("points", 0) for item_id in observed)
        unknown_count = len(applicable) - len(observed)
        if applicable:
            lower = math.floor(observed_points / len(applicable) * 10)
            upper = math.floor((observed_points + unknown_count * 10) / len(applicable) * 10)
        else:
            lower, upper = 0, 100
            empty_dimensions.append(dimension_name)
            gaps.append({"id": dimension_name, "reason": "profile dimension has no applicable items"})
        dimension_intervals[dimension_name] = [lower, upper]
        if coverage == 100 and applicable:
            dimension_scores[dimension_name] = lower

    overall_coverage = 100 if total_expected == 0 else math.floor(100 * total_observed / total_expected)
    weights = framework["profiles"][profile]["dimensions"]
    lower_bound = math.floor(sum(dimension_intervals[name][0] * weight for name, weight in weights.items()))
    upper_bound = math.floor(sum(dimension_intervals[name][1] * weight for name, weight in weights.items()))
    complete = not empty_dimensions and overall_coverage == semantics["required_coverage"] and all(
        dimension_coverage[name] == semantics["required_coverage"] for name in weights
    )
    veto_count = len(veto_failures)
    result = {
        "schema_version": "3.0",
        "catalog_version": catalog["catalog_version"],
        "advisory": True,
        "external_validity": semantics["external_validity"],
        "framework": framework_name,
        "profile": profile,
        "target": target,
        "observed_at": run.get("observed_at"),
        "context": context,
        "score_state": "SCORED" if complete else "NOT_SCORED",
        "evidence_coverage": overall_coverage,
        "dimension_coverage": dimension_coverage,
        "score_interval": [lower_bound, upper_bound],
        "score_confidence": confidence_label(strengths) if complete else "not_scored",
        "veto_items_failed": sorted(veto_failures),
        "veto_count": veto_count,
        "flags": flags,
        "cap_applied": False,
        "gaps": gaps,
    }
    if not complete:
        result["status"] = "DONE" if veto_count >= 2 else "NEEDS_INPUT"
        result["verdict"] = "BLOCK" if veto_count >= 2 else "UNDECIDED"
        return result

    raw = math.floor(sum(dimension_scores[name] * weight for name, weight in weights.items()))
    result["dimension_scores"] = dimension_scores
    result["raw_overall_score"] = raw
    if veto_count >= 2:
        result.update({"status": "DONE", "verdict": "BLOCK"})
    elif veto_count == 1:
        result.update({
            "status": "DONE_WITH_CONCERNS",
            "verdict": "FIX",
            "cap_applied": True,
            "final_overall_score": min(raw, semantics["veto_ceiling"]),
        })
    else:
        any_fail = any(item["state"] == "fail" for item in normalized.values())
        final = raw
        result.update({
            "status": "DONE" if raw >= 75 and not any_fail else "DONE_WITH_CONCERNS",
            "verdict": "SHIP" if raw >= 75 and not any_fail else "FIX",
            "final_overall_score": final,
        })
    return result


def c3_rollup(payload):
    if not isinstance(payload, dict) or set(payload) - {"scopes", "components"}:
        raise RubricError("C3 rollup input must contain only scopes or components")
    if ("scopes" in payload) == ("components" in payload):
        raise RubricError("C3 rollup requires exactly one of scopes or components")
    if "scopes" in payload:
        scopes = payload["scopes"]
        if not isinstance(scopes, list) or len(scopes) != 3:
            raise RubricError("C3 scopes mode requires exactly three scored results")
        components = {"ace": [], "art": [], "roi": []}
        for result in scopes:
            prefix = str(result.get("profile", "")).split("-", 1)[0] if isinstance(result, dict) else ""
            if prefix not in components or components[prefix]:
                raise RubricError("C3 scopes mode requires one ACE, one ART, and one ROI result")
            components[prefix].append({"result": result})
    else:
        raw_components = payload["components"]
        if not isinstance(raw_components, dict) or set(raw_components) != {"ace", "art", "roi"}:
            raise RubricError("C3 components require exactly ace, art, and roi arrays")
        components = {}
        for scope, entries in raw_components.items():
            if not isinstance(entries, list) or not entries:
                raise RubricError("C3 %s components must be a non-empty array" % scope)
            if scope == "roi" and len(entries) != 1:
                raise RubricError("C3 components require exactly one ROI result")
            components[scope] = entries

    scores_by_scope = {"ace": [], "art": [], "roi": []}
    weights = []
    times = set()
    dates = set()
    goals = set()
    rollup_ids = set()
    catalog_versions = set()
    targets = {"ace": [], "art": [], "roi": []}
    for scope in ("ace", "art", "roi"):
        for entry in components[scope]:
            if not isinstance(entry, dict) or set(entry) - {"result", "weight"} or "result" not in entry:
                raise RubricError("C3 component entries require result and optional weight only")
            result = entry["result"]
            if not isinstance(result, dict) or result.get("framework") != "C3" or result.get("score_state") != "SCORED":
                raise RubricError("every C3 component must be a scored C3 result")
            profile_parts = str(result.get("profile", "")).split("-", 1)
            if len(profile_parts) != 2 or profile_parts[0] != scope:
                raise RubricError("C3 %s component must use an %s-* profile" % (scope, scope))
            goal = profile_parts[1]
            if goal not in {"awareness", "engagement", "conversion", "brand-building"}:
                raise RubricError("C3 component has an unknown goal profile")
            if "final_overall_score" not in result:
                raise RubricError("blocked C3 components cannot produce a CVI")
            value = result["final_overall_score"]
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                raise RubricError("C3 component scores must be integers from 0 to 100")
            context = result.get("context", {})
            if not isinstance(context, dict) or context.get("scope") != scope or context.get("goal") != goal:
                raise RubricError("C3 component profile and context must agree")
            target = result.get("target")
            if not isinstance(target, str) or not target.strip():
                raise RubricError("C3 component target is required")
            scores_by_scope[scope].append(value)
            targets[scope].append(target)
            times.add(context.get("assessment_time"))
            goals.add(goal)
            rollup_ids.add(context.get("rollup_id"))
            dates.add(result.get("observed_at"))
            catalog_versions.add(result.get("catalog_version"))

            if scope == "ace":
                raw_weight = entry.get("weight")
                if len(components["ace"]) > 1 and raw_weight is None:
                    raise RubricError("multiple ACE components require a positive budget weight")
                raw_weight = 1 if raw_weight is None else raw_weight
                if isinstance(raw_weight, bool):
                    raise RubricError("ACE component weight must be a positive finite number")
                try:
                    weight = Decimal(str(raw_weight))
                except (InvalidOperation, ValueError):
                    raise RubricError("ACE component weight must be a positive finite number")
                if not weight.is_finite() or weight <= 0:
                    raise RubricError("ACE component weight must be a positive finite number")
                weights.append(weight)
            elif "weight" in entry:
                raise RubricError("only ACE components accept budget weights; ART is equal-weighted")
    if len(times) != 1 or None in times:
        raise RubricError("C3 scopes must use the same assessment_time; forecast and actual cannot mix")
    if not times.issubset({"forecast", "actual"}):
        raise RubricError("C3 assessment_time must be forecast or actual")
    if len(dates) != 1:
        raise RubricError("C3 scopes must share one observation date")
    if len(goals) != 1:
        raise RubricError("C3 scopes must share one goal")
    if len(rollup_ids) != 1 or None in rollup_ids:
        raise RubricError("C3 scopes must share one rollup_id")
    if len(catalog_versions) != 1 or None in catalog_versions:
        raise RubricError("C3 scopes must share one catalog version")
    ace_numerator = sum(
        Decimal(value) * weight for value, weight in zip(scores_by_scope["ace"], weights)
    )
    ace_score = int((ace_numerator / sum(weights)).to_integral_value(rounding=ROUND_FLOOR))
    art_score = sum(scores_by_scope["art"]) // len(scores_by_scope["art"])
    roi_score = scores_by_scope["roi"][0]
    aggregate_scores = {"ace": ace_score, "art": art_score, "roi": roi_score}
    product = ace_score * art_score * roi_score
    return {
        "framework": "C3",
        "rollup": "CVI",
        "catalog_version": catalog_versions.pop(),
        "goal": goals.pop(),
        "rollup_id": rollup_ids.pop(),
        "assessment_time": times.pop(),
        "observed_at": dates.pop(),
        "scope_scores": aggregate_scores,
        "component_counts": {scope: len(values) for scope, values in scores_by_scope.items()},
        "component_targets": targets,
        "cvi": floor_cube_root(product),
        "advisory": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    score_parser = subparsers.add_parser("score", help="Score one typed audit run.")
    score_parser.add_argument("run")
    c3_parser = subparsers.add_parser("c3-rollup", help="Roll up three scored C3 scope results.")
    c3_parser.add_argument("results")
    subparsers.add_parser("check-catalog", help="Validate the framework catalog.")
    args = parser.parse_args(argv)
    try:
        catalog = load_json(args.catalog)
        if args.command == "check-catalog":
            errors = validate_catalog(catalog)
            if errors:
                raise RubricError("; ".join(errors))
            print("framework catalog valid: 8 frameworks")
            return 0
        if args.command == "score":
            output = score_run(load_json(args.run), catalog)
        else:
            output = c3_rollup(load_json(args.results))
    except RubricError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
