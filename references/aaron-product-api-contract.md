# Auto Routing Contract
`/aaron-marketing:auto` is the marketing pack's natural-language entry point across all three disciplines — SEO/GEO, influencer (IMPACT), and paid ads (ROAS) — resolving across all 54 skills (24 SEO/GEO + 18 influencer + 8 paid + 4 protocol); its `--deep` flag (`/aaron-marketing:auto --deep`) is the maximum-depth mode. `/aaron` is an optional host alias for `/aaron-marketing:auto`, not a physical command. This pack declines clearly non-marketing work instead of routing it into a fake marketing workflow; influencer and paid goals are in scope and must be routed, never declined. The four commands (`auto`, `seo-geo`, `impact`, `paid`) are the execution surface; scenario detail lives in `references/auto-routing-scenarios.md`.
## Command Surface
- `/aaron-marketing:auto` — infer discipline and intent from the goal and run the smallest useful workflow; `--deep` for exhaustive, maximum-rigor, or stress-test runs.
- `/aaron-marketing:seo-geo` — SEO/GEO end-to-end via `--mode research|create|audit|track`, with per-mode flags preserved (`--brief`/`--series`/`--refresh`/`--publish`/`--meta`/`--schema`, `--full`/`--tech`/`--visibility`/`--authority`, `--alert`/`--report`/`--remember`, `--competitors`/`--map`).
- `/aaron-marketing:impact` — influencer (IMPACT) lifecycle across six phases: insight / map / plan / activate / convert / track (`--phase` to force one).
- `/aaron-marketing:paid` — paid ads along the ROAS loop across four phases: research / orchestrate / activate / scale (`--phase` to force one).
## `/aaron-marketing:auto`
- Accept natural-language marketing tasks (SEO/GEO, influencer, or paid) when invoked directly or by verified host routing, then identify the discipline, scenario family, and risk gates.
- Execute the end-to-end command chain implied by the user goal — `/aaron-marketing:seo-geo` modes for SEO/GEO, `/aaron-marketing:impact` phases for influencer, `/aaron-marketing:paid` phases for paid — using the smallest depth that can produce the requested outcome.
- Route influencer and paid goals to the matching IMPACT or ROAS skill by name; do not decline them and do not force them through an SEO/GEO mode.
- Ask only blocking questions required for that chain, then continue until the natural stopping point is reached.
- If the user gives an object but no clear outcome, run a lightweight triage and choose the safest useful starting chain; if the user gives neither object nor outcome, ask one concise blocking question.
- Stop at evidence gaps, permission/write gates, external side effects (outreach sends, alert setup, ad launches, spend changes), publish/readiness/launch gates, oversized batches, repo governance, or memory/entity/registry writes; do not treat ordinary action words as approval.
- Do not redirect to `/aaron-marketing:auto --deep` unless the user explicitly asks for maximum-depth, exhaustive, or stress-test mode; decline clearly non-marketing work with a pack-boundary note unless a verified slash-aaron product registry provides another capability route.
- Do not publish, send outreach, launch or scale spend, write, commit, release, or claim readiness without the relevant specialist gate (`content-quality-auditor`, `domain-authority-auditor`, `content-reviewer`, `ad-account-auditor`) and explicit permission.
## `/aaron-marketing:auto --deep`
- Run only when the user explicitly asks for maximum-depth, exhaustive, or stress-test work.
- Infer depth without parameters, then start with phase plan, evidence inventory, risk gates, permission checkpoints, and stop condition.
- Coordinate the discipline commands (`seo-geo`, `impact`, `paid`) without bypassing their gates.
- Do not publish, write, commit, release, or claim ready by summary alone.
## Risk Gate Set
The canonical gates are `publish_readiness`, `ymyl`, `schema_factuality`, `batch_scale`, `external_side_effect`, `memory_or_entity_write`, `reputation_ethics`, `geo_visibility_claim`, `data_insufficient`, and `technical_indexation`. Discipline scenarios add discipline-specific gates — influencer: `brand_safety`, `engagement_authenticity`, `ftc_disclosure`, `claim_integrity`, `attribution`; paid: `launch_readiness`, `conversion_signal_integrity`, `claim_substantiation`, `attribution` — each mapping to a stop condition in the scenario record.
New high-frequency or high-risk behavior must land as a scenario first, with a real `target_skill`, expected route, blocking inputs, and failure modes, before `/aaron-marketing:auto` (including its `--deep` mode) changes.
