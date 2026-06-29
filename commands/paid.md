---
name: paid
description: "Run a paid-ads (ROAS) workflow: audience segments, account structure, ad creative, experiment design, pre-launch signal QA + the account-audit gate, measurement, and attribution. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-account> [--phase research|orchestrate|activate|scale]"
parameters:
  - name: target
    type: string
    required: true
    description: "Paid-ads goal, account, or campaign (with the user's own exported data)"
  - name: phase
    type: string
    required: false
    description: "Force a ROAS-loop phase: research | orchestrate | activate | scale"
---

# Paid Command

Run the paid-ads lifecycle along the **ROAS loop** (Research → Orchestrate → Activate → Scale). Skills score on the [ROAS framework](../references/roas-benchmark.md) and operate from the user's **own-account manual export** — keyed ad-platform APIs are never required.

## Route

Infer the ROAS-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Research** — campaign-architect (structure + search-term mining), audience-segment-builder; reuse budget-optimizer for spend
- **Orchestrate** — ad-creative-builder, ad-test-designer; reuse landing-optimizer for the post-click page
- **Activate** — conversion-signal-qa (build/verify tracking), then ad-account-auditor (the RQS gate + launch go/no-go)
- **Scale** — paid-measurement-loop, attribution-reconciler; reuse roi-calculator / report-generator / performance-analyzer

## Rules

- `ad-account-auditor` is the launch gate: score RQS and enforce the five vetoes (R1/R2/O1/O2/A1) before any budget increase; run conversion-signal-qa first so R1/R2 can be trusted.
- Keyless Tier 1 — score from native ad-manager / GA4 / ecommerce exports the user provides; keyed Google Ads / Meta APIs are opt-in Tier-2/3 MCP only.
- Only `ad-account-auditor` computes the goal-weighted RQS; every other skill works one lever and hands off. Bid-pacing and search-term mining are modes of budget-optimizer / campaign-architect, not separate skills.
- Label every metric Measured / User-provided / Estimated; never invent ROAS/CPA figures.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
