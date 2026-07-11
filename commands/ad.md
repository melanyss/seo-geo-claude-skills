---
description: "Run a paid-ads (ROAS) workflow: audience segments, account structure, ad creative, experiment design, pre-launch signal QA + the account-audit gate, measurement, and attribution. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-account> [--phase research|orchestrate|activate|scale]"
---

# Paid Command

Run the paid-ads lifecycle along the **ROAS loop** (Research → Orchestrate → Activate → Scale). Skills score on the [ROAS framework](../references/roas-benchmark.md) and operate from the user's **own-account manual export** — keyed ad-platform APIs are never required.

## Route

Infer the ROAS-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Research** — campaign-architect (account/campaign structure), audience-segment-builder (segments), search-term-miner (converting-query mining + negative-keyword lists), product-feed-optimizer (Shopping/PMax feed, title/attribute fixes); reuse budget-optimizer for spend; consult offer-claims-registry's live-offers table (`memory/claims/offers.md`) when structuring promo campaigns
- **Orchestrate** — ad-creative-builder, ad-test-designer, bid-strategy-planner (tCPA/tROAS target + learning-phase entry), landing-experience-checker (pre-launch Quality-Score + ad-to-page message-match preflight); reuse landing-optimizer for the post-click page; read approved wording from the claims projection and submit `[needs source]` items as `operation: propose` events to the claims registry
- **Activate** — conversion-signal-qa (build/verify tracking), placement-exclusion-manager (brand-safety exclusion lists), conversion-value-mapper (margin→value so tROAS optimizes profit, not orders), then ad-account-auditor (the RQS gate + launch go/no-go; O1/O2 judged against offer-claims-registry's ledger)
- **Scale** — paid-measurement-loop, attribution-reconciler, budget-pacing-monitor (over/under-spend pacing), fatigue-frequency-manager (frequency/CTR decay + creative rotation); reuse roi-calculator / report-generator / performance-analyzer

## Rules

- `ad-account-auditor` is the launch gate: score RQS and enforce the five vetoes (R1/R2/O1/O2/A1) before any budget increase; run conversion-signal-qa first so R1/R2 can be trusted, and resolve unregistered claims via offer-claims-registry before the O1/O2 checks.
- `memory/events/claims.ndjson` is the claims/offers history. Other skills submit authorized `operation: propose` events through `registry-events.py`; `offer-claims-registry` alone accepts/rejects or mutates canonical state, while Markdown ledgers are generated views.
- Keyless Tier 1 — score from native ad-manager / GA4 / ecommerce exports the user provides; keyed Google Ads / Meta APIs are opt-in Tier-2/3 MCP only.
- Only `ad-account-auditor` computes the profile-weighted RQS; every other skill works one lever and hands off. `budget-optimizer` (reused from influencer) allocates spend across campaigns; in-platform bid strategy, search-term mining, and feed work are their own skills (`bid-strategy-planner`, `search-term-miner`, `product-feed-optimizer`).
- Label every metric Measured / User-provided / Estimated; never invent ROAS/CPA figures.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
