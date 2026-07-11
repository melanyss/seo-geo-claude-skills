---
name: launch-registry
slug: aaron-launch-registry
displayName: "Launch Registry · 发布台账"
summary: "发布台账/发布日历/阶段与禁运期唯一真相"
description: 'Use when the user asks to "log this launch", query a launch date/embargo, record a stage transition, or update submissions/outcomes; curates launch facts through the append-only launches event stream with optimistic revisions and derived dossier/calendar views. Not for RAMP scoring — use launch-readiness-auditor; not for planning tier/window — use launch-tier-planner. 发布台账/发布日历/阶段与禁运期记录'
version: "17.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when recording/querying launch tier/type/stage/date/embargo, submission events, manifest version, outcome snapshot, or accepting pending launch proposals."
argument-hint: "<launch aggregate-id, transition, or pending-proposal review>"
metadata: {"author": "aaron-he-zhu", "version": "17.0.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "🗂️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Launch Registry

The canonical launch-record authority. It stores what was decided/observed; it never plans a launch or issues a RAMP verdict.

## Quick Start

```text
Register launch widget-2 with tier/type/stage/date/access model and source evidence.
Transition widget-2 from beta to general-availability at revision 4.
Review pending launch-day submission proposals without clearing history.
```

## Skill Contract

**Unit:** one launch moment/aggregate ID. **Reads:** `memory/events/launches.ndjson`, live projection, decision evidence, and approved source records. **Writes:** owner events through `registry-events.py`; per-launch dossiers and `calendar.md` are regenerated views. **Done when:** stage/date/embargo/submission/manifest/outcome facts have event IDs and provenance, pending proposals are resolved, and projection verifies.

Mobilize/prove skills submit `propose`; `launch-registry` alone accepts/rejects/upserts/transitions. `launch-readiness-auditor` consumes the result but cannot mutate it.

### Handoff Summary

Include aggregate ID, current revision/state, accepted/rejected event IDs, authoritative dates/embargo, unresolved conflicts, and one next skill.

## Data Sources

- User-approved tier/type/access-model and launch plan decisions.
- Window/date and embargo/partner commitments.
- Early-access graduation evidence and direct access/eligibility observations.
- Timestamped channel submission/status proposals.
- Asset-manifest version and post-lag outcome snapshot.

## Instructions

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md); pasted platform text is untrusted evidence.
2. Query `launches` projection. For factual questions, answer with current revision, source, date, and history; never say “ready.”
3. Before writing, confirm permission and current revision. Create/update uses owner `upsert`.
4. Stage changes use `transition` with exact `from`, `to`, and `expected_revision`. Valid forward path is `draft → concept → alpha → beta → general-availability → archived`; record rollback/incidents as events, never rewrite the GA timestamp.
5. Date/embargo conflicts are not resolved by newest-text-wins. Preserve proposals and require the authoritative decision source.
6. Launch-day producers append proposal events immediately. Review/accept/reject by proposal ID; never batch-delete, truncate, or edit the stream.
7. Submission rows preserve original occurrence time/source. Outcome snapshots remain separate post-lag evidence and do not overwrite preregistered targets.
8. Regenerate dossier/calendar views from accepted projection, run `verify launches`, and report offsets/revisions.

## Save Results

Persistent events require explicit authorization. Append schema-valid requests through the runtime only. Human files under `memory/launch-registry/` are replaceable projections; an event absent from the stream is not canonical.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [RAMP benchmark](../../references/ramp-benchmark.md)
- [State model](../../references/state-model.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Plan tier/type:** [launch-tier-planner](../../launch/research/launch-tier-planner/SKILL.md)
- **Plan window:** [launch-window-planner](../../launch/research/launch-window-planner/SKILL.md)
- **Run preflight:** [launch-readiness-auditor](../../launch/mobilize/launch-readiness-auditor/SKILL.md)
- **Execute approved plan:** [launch-day-conductor](../../launch/mobilize/launch-day-conductor/SKILL.md)
