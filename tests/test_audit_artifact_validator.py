import importlib.util
import pathlib
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_validator", ROOT / "scripts" / "validate-audit-artifact.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def artifact(**overrides):
    values = {
        "framework": "ROAS",
        "profile": "direct-response",
        "status": "DONE",
        "verdict": "SHIP",
        "score_state": "SCORED",
        "coverage": 100,
        "confidence": "high",
        "veto_count": 0,
        "cap": "false",
        "raw": "80",
        "final": "final_overall_score: 80",
    }
    values.update(overrides)
    return textwrap.dedent(
        """\
        ---
        class: auditor-output
        schema_version: "3.0"
        runbook_version: "3.0.0"
        framework: {framework}
        profile: {profile}
        ---
        status: {status}
        verdict: {verdict}
        score_state: {score_state}
        objective: audit account
        target: account-1
        observed_at: 2026-07-10
        key_findings: []
        evidence_summary: export reviewed
        evidence_coverage: {coverage}
        score_confidence: {confidence}
        open_loops: none
        recommended_next_skill: paid-measurement-loop
        veto_count: {veto_count}
        cap_applied: {cap}
        raw_overall_score: {raw}
        {final}
        """
    ).format(**values)


class AuditArtifactValidatorTests(unittest.TestCase):
    def validate(self, text, relative="memory/audits/ad/test.md"):
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            return validator.validate(handle.name, relative)

    def test_valid_scored_artifact(self):
        record, errors = self.validate(artifact())
        self.assertEqual(errors, [])
        self.assertEqual(record["final_overall_score"], 80)

    def test_low_coverage_cannot_emit_score(self):
        _, errors = self.validate(artifact(coverage=99))
        self.assertTrue(any("coverage" in error for error in errors))

    def test_single_veto_cap_math_is_exact(self):
        valid = artifact(status="DONE_WITH_CONCERNS", verdict="FIX", veto_count=1,
                         cap="true", raw="80", final="final_overall_score: 59")
        valid = valid.replace(
            "key_findings: []",
            "key_findings:\n  - title: missing disclosure\n    severity: veto\n"
            "    evidence: paid relationship confirmed without disclosure",
        )
        self.assertEqual(self.validate(valid)[1], [])
        invalid = valid.replace("final_overall_score: 59", "final_overall_score: 60")
        self.assertTrue(any("one veto" in error for error in self.validate(invalid)[1]))

    def test_completed_block_is_not_execution_blocked(self):
        valid = artifact(verdict="BLOCK", veto_count=2, cap="false", raw="80", final="")
        valid = valid.replace(
            "key_findings: []",
            "key_findings:\n  - title: attribution mismatch\n    severity: veto\n"
            "    evidence: platform conversions do not reconcile\n"
            "  - title: policy violation\n    severity: veto\n"
            "    evidence: restricted claim is unsubstantiated",
        )
        self.assertEqual(self.validate(valid)[1], [])
        invalid = valid.replace("status: DONE", "status: BLOCKED")
        self.assertTrue(any("execution" in error for error in self.validate(invalid)[1]))

    def test_path_framework_ownership(self):
        _, errors = self.validate(artifact(framework="SEND"))
        self.assertTrue(any("requires framework ROAS" in error for error in errors))

    def test_profile_must_belong_to_framework(self):
        _, errors = self.validate(artifact(profile="newsletter"))
        self.assertTrue(any("not declared for framework ROAS" in error for error in errors))

    def test_unknown_fields_and_free_text_fail_closed(self):
        unknown = artifact().replace("framework: ROAS", "framework: ROAS\nextra: value")
        self.assertTrue(any("unknown frontmatter" in error for error in self.validate(unknown)[1]))
        prose = artifact() + "this prose is outside the deterministic body subset\n"
        self.assertTrue(any("not a scalar key/value" in error for error in self.validate(prose)[1]))

    def test_veto_count_requires_matching_findings(self):
        text = artifact(status="DONE_WITH_CONCERNS", verdict="FIX", veto_count=1,
                        cap="true", final="final_overall_score: 59")
        self.assertTrue(any("veto_count" in error for error in self.validate(text)[1]))

    def test_status_and_verdict_pairing_is_enforced(self):
        text = artifact(status="DONE", verdict="FIX")
        self.assertTrue(any("requires status DONE_WITH_CONCERNS" in error
                            for error in self.validate(text)[1]))

    def test_direct_audit_path_is_reserved_for_unscored_multi_summary(self):
        _, individual_errors = self.validate(artifact(), "memory/audits/result.md")
        self.assertTrue(any("only MULTI" in error for error in individual_errors))

        multi = artifact(
            framework="MULTI", profile="cross-framework-summary", status="DONE",
            verdict="UNDECIDED", score_state="NOT_SCORED", coverage=0,
            confidence="not_scored", veto_count=0, cap="false", raw="0", final="",
        )
        multi = multi.replace("raw_overall_score: 0\n", "")
        self.assertEqual(self.validate(multi, "memory/audits/2026-07.md")[1], [])


if __name__ == "__main__":
    unittest.main()
