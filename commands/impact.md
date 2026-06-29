---
name: impact
description: "Run an influencer (IMPACT) workflow: audience insight, creator discovery & fit, campaign planning, briefs, outreach, amplification, and ROI. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-brand> [--phase insight|map|plan|activate|convert|track]"
parameters:
  - name: target
    type: string
    required: true
    description: "Campaign goal, brand, product, or audience to run influencer marketing for"
  - name: phase
    type: string
    required: false
    description: "Force an IMPACT phase: insight | map | plan | activate | convert | track"
---

# Impact Command

Run the influencer-marketing (IMPACT) lifecycle: understand the audience, find and score creators, plan and brief the campaign, run outreach, amplify and convert, then track ROI. Skills score on the [C³ framework](../references/c3-benchmark.md).

## Route

Infer the IMPACT phase from the goal (or honor `--phase`) and route to the matching skill:

- **Insight** — audience-analyzer, niche-researcher, trend-spotter
- **Map** — influencer-discovery, fit-scorer (C³ ACE), competitor-tracker
- **Plan** — campaign-planner, brief-generator, budget-optimizer
- **Activate** — outreach-manager, content-reviewer (C³ ART gate), contract-helper
- **Convert** — content-amplifier, ugc-repurposer, landing-optimizer
- **Track** — performance-analyzer, roi-calculator (CVI), report-generator

## Rules

- Start where the goal sits in the funnel; do not force the full six-phase chain when the user only needs one stage.
- `content-reviewer` is the pre-publish gate: any creator content goes through its C³ **ART** check (FTC disclosure T1, claim integrity T2) before it ships.
- Score creators/content/campaigns on C³ (ACE/ART/ROI → CVI); label every metric Measured / User-provided / Estimated; never fabricate reach or rates.
- Tier 1 by default — works from user-provided data; connectors only automate retrieval. Compliance checks are guidance, not legal advice.
- Follow each skill's Next Best Skill handoff; stop at the documented termination rules rather than auto-chaining the whole discipline.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
