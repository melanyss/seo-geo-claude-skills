---
description: "Run an influencer-marketing workflow: audience & creator discovery, campaign planning, briefs, outreach, amplification, and ROI measurement. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-brand> [--phase discover|plan|activate|measure]"
---

# Influencer Command

Run the influencer-marketing lifecycle across four phases — **Discover → Plan → Activate → Measure**: understand the audience, find and score creators, plan and brief the campaign, run outreach and amplify, then track ROI. Skills score on the [C³ framework](../references/c3-benchmark.md) (Creator / Content / Campaign → CVI) and operate from the user's **own data and project memory** — keyed creator-analytics suites are never required; connectors only automate retrieval.

## Route

Infer the phase from the goal (or honor `--phase`) and route to the matching skill:

- **Discover** — audience-mapper (audience/niche modes), trend-spotter, influencer-discovery, fit-scorer (C³ ACE); creator-registry dedupes candidates against the roster
- **Plan** — competitor-tracker, campaign-planner, brief-generator, budget-optimizer
- **Activate** — outreach-manager, content-reviewer (C³ ART gate), contract-helper, content-amplifier (paid whitelisting / UGC repurpose modes) — consult creator-registry's dossier (`memory/creators/<handle-slug>.md`: contact path, last agreed rate, exclusivity, compliance history) before outreach or contracting
- **Measure** — landing-optimizer (post-click), performance-analyzer, roi-calculator (CVI), report-generator

## Rules

- Start where the goal sits in the funnel; do not force the full four-phase chain when the user only needs one stage.
- `content-reviewer` is the pre-publish gate: any creator content goes through its C³ **ART** check (FTC disclosure T1, claim integrity T2) before it ships.
- `memory/events/creators.ndjson` is the roster history. Other skills submit authorized `operation: propose` events; `creator-registry` alone accepts/rejects or mutates canonical creator state. Run it when proposals are pending or a campaign cycle closes; `memory/creators/` contains generated views.
- Score creators/content/campaigns on C³ (ACE/ART/ROI → CVI); label every metric Measured / User-provided / Estimated; never fabricate reach or rates.
- Tier 1 by default — works from user-provided data; connectors only automate retrieval. Compliance checks are guidance, not legal advice.
- Follow each skill's Next Best Skill handoff; stop at the documented termination rules rather than auto-chaining the whole discipline.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
