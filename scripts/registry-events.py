#!/usr/bin/env python3
"""Append-only, idempotent event runtime for the seven truth registries."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised only on non-POSIX hosts
    fcntl = None


SCHEMA_VERSION = "1.0"
REGISTRIES = {"entities", "creators", "claims", "consent", "launches", "channels", "narrative"}
OWNERS = {
    "entities": "entity-optimizer",
    "creators": "creator-registry",
    "claims": "offer-claims-registry",
    "consent": "consent-registry",
    "launches": "launch-registry",
    "channels": "channel-registry",
    "narrative": "narrative-registry",
}
OPERATIONS = {"propose", "accept", "reject", "upsert", "transition", "tombstone", "suppress", "restore", "erase"}
PROPOSED_OPERATIONS = {"upsert", "transition", "tombstone"}
REQUEST_FIELDS = {
    "schema_version", "idempotency_key", "aggregate_id", "operation",
    "proposed_operation", "proposal_event_id", "occurred_at", "actor",
    "authorized_by", "authorization_ref", "source", "expected_revision", "payload",
}
ASSIGNED_EVENT_FIELDS = {
    "registry", "event_id", "offset", "recorded_at", "request_hash",
    "previous_hash", "event_hash",
}
TRANSITION_GRAPHS = {
    "channels": {
        None: {"proposed"},
        "proposed": {"warming", "retired"},
        "warming": {"active", "paused", "retired"},
        "active": {"paused", "retired"},
        "paused": {"warming", "retired"},
        "retired": set(),
    },
    "launches": {
        None: {"draft"},
        "draft": {"concept"},
        "concept": {"alpha"},
        "alpha": {"beta"},
        "beta": {"general-availability"},
        "general-availability": {"archived"},
        "archived": set(),
    },
}
SOURCE_TYPES = {"measured", "user-provided", "calculated", "estimated", "proxy"}
ACTOR_TYPES = {"user", "skill", "system", "data-subject"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
NAMESPACE = uuid.UUID("a59b2db7-8dc7-4e9c-91a6-2ad614327f4b")
MAX_EVENT_BYTES = 1_000_000
FORBIDDEN_CONSENT_KEYS = {
    "email", "email_address", "phone", "phone_number", "name", "full_name",
    "first_name", "last_name", "address", "postal_address", "raw_identifier",
}


class RegistryError(ValueError):
    pass


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise RegistryError("event must contain finite JSON values: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def event_hash(event):
    material = dict(event)
    material.pop("event_hash", None)
    return sha256_json(material)


def parse_datetime(value, label):
    if not isinstance(value, str) or not value.strip():
        raise RegistryError("%s is required" % label)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError("%s must be an ISO date-time" % label) from exc
    if parsed.tzinfo is None:
        raise RegistryError("%s must include a timezone" % label)
    return parsed


def validate_observed_at(value):
    if not isinstance(value, str) or not value:
        raise RegistryError("source.observed_at is required")
    try:
        dt.date.fromisoformat(value)
        return
    except ValueError:
        parse_datetime(value, "source.observed_at")


def walk_json(value, path="payload"):
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RegistryError("%s contains a non-finite number" % path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            walk_json(item, "%s[%d]" % (path, index))
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise RegistryError("%s has a non-string key" % path)
            walk_json(item, "%s.%s" % (path, key))
        return
    raise RegistryError("%s contains unsupported value %r" % (path, type(value).__name__))


def consent_keys(value):
    found = set()
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in FORBIDDEN_CONSENT_KEYS:
                found.add(key)
            found.update(consent_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.update(consent_keys(item))
    return found


def validate_operation_payload(operation, payload):
    """Enforce one unambiguous mutation shape for the effective operation."""
    has_set = bool(payload.get("set"))
    has_unset = bool(payload.get("unset"))
    has_transition = "transition" in payload
    if operation == "upsert":
        if has_transition:
            raise RegistryError("upsert payload cannot carry transition")
        if not (has_set or has_unset):
            raise RegistryError("upsert requires a non-empty set or unset")
    elif operation == "transition":
        if not has_transition:
            raise RegistryError("transition operation requires payload.transition")
        if "set" in payload or "unset" in payload:
            raise RegistryError("transition payload cannot carry set or unset")
    elif operation in {"tombstone", "suppress", "erase"}:
        if any(key in payload for key in ("set", "unset", "transition")):
            raise RegistryError("%s payload cannot carry a second mutation" % operation)
        if not str(payload.get("reason", "")).strip():
            raise RegistryError("%s requires payload.reason" % operation)
    elif operation == "restore":
        if "unset" in payload or has_transition:
            raise RegistryError("restore payload cannot carry unset or transition")
        if not has_set or not str(payload.get("reason", "")).strip():
            raise RegistryError("restore requires payload.reason and a non-empty set")


def validate_request(registry, request):
    if registry not in REGISTRIES:
        raise RegistryError("unknown registry: %s" % registry)
    if not isinstance(request, dict):
        raise RegistryError("event request must be an object")
    extra = sorted(set(request) - REQUEST_FIELDS)
    if extra:
        raise RegistryError("unknown request fields: %s" % ", ".join(extra))
    if request.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("schema_version must be %s" % SCHEMA_VERSION)
    for name in ("idempotency_key", "aggregate_id"):
        value = request.get(name)
        if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or "@" in value:
            raise RegistryError("%s must be a non-PII safe identifier" % name)
    operation = request.get("operation")
    if operation not in OPERATIONS:
        raise RegistryError("invalid operation")
    parse_datetime(request.get("occurred_at"), "occurred_at")

    actor = request.get("actor")
    if not isinstance(actor, dict) or set(actor) != {"type", "id"}:
        raise RegistryError("actor requires exactly type and id")
    if (actor.get("type") not in ACTOR_TYPES or not isinstance(actor.get("id"), str)
            or not actor["id"].strip() or len(actor["id"]) > 128):
        raise RegistryError("invalid actor")
    authorized_by = request.get("authorized_by")
    if authorized_by not in {"user", "data-subject"}:
        raise RegistryError("authorized_by must be user or data-subject")
    auth_ref = request.get("authorization_ref")
    if not isinstance(auth_ref, str) or not auth_ref.strip() or len(auth_ref) > 256:
        raise RegistryError("authorization_ref is required and limited to 256 characters")
    if authorized_by == "data-subject" and not (registry == "consent" and operation in {"suppress", "erase"}):
        raise RegistryError("data-subject authorization is limited to consent suppress/erase")

    source = request.get("source")
    if not isinstance(source, dict) or set(source) != {"type", "ref", "observed_at"}:
        raise RegistryError("source requires exactly type, ref, and observed_at")
    if source.get("type") not in SOURCE_TYPES:
        raise RegistryError("invalid source.type")
    if not isinstance(source.get("ref"), str) or not source["ref"].strip() or len(source["ref"]) > 512:
        raise RegistryError("source.ref is required and limited to 512 characters")
    validate_observed_at(source.get("observed_at"))

    revision = request.get("expected_revision")
    if revision is not None and (not isinstance(revision, int) or isinstance(revision, bool) or revision < 0):
        raise RegistryError("expected_revision must be a non-negative integer")
    payload = request.get("payload", {})
    if not isinstance(payload, dict):
        raise RegistryError("payload must be an object")
    allowed_payload = {"set", "unset", "transition", "reason"}
    if set(payload) - allowed_payload:
        raise RegistryError("payload contains unknown fields")
    if "set" in payload and not isinstance(payload["set"], dict):
        raise RegistryError("payload.set must be an object")
    if "set" in payload and any(
            not isinstance(field, str) or not SAFE_FIELD.fullmatch(field)
            for field in payload["set"]):
        raise RegistryError("payload.set must use safe field names")
    if "unset" in payload:
        if not isinstance(payload["unset"], list) or any(
                not isinstance(item, str) or not SAFE_FIELD.fullmatch(item) for item in payload["unset"]):
            raise RegistryError("payload.unset must contain safe field names")
        if len(set(payload["unset"])) != len(payload["unset"]):
            raise RegistryError("payload.unset cannot contain duplicates")
    overlap = set(payload.get("set", {})) & set(payload.get("unset", []))
    if overlap:
        raise RegistryError("payload cannot set and unset the same field: %s" % ", ".join(sorted(overlap)))
    if "reason" in payload and (not isinstance(payload["reason"], str) or len(payload["reason"]) > 1024):
        raise RegistryError("payload.reason must be a string limited to 1024 characters")
    transition = payload.get("transition")
    if transition is not None:
        if not isinstance(transition, dict) or set(transition) != {"from", "to"}:
            raise RegistryError("payload.transition requires exactly from and to")
        if transition["from"] is not None and not isinstance(transition["from"], str):
            raise RegistryError("transition.from must be a string or null")
        if not isinstance(transition["to"], str) or not transition["to"].strip():
            raise RegistryError("transition.to must be non-empty")
    walk_json(payload)
    if len(canonical_json(payload).encode("utf-8")) > 256_000:
        raise RegistryError("payload exceeds 256 KB")

    if operation == "propose":
        if request.get("proposed_operation") not in PROPOSED_OPERATIONS:
            raise RegistryError("propose requires proposed_operation")
        validate_operation_payload(request["proposed_operation"], payload)
    elif "proposed_operation" in request:
        raise RegistryError("proposed_operation is valid only for propose")
    if operation in {"accept", "reject"}:
        try:
            uuid.UUID(str(request.get("proposal_event_id")))
        except (ValueError, TypeError, AttributeError) as exc:
            raise RegistryError("accept/reject requires proposal_event_id") from exc
        if any(key in payload for key in ("set", "unset", "transition")):
            raise RegistryError("accept/reject decision payload cannot carry a second mutation")
        if operation == "reject" and not str(payload.get("reason", "")).strip():
            raise RegistryError("reject requires payload.reason")
        if revision is not None:
            raise RegistryError("accept/reject inherit the proposal revision and must omit expected_revision")
    elif "proposal_event_id" in request:
        raise RegistryError("proposal_event_id is valid only for accept/reject")
    elif operation not in {"accept", "reject", "propose"}:
        validate_operation_payload(operation, payload)
    if operation == "suppress" and registry != "consent":
        raise RegistryError("suppress is valid only for consent")
    if operation == "restore" and registry != "consent":
        raise RegistryError("restore is valid only for consent")

    subject_erasure = (
        registry == "consent" and operation == "erase"
        and authorized_by == "data-subject" and actor["type"] == "data-subject"
    )
    revision_required = operation in {"propose", "upsert", "transition", "tombstone", "restore"}
    if operation == "erase" and not subject_erasure:
        revision_required = True
    if revision_required and revision is None:
        raise RegistryError("%s requires expected_revision" % operation)

    owner = OWNERS[registry]
    canonical_ops = {"accept", "reject", "upsert", "transition", "restore"}
    if operation in canonical_ops and actor["id"] != owner:
        raise RegistryError("%s may be emitted only by %s" % (operation, owner))
    if operation in {"tombstone", "erase"} and actor["id"] not in {owner, "memory-management"} and not subject_erasure:
        raise RegistryError("%s requires the registry owner or memory-management" % operation)
    if registry == "consent":
        for label, value in (
                ("idempotency_key", request["idempotency_key"]),
                ("actor.id", actor["id"]),
                ("authorization_ref", auth_ref),
                ("source.ref", source["ref"])):
            if "@" in value:
                raise RegistryError("consent %s must not contain a raw email address" % label)
        forbidden = sorted(consent_keys(payload))
        if forbidden:
            raise RegistryError("consent payload contains raw PII fields: %s" % ", ".join(forbidden))
        if operation == "restore":
            restored = payload.get("set", {})
            if restored.get("subscription_status") != "subscribed" or not restored.get("basis_ref"):
                raise RegistryError("restore requires subscription_status=subscribed and basis_ref")
    return json.loads(canonical_json(request))


def memory_paths(root, registry):
    supplied_root = Path(root)
    if supplied_root.exists() and supplied_root.is_symlink():
        raise RegistryError("project root cannot be a symlink")
    root_path = supplied_root.resolve()
    if root_path.exists() and not root_path.is_dir():
        raise RegistryError("project root must be a directory")
    memory = root_path / "memory"
    events_dir = memory / "events"
    projections_dir = memory / "projections"
    for path in (memory, events_dir, projections_dir):
        if path.exists() and path.is_symlink():
            raise RegistryError("runtime path cannot be a symlink: %s" % path)
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            path.chmod(0o700)
        except OSError as exc:
            raise RegistryError("cannot secure runtime directory %s: %s" % (path, exc)) from exc
    return (
        events_dir / (registry + ".ndjson"),
        projections_dir / (registry + ".json"),
        projections_dir / "consent-suppressions.json",
    )


@contextlib.contextmanager
def locked_stream(path, exclusive=True):
    if path.exists() and path.is_symlink():
        raise RegistryError("event stream cannot be a symlink")
    flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(path), flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
    except OSError as exc:
        os.close(fd)
        raise RegistryError("cannot secure event stream %s: %s" % (path, exc)) from exc
    handle = os.fdopen(fd, "r+", encoding="utf-8")
    lock_path = str(path) + ".lock"
    fallback_fd = None
    try:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        else:  # pragma: no cover
            for _ in range(200):
                try:
                    fallback_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                    break
                except FileExistsError:
                    time.sleep(0.05)
            if fallback_fd is None:
                raise RegistryError("timed out acquiring event lock")
        yield handle
    finally:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        if fallback_fd is not None:  # pragma: no cover
            os.close(fallback_fd)
            try:
                os.unlink(lock_path)
            except FileNotFoundError:
                pass
        handle.close()


def read_stream(handle, registry):
    handle.seek(0)
    events = []
    previous_hash = "0" * 64
    seen_ids = set()
    seen_keys = set()
    for line_number, raw in enumerate(handle, 1):
        if len(raw.encode("utf-8")) > MAX_EVENT_BYTES:
            raise RegistryError("event line %d exceeds size limit" % line_number)
        if not raw.strip():
            raise RegistryError("blank line in event stream at %d" % line_number)
        try:
            event = json.loads(raw)
        except ValueError as exc:
            raise RegistryError("invalid JSON at event line %d" % line_number) from exc
        if not isinstance(event, dict) or set(event) - (REQUEST_FIELDS | ASSIGNED_EVENT_FIELDS):
            raise RegistryError("invalid event fields at line %d" % line_number)
        missing_assigned = ASSIGNED_EVENT_FIELDS - set(event)
        if missing_assigned:
            raise RegistryError("event line %d is missing assigned fields" % line_number)
        if event.get("registry") != registry:
            raise RegistryError("event line %d has wrong registry" % line_number)
        request = {key: event[key] for key in REQUEST_FIELDS if key in event}
        try:
            normalized = validate_request(registry, request)
        except RegistryError as exc:
            raise RegistryError("stored event is invalid at line %d: %s" % (line_number, exc)) from exc
        if event.get("request_hash") != sha256_json(normalized):
            raise RegistryError("event request hash mismatch at line %d" % line_number)
        parse_datetime(event.get("recorded_at"), "recorded_at")
        if not isinstance(event.get("offset"), int) or isinstance(event.get("offset"), bool):
            raise RegistryError("event offset must be an integer at line %d" % line_number)
        if event.get("offset") != line_number:
            raise RegistryError("event offset discontinuity at line %d" % line_number)
        if event.get("previous_hash") != previous_hash:
            raise RegistryError("event hash chain mismatch at line %d" % line_number)
        if event.get("event_hash") != event_hash(event):
            raise RegistryError("event hash mismatch at line %d" % line_number)
        expected_id = str(uuid.uuid5(NAMESPACE, registry + ":" + str(event.get("idempotency_key"))))
        if event.get("event_id") != expected_id:
            raise RegistryError("event ID mismatch at line %d" % line_number)
        if event["event_id"] in seen_ids or event.get("idempotency_key") in seen_keys:
            raise RegistryError("duplicate event identity at line %d" % line_number)
        seen_ids.add(event["event_id"])
        seen_keys.add(event["idempotency_key"])
        previous_hash = event["event_hash"]
        events.append(event)
    return events


def new_projection(registry):
    return {
        "schema_version": SCHEMA_VERSION,
        "registry": registry,
        "last_offset": 0,
        "last_event_hash": "0" * 64,
        "records": {},
        "pending": {},
        "proposal_decisions": {},
    }


def current_record(state, aggregate_id):
    return state["records"].get(aggregate_id, {
        "revision": 0,
        "status": "active",
        "suppressed": False,
        "data": {},
        "last_event_id": None,
        "updated_at": None,
        "last_occurred_at": None,
        "last_source": None,
        "source_occurred_at": None,
    })


def check_revision(event, record, expected=None):
    wanted = event.get("expected_revision") if expected is None else expected
    if wanted is not None and wanted != record["revision"]:
        raise RegistryError(
            "stale expected_revision for %s: expected %d, current %d"
            % (event["aggregate_id"], wanted, record["revision"])
        )


def apply_mutation(registry, state, event, operation, payload, expected_revision=None,
                   provenance=None):
    aggregate_id = event["aggregate_id"]
    record = json.loads(canonical_json(current_record(state, aggregate_id)))
    check_revision(event, record, expected_revision)
    terminal = record.get("status") in {"tombstoned", "erased"}
    if terminal and not (registry == "consent" and operation in {"suppress", "restore"}):
        raise RegistryError(
            "%s record %s is terminal; use a new aggregate ID"
            % (record["status"], aggregate_id)
        )
    if operation == "restore" and (record["revision"] == 0 or not record.get("suppressed")):
        raise RegistryError("restore requires an existing suppressed consent record")
    if operation == "transition":
        transition = payload.get("transition")
        if not transition:
            raise RegistryError("transition payload is missing")
        current = record["data"].get("state")
        if current != transition["from"]:
            raise RegistryError(
                "transition conflict for %s: expected state %r, current %r"
                % (aggregate_id, transition["from"], current)
            )
        graph = TRANSITION_GRAPHS.get(registry)
        if graph is not None and transition["to"] not in graph.get(current, set()):
            raise RegistryError(
                "invalid %s transition for %s: %r -> %r"
                % (registry, aggregate_id, current, transition["to"])
            )
        record["data"]["state"] = transition["to"]
    if operation == "upsert" and "state" in payload.get("set", {}):
        graph = TRANSITION_GRAPHS.get(registry)
        proposed_state = payload["set"]["state"]
        if graph is not None and (
                record["revision"] != 0 or proposed_state not in graph.get(None, set())):
            raise RegistryError(
                "%s state may be initialized once to %s; later changes require transition"
                % (registry, sorted(graph.get(None, set())))
            )
    for key, value in payload.get("set", {}).items():
        record["data"][key] = value
    for key in payload.get("unset", []):
        record["data"].pop(key, None)
    if operation == "tombstone":
        record["status"] = "tombstoned"
    elif operation == "suppress":
        record["suppressed"] = True
        if record.get("status") not in {"erased", "tombstoned"}:
            record["data"]["subscription_status"] = "suppressed"
    elif operation == "restore":
        if record.get("last_occurred_at"):
            previous = parse_datetime(record["last_occurred_at"], "record.last_occurred_at")
            current = parse_datetime(event["occurred_at"], "occurred_at")
            if current <= previous:
                raise RegistryError("restore must occur after the current consent event")
        record["suppressed"] = False
        record["status"] = "active"
    elif operation == "erase":
        record["data"] = {}
        record["status"] = "erased"
        if registry == "consent":
            record["suppressed"] = True
    record["revision"] += 1
    record["last_event_id"] = event["event_id"]
    record["updated_at"] = event["recorded_at"]
    record["last_occurred_at"] = event["occurred_at"]
    source_event = provenance or event
    record["last_source"] = source_event["source"]
    record["source_occurred_at"] = source_event["occurred_at"]
    state["records"][aggregate_id] = record


def project_events(registry, events):
    state = new_projection(registry)
    for event in events:
        operation = event["operation"]
        if operation == "propose":
            state["pending"][event["event_id"]] = {
                "aggregate_id": event["aggregate_id"],
                "proposed_operation": event["proposed_operation"],
                "payload": event.get("payload", {}),
                "expected_revision": event.get("expected_revision"),
                "source": event["source"],
                "occurred_at": event["occurred_at"],
                "actor": event["actor"],
                "event_id": event["event_id"],
            }
        elif operation in {"accept", "reject"}:
            proposal_id = event["proposal_event_id"]
            proposal = state["pending"].get(proposal_id)
            if proposal is None:
                raise RegistryError("proposal is missing or already resolved: %s" % proposal_id)
            if proposal["aggregate_id"] != event["aggregate_id"]:
                raise RegistryError("proposal aggregate_id does not match decision")
            if operation == "accept":
                apply_mutation(
                    registry, state, event, proposal["proposed_operation"], proposal["payload"],
                    proposal.get("expected_revision"), provenance=proposal,
                )
            state["proposal_decisions"][proposal_id] = {
                "decision": operation,
                "event_id": event["event_id"],
                "recorded_at": event["recorded_at"],
                "proposal_source": proposal["source"],
                "proposal_occurred_at": proposal["occurred_at"],
            }
            del state["pending"][proposal_id]
        else:
            apply_mutation(registry, state, event, operation, event.get("payload", {}))
        state["last_offset"] = event["offset"]
        state["last_event_hash"] = event["event_hash"]
    return state


def atomic_write_json(path, value):
    if path.exists() and path.is_symlink():
        raise RegistryError("projection path cannot be a symlink")
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        directory_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def write_projections(registry, state, projection_path, suppressions_path):
    atomic_write_json(projection_path, state)
    if registry == "consent":
        suppressed = sorted(
            aggregate_id for aggregate_id, record in state["records"].items()
            if record.get("suppressed")
        )
        atomic_write_json(suppressions_path, {
            "schema_version": SCHEMA_VERSION,
            "registry": "consent",
            "last_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "suppressed": suppressed,
        })


def append_event(root, registry, request):
    normalized = validate_request(registry, request)
    request_hash = sha256_json(normalized)
    stream_path, projection_path, suppressions_path = memory_paths(root, registry)
    with locked_stream(stream_path, exclusive=True) as handle:
        events = read_stream(handle, registry)
        existing = next((event for event in events
                         if event["idempotency_key"] == normalized["idempotency_key"]), None)
        if existing:
            if existing.get("request_hash") != request_hash:
                raise RegistryError("idempotency key was already used with different content")
            state = project_events(registry, events)
            write_projections(registry, state, projection_path, suppressions_path)
            return {"deduplicated": True, "event": existing,
                    "record": state["records"].get(existing["aggregate_id"])}

        offset = len(events) + 1
        recorded_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        event = dict(normalized)
        event.update({
            "registry": registry,
            "event_id": str(uuid.uuid5(NAMESPACE, registry + ":" + normalized["idempotency_key"])),
            "offset": offset,
            "recorded_at": recorded_at,
            "request_hash": request_hash,
            "previous_hash": events[-1]["event_hash"] if events else "0" * 64,
        })
        event["event_hash"] = event_hash(event)
        state = project_events(registry, events + [event])
        line = canonical_json(event) + "\n"
        if len(line.encode("utf-8")) > MAX_EVENT_BYTES:
            raise RegistryError("event exceeds size limit")
        handle.seek(0, os.SEEK_END)
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
        write_projections(registry, state, projection_path, suppressions_path)
        return {"deduplicated": False, "event": event,
                "record": state["records"].get(event["aggregate_id"])}


def load_state(root, registry, create=False):
    if registry not in REGISTRIES:
        raise RegistryError("unknown registry: %s" % registry)
    stream_path, projection_path, suppressions_path = memory_paths(root, registry)
    if not stream_path.exists() and not create:
        return new_projection(registry)
    with locked_stream(stream_path, exclusive=False) as handle:
        events = read_stream(handle, registry)
        state = project_events(registry, events)
    return state


def rebuild_projection(root, registry):
    stream_path, projection_path, suppressions_path = memory_paths(root, registry)
    with locked_stream(stream_path, exclusive=False) as handle:
        events = read_stream(handle, registry)
        state = project_events(registry, events)
        # Keep the shared lock through installation so a concurrent append cannot
        # install a newer projection and then be overwritten by this replay.
        write_projections(registry, state, projection_path, suppressions_path)
    return state


def get_record(root, registry, aggregate_id):
    if not SAFE_ID.fullmatch(aggregate_id) or "@" in aggregate_id:
        raise RegistryError("aggregate_id must be a safe pseudonymous identifier")
    return load_state(root, registry)["records"].get(aggregate_id)


def is_suppressed(root, aggregate_id):
    record = get_record(root, "consent", aggregate_id)
    return bool(record and record.get("suppressed"))


def load_request(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise RegistryError("cannot read event request: %s" % exc) from exc
    if len(raw) > MAX_EVENT_BYTES:
        raise RegistryError("event request exceeds size limit")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RegistryError("event request must be UTF-8 JSON") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.getcwd(), help="Project root containing memory/.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    append = sub.add_parser("append")
    append.add_argument("registry", choices=sorted(REGISTRIES))
    append.add_argument("event_json")
    verify = sub.add_parser("verify")
    verify.add_argument("registry", choices=sorted(REGISTRIES))
    project = sub.add_parser("project")
    project.add_argument("registry", choices=sorted(REGISTRIES))
    get = sub.add_parser("get")
    get.add_argument("registry", choices=sorted(REGISTRIES))
    get.add_argument("aggregate_id")
    suppressed = sub.add_parser("is-suppressed")
    suppressed.add_argument("aggregate_id")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            for registry in sorted(REGISTRIES):
                memory_paths(args.root, registry)
            result = {"initialized": True, "registries": sorted(REGISTRIES)}
        elif args.command == "append":
            result = append_event(args.root, args.registry, load_request(args.event_json))
        elif args.command == "verify":
            state = load_state(args.root, args.registry, create=True)
            result = {"valid": True, "registry": args.registry,
                      "last_offset": state["last_offset"], "records": len(state["records"]),
                      "pending": len(state["pending"])}
        elif args.command == "project":
            state = rebuild_projection(args.root, args.registry)
            result = {"projected": True, "registry": args.registry,
                      "last_offset": state["last_offset"]}
        elif args.command == "get":
            result = {"registry": args.registry, "aggregate_id": args.aggregate_id,
                      "record": get_record(args.root, args.registry, args.aggregate_id)}
        else:
            result = {"aggregate_id": args.aggregate_id,
                      "suppressed": is_suppressed(args.root, args.aggregate_id)}
    except RegistryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
