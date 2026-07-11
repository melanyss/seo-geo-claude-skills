import importlib.util
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("registry_events", ROOT / "scripts" / "registry-events.py")
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)


def event(registry_name, key, aggregate_id="record-1", operation="upsert", **overrides):
    owner = registry.OWNERS[registry_name]
    value = {
        "schema_version": "1.0",
        "idempotency_key": key,
        "aggregate_id": aggregate_id,
        "operation": operation,
        "occurred_at": "2026-07-10T10:00:00Z",
        "actor": {"type": "skill", "id": owner},
        "authorized_by": "user",
        "authorization_ref": "explicit-test-approval",
        "source": {"type": "user-provided", "ref": "fixture", "observed_at": "2026-07-10"},
        "payload": {"set": {"title": "Fixture"}},
    }
    if operation in {"propose", "upsert", "transition", "tombstone", "restore", "erase"}:
        value["expected_revision"] = 0
    value.update(overrides)
    return value


class RegistryEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cli_append(self, registry_name, request_path):
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "registry-events.py"),
                "--root", str(self.root), "append", registry_name, str(request_path),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_proposal_acceptance_and_idempotent_retry(self):
        proposal = event(
            "entities", "proposal-1", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"title": "Acme"}},
        )
        first = registry.append_event(self.root, "entities", proposal)
        self.assertFalse(first["deduplicated"])
        self.assertIsNone(first["record"])
        retry = registry.append_event(self.root, "entities", proposal)
        self.assertTrue(retry["deduplicated"])
        state = registry.load_state(self.root, "entities")
        self.assertEqual(len(state["pending"]), 1)

        accept = event(
            "entities", "accept-1", operation="accept", payload={},
            proposal_event_id=first["event"]["event_id"],
        )
        accepted = registry.append_event(self.root, "entities", accept)
        self.assertEqual(accepted["record"]["revision"], 1)
        self.assertEqual(accepted["record"]["data"]["title"], "Acme")
        self.assertEqual(accepted["record"]["last_source"], proposal["source"])
        self.assertEqual(accepted["record"]["source_occurred_at"], proposal["occurred_at"])
        self.assertEqual(registry.load_state(self.root, "entities")["pending"], {})

    def test_reject_requires_reason_and_cannot_smuggle_mutation(self):
        proposal = registry.append_event(
            self.root,
            "entities",
            event(
                "entities", "proposal-reject", operation="propose",
                proposed_operation="upsert", actor={"type": "skill", "id": "content-writer"},
                payload={"set": {"title": "Unsubstantiated"}},
            ),
        )
        without_reason = event(
            "entities", "reject-without-reason", operation="reject", payload={},
            proposal_event_id=proposal["event"]["event_id"],
        )
        with self.assertRaisesRegex(registry.RegistryError, "requires payload.reason"):
            registry.append_event(self.root, "entities", without_reason)
        smuggled = event(
            "entities", "reject-with-mutation", operation="reject",
            payload={"reason": "unsupported", "set": {"title": "Still applied"}},
            proposal_event_id=proposal["event"]["event_id"],
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot carry a second mutation"):
            registry.append_event(self.root, "entities", smuggled)

    def test_idempotency_conflict_and_optimistic_revision(self):
        original = event("claims", "claim-write", payload={"set": {"status": "draft"}})
        registry.append_event(self.root, "claims", original)
        changed = event("claims", "claim-write", payload={"set": {"status": "approved"}})
        with self.assertRaisesRegex(registry.RegistryError, "idempotency"):
            registry.append_event(self.root, "claims", changed)
        stale = event(
            "claims", "claim-stale", expected_revision=0,
            payload={"set": {"status": "approved"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "stale expected_revision"):
            registry.append_event(self.root, "claims", stale)

    def test_concurrent_same_revision_has_one_winner(self):
        registry.append_event(
            self.root, "claims",
            event("claims", "claim-base", payload={"set": {"status": "draft"}}),
        )
        paths = []
        for index, status in enumerate(("approved", "rejected"), 1):
            path = self.root / ("concurrent-%d.json" % index)
            path.write_text(json.dumps(event(
                "claims", "claim-race-%d" % index, expected_revision=1,
                payload={"set": {"status": status}},
            )))
            paths.append(path)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda path: self.cli_append("claims", path), paths))
        self.assertEqual(sorted(result.returncode for result in results), [0, 1])
        self.assertTrue(any("stale expected_revision" in result.stderr for result in results))
        state = registry.load_state(self.root, "claims")
        self.assertEqual(state["records"]["record-1"]["revision"], 2)
        self.assertEqual(state["last_offset"], 2)

    def test_concurrent_identical_retry_is_idempotent(self):
        request = self.root / "same-event.json"
        request.write_text(json.dumps(event("entities", "parallel-identical")))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(
                lambda _: self.cli_append("entities", request), range(2)
            ))
        self.assertEqual([result.returncode for result in results], [0, 0])
        outputs = [json.loads(result.stdout) for result in results]
        self.assertEqual(sorted(output["deduplicated"] for output in outputs), [False, True])
        stream = self.root / "memory" / "events" / "entities.ndjson"
        self.assertEqual(len(stream.read_text().splitlines()), 1)

    def test_transition_compare_and_set(self):
        registry.append_event(
            self.root, "launches",
            event("launches", "launch-create", payload={"set": {"state": "draft"}}),
        )
        moved = event(
            "launches", "launch-move", operation="transition", expected_revision=1,
            payload={"transition": {"from": "draft", "to": "concept"}},
        )
        result = registry.append_event(self.root, "launches", moved)
        self.assertEqual(result["record"]["data"]["state"], "concept")
        wrong = event(
            "launches", "launch-wrong", operation="transition", expected_revision=2,
            payload={"transition": {"from": "draft", "to": "alpha"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "transition conflict"):
            registry.append_event(self.root, "launches", wrong)

    def test_transition_graph_rejects_jump_and_upsert_bypass(self):
        registry.append_event(
            self.root, "launches",
            event("launches", "launch-init", payload={"set": {"state": "draft"}}),
        )
        jump = event(
            "launches", "launch-jump", operation="transition", expected_revision=1,
            payload={"transition": {"from": "draft", "to": "general-availability"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "invalid launches transition"):
            registry.append_event(self.root, "launches", jump)
        bypass = event(
            "launches", "launch-bypass", expected_revision=1,
            payload={"set": {"state": "general-availability"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "later changes require transition"):
            registry.append_event(self.root, "launches", bypass)

    def test_channel_reactivation_path_is_explicit(self):
        registry.append_event(
            self.root, "channels",
            event("channels", "channel-init", payload={"set": {"state": "proposed"}}),
        )
        revision = 1
        for index, (source, target) in enumerate((
                ("proposed", "warming"), ("warming", "active"),
                ("active", "paused"), ("paused", "warming")), 1):
            result = registry.append_event(
                self.root, "channels",
                event(
                    "channels", "channel-step-%d" % index, operation="transition",
                    expected_revision=revision,
                    payload={"transition": {"from": source, "to": target}},
                ),
            )
            revision = result["record"]["revision"]
        self.assertEqual(result["record"]["data"]["state"], "warming")

    def test_consent_suppression_is_immediate_and_replay_safe(self):
        subject = "sha256-7d9f4b2a"
        suppress = event(
            "consent", "unsubscribe-1", aggregate_id=subject, operation="suppress",
            actor={"type": "data-subject", "id": subject},
            authorized_by="data-subject", authorization_ref="unsubscribe-click-evt-1",
            source={"type": "measured", "ref": "esp-webhook-evt-1", "observed_at": "2026-07-10"},
            payload={"reason": "unsubscribe"},
        )
        registry.append_event(self.root, "consent", suppress)
        self.assertTrue(registry.is_suppressed(self.root, subject))
        projection = json.loads((self.root / "memory/projections/consent-suppressions.json").read_text())
        self.assertIn(subject, projection["suppressed"])

        restore = event(
            "consent", "resubscribe-1", aggregate_id=subject, operation="restore",
            expected_revision=1,
            occurred_at="2026-07-11T10:00:00Z",
            payload={"reason": "new confirmed opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "doi-event-2",
            }},
        )
        registry.append_event(self.root, "consent", restore)
        self.assertFalse(registry.is_suppressed(self.root, subject))

    def test_consent_erasure_keeps_safety_tombstone(self):
        subject = "sha256-erasure-subject"
        erase = event(
            "consent", "erase-1", aggregate_id=subject, operation="erase",
            actor={"type": "data-subject", "id": subject}, authorized_by="data-subject",
            authorization_ref="subject-erasure-request-1",
            payload={"reason": "data subject erasure"},
        )
        result = registry.append_event(self.root, "consent", erase)
        self.assertEqual(result["record"]["data"], {})
        self.assertEqual(result["record"]["status"], "erased")
        self.assertTrue(registry.is_suppressed(self.root, subject))

    def test_consent_rejects_raw_pii(self):
        raw_email = "person" + "@" + "example.test"
        raw = event(
            "consent", "consent-raw-pii", operation="upsert",
            payload={"set": {"email": raw_email}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw PII"):
            registry.append_event(self.root, "consent", raw)
        raw_ref = event(
            "consent", "consent-source-pii", operation="upsert",
            source={"type": "user-provided", "ref": raw_email, "observed_at": "2026-07-10"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email"):
            registry.append_event(self.root, "consent", raw_ref)

    def test_non_owner_cannot_mutate_canonical_state(self):
        request = event(
            "channels", "bad-owner", actor={"type": "skill", "id": "social-calendar-builder"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "channel-registry"):
            registry.append_event(self.root, "channels", request)

    def test_canonical_mutations_and_proposals_require_revision(self):
        direct = event("entities", "missing-cas")
        direct.pop("expected_revision")
        with self.assertRaisesRegex(registry.RegistryError, "requires expected_revision"):
            registry.append_event(self.root, "entities", direct)

        proposal = event(
            "entities", "missing-proposal-cas", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "content-writer"},
        )
        proposal.pop("expected_revision")
        with self.assertRaisesRegex(registry.RegistryError, "requires expected_revision"):
            registry.append_event(self.root, "entities", proposal)

    def test_effective_operation_rejects_ambiguous_payloads(self):
        bad_proposal = event(
            "entities", "bad-transition-proposal", operation="propose",
            proposed_operation="transition", actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"state": "active"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "requires payload.transition"):
            registry.append_event(self.root, "entities", bad_proposal)

        no_op = event("entities", "empty-upsert", payload={"set": {}})
        with self.assertRaisesRegex(registry.RegistryError, "non-empty"):
            registry.append_event(self.root, "entities", no_op)

        smuggled = event(
            "launches", "transition-with-set", operation="transition",
            payload={"transition": {"from": None, "to": "draft"}, "set": {"title": "x"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot carry set or unset"):
            registry.append_event(self.root, "launches", smuggled)

    def test_restore_requires_prior_suppression_and_terminal_records_do_not_resurrect(self):
        restore = event(
            "consent", "restore-without-suppress", operation="restore",
            payload={"reason": "new opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "doi-1",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "existing suppressed"):
            registry.append_event(self.root, "consent", restore)

        registry.append_event(
            self.root, "entities",
            event("entities", "entity-tombstone", operation="tombstone",
                  payload={"reason": "retired"}),
        )
        resurrect = event(
            "entities", "entity-resurrect", expected_revision=1,
            payload={"set": {"title": "Back"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "terminal"):
            registry.append_event(self.root, "entities", resurrect)

    def test_replay_semantically_validates_rehashed_events(self):
        registry.append_event(self.root, "entities", event("entities", "semantic-base"))
        stream = self.root / "memory/events/entities.ndjson"
        stored = json.loads(stream.read_text())
        stored.pop("expected_revision")
        request = {key: stored[key] for key in registry.REQUEST_FIELDS if key in stored}
        stored["request_hash"] = registry.sha256_json(request)
        stored["event_hash"] = registry.event_hash(stored)
        stream.write_text(registry.canonical_json(stored) + "\n")
        with self.assertRaisesRegex(registry.RegistryError, "stored event is invalid"):
            registry.load_state(self.root, "entities")

    def test_hash_chain_detects_tampering(self):
        registry.append_event(self.root, "narrative", event("narrative", "canon-1"))
        stream = self.root / "memory/events/narrative.ndjson"
        stream.write_text(stream.read_text().replace("Fixture", "Tampered"))
        with self.assertRaisesRegex(registry.RegistryError, "hash mismatch"):
            registry.load_state(self.root, "narrative")

    def test_truncated_stream_fails_closed(self):
        registry.append_event(self.root, "narrative", event("narrative", "canon-valid"))
        stream = self.root / "memory/events/narrative.ndjson"
        with stream.open("a", encoding="utf-8") as handle:
            handle.write('{"registry":"narrative"')
        with self.assertRaisesRegex(registry.RegistryError, "invalid JSON"):
            registry.load_state(self.root, "narrative")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_symlinked_runtime_root_is_rejected(self):
        real_root = self.root / "real-project"
        real_root.mkdir()
        alias = self.root / "project-alias"
        alias.symlink_to(real_root, target_is_directory=True)
        with self.assertRaisesRegex(registry.RegistryError, "root cannot be a symlink"):
            registry.append_event(alias, "entities", event("entities", "alias-write"))

        safe_root = self.root / "safe-project"
        safe_root.mkdir()
        external_memory = self.root / "external-memory"
        external_memory.mkdir()
        (safe_root / "memory").symlink_to(external_memory, target_is_directory=True)
        with self.assertRaisesRegex(registry.RegistryError, "runtime path cannot be a symlink"):
            registry.append_event(safe_root, "entities", event("entities", "memory-alias"))

    def test_projection_can_be_rebuilt(self):
        registry.append_event(self.root, "creators", event("creators", "creator-1"))
        projection = self.root / "memory/projections/creators.json"
        projection.unlink()
        state = registry.rebuild_projection(self.root, "creators")
        self.assertEqual(state["last_offset"], 1)
        self.assertTrue(projection.exists())


if __name__ == "__main__":
    unittest.main()
