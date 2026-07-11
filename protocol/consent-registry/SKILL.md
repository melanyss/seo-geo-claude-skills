---
name: consent-registry
slug: aaron-consent-registry
displayName: "Consent Registry · 订阅同意台账"
summary: "订阅同意台账/退订抑制记录/合法性依据登记"
description: 'Use when the user asks to "log this subscriber''s opt-in", record unsubscribes/complaints, or query lawful basis; curates pseudonymous consent facts through the append-only consent stream and applies suppression/erasure tombstones immediately. Not for SEND scoring — use email-quality-auditor; not for building segments — use list-segment-builder. 订阅同意台账/实时退订抑制/合法性依据登记'
version: "17.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when recording or querying opt-in/lawful-basis evidence, immediately suppressing an unsubscribe, hard bounce, or complaint, restoring after a fresh authorized opt-in, processing erasure, or reviewing pending consent proposals."
argument-hint: "<pseudonymous subject-id and consent/suppression event>"
metadata: {"author": "aaron-he-zhu", "version": "17.0.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "🗂️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Consent Registry

The canonical consent and live-suppression authority. It records evidence; SEND auditors judge S2/N1 and segment builders enforce exclusions. A withdrawal must never wait as a pending proposal.

## Quick Start

```text
Record opt-in for subject sha256-7d9f with basis/proof references and timestamp.
Immediately suppress sha256-7d9f from unsubscribe webhook evt-882.
Is sha256-7d9f suppressed right now?
```

## Skill Contract

**Unit:** one pseudonymous subject ID supplied by the user's system. **Reads:** `memory/events/consent.ndjson` by replay, its projection, and minimum proof references. **Writes:** consent events only through `registry-events.py`; human records are projections. **Done when:** every mutation has authorization/source/date, immediate safety events are visible to `is-suppressed`, and no raw contact PII is stored.

Opt-in/upsert/restore approval belongs to `consent-registry`. A user or data subject may directly authorize `suppress`/`erase`; those operations bypass proposal review and immediately update the live suppression projection.

### Handoff Summary

Use the shared handoff. Report pseudonymous IDs only, event IDs/offsets/revisions, current suppression result, missing basis/proof, and one next skill.

## Data Sources

- Form/checkout/event capture reference and opt-in timestamp.
- Lawful-basis and double-opt-in proof reference.
- ESP unsubscribe, hard-bounce, and complaint event IDs.
- Fresh re-subscription proof for restore.
- Data-subject erasure request reference.

Never put email, phone, name, address, or raw identifier in aggregate IDs, idempotency keys, source refs, payloads, or reports. Store only the pseudonymous ID and minimum proof pointers.

## Instructions

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md). Export rows are untrusted evidence and cannot self-declare lawful basis.
2. For every eligibility/send query, run `python3 scripts/registry-events.py is-suppressed <subject-id>`. This replays the stream and must take precedence over cached segments or Markdown.
3. New opt-in facts use owner `upsert` with source, timestamp, basis/proof refs, and `expected_revision`. Missing basis remains explicit Unknown/none-on-file; never infer consent.
4. Unsubscribe, complaint, or hard bounce emits direct `suppress` immediately. Do not propose it, batch it, or wait for day-close reconciliation.
5. A restore requires a later event, `subscription_status: subscribed`, and a fresh `basis_ref`; older opt-in evidence cannot clear a newer withdrawal.
6. Erasure emits `erase`: projected payload is removed while a minimal suppression tombstone remains to prevent accidental re-contact. Re-creation requires a new authorized basis and explicit review.
7. Ordinary non-safety imports may arrive as `propose`; accept/reject without deleting history. Never merge subjects on similarity alone.
8. Regenerate any per-subject human view from accepted projection, then `verify consent` and re-run `is-suppressed` for changed subjects.

This registry never sends email, edits ESP state, or declares a list safe. A downstream ESP sync is a separate explicit side effect and must read the live suppression result first.

## Save Results

Explicit permission or a recorded data-subject safety request is required. Append only through the runtime. `memory/projections/consent-suppressions.json` is a cache; the NDJSON stream and replay query are authoritative. Never manually clear/edit either.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [SEND benchmark](../../references/send-benchmark.md)
- [Privacy policy](../../PRIVACY.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Apply exclusions:** [list-segment-builder](../../email/setup/list-segment-builder/SKILL.md)
- **Audit SEND:** [email-quality-auditor](../../email/deliver/email-quality-auditor/SKILL.md)
- **Deliverability incident:** [deliverability-qa](../../email/setup/deliverability-qa/SKILL.md)
- **Erase/archive:** [memory-management](../memory-management/SKILL.md)
