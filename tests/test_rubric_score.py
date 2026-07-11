import copy
import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rubric_score", ROOT / "scripts" / "rubric-score.py")
score = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score)
CATALOG = json.loads((ROOT / "references" / "framework-catalog.json").read_text())


def evidence(kind="measured", confidence="high"):
    return {
        "type": kind,
        "source": "own export fixture",
        "observed_at": "2026-07-10",
        "confidence": confidence,
    }


def complete_run(framework="ROAS", profile="direct-response", context=None, state="pass"):
    spec = CATALOG["frameworks"][framework]
    if context is None:
        context = {key: "fixture" for key in spec.get("required_context", [])}
        context.update(spec["profiles"][profile].get("context_equals", {}))
        if framework == "C3":
            context["assessment_time"] = "actual"
    items = []
    for ids in score.expected_items(spec, profile).values():
        items.extend({"id": item_id, "state": state, "evidence": evidence()} for item_id in ids)
    return {
        "framework": framework,
        "profile": profile,
        "target": "fixture-target",
        "observed_at": "2026-07-10",
        "context": context,
        "items": items,
    }


class CatalogTests(unittest.TestCase):
    def test_catalog_is_valid(self):
        self.assertEqual(score.validate_catalog(CATALOG), [])

    def test_catalog_contains_eight_frameworks(self):
        self.assertEqual(len(CATALOG["frameworks"]), 8)

    def test_malformed_catalog_fails_closed_without_crashing(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["frameworks"]["ROAS"]["profiles"]["direct-response"]["dimensions"]["R"] = "invalid"
        errors = score.validate_catalog(catalog)
        self.assertTrue(errors)
        self.assertTrue(any("weights do not sum to 1" in error for error in errors))


class RubricScoreTests(unittest.TestCase):
    def test_complete_roas_run_scores_and_ships(self):
        result = score.score_run(complete_run(), CATALOG)
        self.assertEqual(result["score_state"], "SCORED")
        self.assertEqual(result["final_overall_score"], 100)
        self.assertEqual(result["verdict"], "SHIP")
        self.assertEqual(result["evidence_coverage"], 100)

    def test_missing_item_is_unknown_and_prevents_total(self):
        run = complete_run()
        run["items"].pop()
        result = score.score_run(run, CATALOG)
        self.assertEqual(result["score_state"], "NOT_SCORED")
        self.assertEqual(result["verdict"], "UNDECIDED")
        self.assertNotIn("raw_overall_score", result)
        self.assertLess(result["evidence_coverage"], 100)

    def test_na_requires_catalog_permission_and_reason(self):
        run = complete_run("SEND", "newsletter")
        e2 = next(item for item in run["items"] if item["id"] == "E2")
        e2.clear()
        e2.update({"id": "E2", "state": "na", "reason": "opens are not used"})
        self.assertEqual(score.score_run(run, CATALOG)["score_state"], "SCORED")
        required = next(item for item in run["items"] if item["id"] == "E1")
        required.clear()
        required.update({"id": "E1", "state": "na", "reason": "not available"})
        with self.assertRaisesRegex(score.RubricError, "cannot be N/A"):
            score.score_run(run, CATALOG)

    def test_single_veto_caps_at_59(self):
        run = complete_run()
        item = next(item for item in run["items"] if item["id"] == "R1")
        item["state"] = "fail"
        result = score.score_run(run, CATALOG)
        self.assertEqual(result["veto_count"], 1)
        self.assertEqual(result["verdict"], "FIX")
        self.assertEqual(result["final_overall_score"], 59)

    def test_multi_veto_blocks_without_execution_failure(self):
        run = complete_run()
        for item in run["items"]:
            if item["id"] in {"R1", "R2"}:
                item["state"] = "fail"
        result = score.score_run(run, CATALOG)
        self.assertEqual(result["status"], "DONE")
        self.assertEqual(result["verdict"], "BLOCK")
        self.assertNotIn("final_overall_score", result)

    def test_incomplete_multi_veto_still_has_completed_block_status(self):
        run = complete_run()
        for item in run["items"]:
            if item["id"] in {"R1", "R2"}:
                item["state"] = "fail"
        run["items"].pop()
        result = score.score_run(run, CATALOG)
        self.assertEqual(result["score_state"], "NOT_SCORED")
        self.assertEqual((result["status"], result["verdict"]), ("DONE", "BLOCK"))

    def test_required_framework_context_is_enforced(self):
        run = complete_run("CITE", "default")
        del run["context"]["peer_cohort"]
        with self.assertRaisesRegex(score.RubricError, "peer_cohort"):
            score.score_run(run, CATALOG)

    def test_ramp_profiles_do_not_mix_time_horizons(self):
        preflight = complete_run("RAMP", "preflight")
        ids = {item["id"] for item in preflight["items"]}
        self.assertIn("P1", ids)
        self.assertNotIn("P2", ids)
        self.assertIn("M1", ids)
        self.assertNotIn("M2", ids)
        outcome = complete_run("RAMP", "outcome")
        outcome_ids = {item["id"] for item in outcome["items"]}
        self.assertNotIn("P1", outcome_ids)
        self.assertIn("P10", outcome_ids)

    def test_echo_asset_gate_contains_only_asset_relevant_controls(self):
        run = complete_run("ECHO", "asset-gate")
        ids = {item["id"] for item in run["items"]}
        self.assertEqual(len(ids), 14)
        self.assertTrue({"E1", "C1", "C10", "H1", "H2", "O1"}.issubset(ids))
        self.assertNotIn("E2", ids)
        self.assertNotIn("H3", ids)
        self.assertEqual(score.score_run(run, CATALOG)["score_state"], "SCORED")

    def test_all_na_weighted_dimension_never_crashes_or_renormalizes(self):
        catalog = copy.deepcopy(CATALOG)
        catalog["frameworks"]["ECHO"]["item_policies"]["O1"]["na_profiles"] = ["asset-gate"]
        run = complete_run("ECHO", "asset-gate")
        o1 = next(item for item in run["items"] if item["id"] == "O1")
        o1.clear()
        o1.update({"id": "O1", "state": "na", "reason": "fixture"})
        result = score.score_run(run, catalog)
        self.assertEqual(result["score_state"], "NOT_SCORED")
        self.assertEqual(result["dimension_coverage"]["O"], 0)

    def test_c3_rollup_rejects_forecast_actual_mixing(self):
        scopes = []
        for profile in ("ace-awareness", "art-awareness", "roi-awareness"):
            run = complete_run("C3", profile, context={
                "scope": profile.split("-", 1)[0],
                "goal": "awareness",
                "assessment_time": "actual",
                "rollup_id": "campaign-1",
            })
            scopes.append(score.score_run(run, CATALOG))
        rollup = score.c3_rollup({"scopes": scopes})
        self.assertEqual(rollup["cvi"], 100)
        mixed = copy.deepcopy(scopes)
        mixed[-1]["context"]["assessment_time"] = "forecast"
        with self.assertRaisesRegex(score.RubricError, "cannot mix"):
            score.c3_rollup({"scopes": mixed})

    def test_profile_context_must_match(self):
        run = complete_run("SEND", "newsletter")
        run["context"]["program_type"] = "promotional"
        with self.assertRaisesRegex(score.RubricError, "must be 'newsletter'"):
            score.score_run(run, CATALOG)

    def test_unknown_fields_and_ambiguous_unknown_fail_closed(self):
        run = complete_run()
        run["surprise"] = True
        with self.assertRaisesRegex(score.RubricError, "unknown audit run fields"):
            score.score_run(run, CATALOG)

        run = complete_run()
        run["items"][0]["extra"] = "ignored-before-v17"
        with self.assertRaisesRegex(score.RubricError, "unknown fields"):
            score.score_run(run, CATALOG)

        run = complete_run()
        item = run["items"][0]
        item["state"] = "unknown"
        with self.assertRaisesRegex(score.RubricError, "Unknown requires a gap reason"):
            score.score_run(run, CATALOG)

    def test_c3_forecast_requires_actual_only_items_to_be_na(self):
        run = complete_run("C3", "roi-awareness")
        run["context"]["assessment_time"] = "forecast"
        actual_only = {"ROI.R1", "ROI.R2", "ROI.I1", "ROI.I2", "ROI.I3"}
        for item in run["items"]:
            if item["id"] in actual_only:
                item_id = item["id"]
                item.clear()
                item.update({"id": item_id, "state": "na", "reason": "forecast read"})
        self.assertEqual(score.score_run(run, CATALOG)["score_state"], "SCORED")

    def test_c3_roi_attribution_failure_emits_results_unverified_flag(self):
        run = complete_run("C3", "roi-conversion")
        next(item for item in run["items"] if item["id"] == "ROI.I3")["state"] = "fail"
        result = score.score_run(run, CATALOG)
        self.assertEqual(result["flags"], [{"id": "ROI.I3", "flag": "results-unverified"}])

    def test_c3_rollup_requires_same_goal_and_rollup_identity(self):
        scopes = []
        for profile in ("ace-awareness", "art-awareness", "roi-awareness"):
            scopes.append(score.score_run(complete_run("C3", profile), CATALOG))
        wrong_goal = copy.deepcopy(scopes)
        wrong_goal[1]["profile"] = "art-engagement"
        wrong_goal[1]["context"]["goal"] = "engagement"
        with self.assertRaisesRegex(score.RubricError, "share one goal"):
            score.c3_rollup({"scopes": wrong_goal})
        wrong_campaign = copy.deepcopy(scopes)
        wrong_campaign[2]["context"]["rollup_id"] = "campaign-2"
        with self.assertRaisesRegex(score.RubricError, "share one rollup_id"):
            score.c3_rollup({"scopes": wrong_campaign})

    def test_c3_components_aggregate_ace_by_budget_and_art_equally(self):
        def result(profile, value, target):
            scored = score.score_run(complete_run("C3", profile), CATALOG)
            scored["target"] = target
            scored["raw_overall_score"] = value
            scored["final_overall_score"] = value
            return scored

        payload = {"components": {
            "ace": [
                {"result": result("ace-awareness", 60, "creator-a"), "weight": 1},
                {"result": result("ace-awareness", 100, "creator-b"), "weight": 3},
            ],
            "art": [
                {"result": result("art-awareness", 80, "asset-a")},
                {"result": result("art-awareness", 100, "asset-b")},
            ],
            "roi": [{"result": result("roi-awareness", 70, "campaign-1")}],
        }}
        rolled = score.c3_rollup(payload)
        self.assertEqual(rolled["scope_scores"], {"ace": 90, "art": 90, "roi": 70})
        self.assertEqual(rolled["component_counts"], {"ace": 2, "art": 2, "roi": 1})
        self.assertEqual(rolled["cvi"], 82)

        missing_weight = copy.deepcopy(payload)
        del missing_weight["components"]["ace"][0]["weight"]
        with self.assertRaisesRegex(score.RubricError, "require a positive budget weight"):
            score.c3_rollup(missing_weight)

    def test_evidence_date_cannot_be_in_the_future_of_the_run(self):
        run = complete_run()
        run["items"][0]["evidence"]["observed_at"] = "2026-07-11"
        with self.assertRaisesRegex(score.RubricError, "after the audit"):
            score.score_run(run, CATALOG)


if __name__ == "__main__":
    unittest.main()
