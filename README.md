# Aaron Marketing Skills

**52 skills. 5 commands. SEO/GEO, influencer, and paid ads marketing on one shared contract.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat)](https://github.com/aaron-he-zhu/aaron-marketing-skills)
[![Version](https://img.shields.io/badge/version-11.0.0-orange)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills)](https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)](https://claude.ai/download)

[English](README.md) | [中文](docs/README.zh.md)

Claude Skills and Commands for three marketing disciplines on one operating contract:

- **Search (SEO/GEO)** — 26 skills for keyword research, content creation, programmatic/local/comparison builds, technical audits, schema, site architecture, monitoring, AI traffic, quality gates, entity truth, and campaign memory.
- **Influencer marketing (IMPACT)** — 18 skills for audience insight, influencer discovery, campaign planning, outreach, content amplification, and ROI tracking.
- **Paid ads** — 4 skills for campaign structure, ad creative, account audits, and the measurement loop.

Skill content is zero-dependency Markdown; Claude Code hooks use a small Bash runner. Four evaluation frameworks ship inside: [CORE-EEAT](references/core-eeat-benchmark.md) (80-item content quality), [CITE](references/cite-domain-rating.md) (40-item domain authority), [C³](references/c3-benchmark.md) (influencer Creator/Content/Campaign), and [ROAS](references/roas-benchmark.md) (paid ads Return/Offer/Audience/Spend-efficiency).

> The SEO/GEO half also ships on its own, unchanged, at [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) for users who only want search work.

## Quick Start

Install with Claude Code, any Agent Skills-compatible host, or a plain `git clone`:

| Tool | Install |
|------|---------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` then `/plugin install aaron-marketing@aaron` |
| skills.sh / generic Agent Skills hosts | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| Any host | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

In Claude Code, `marketplace add` only registers the catalog — run `/plugin install aaron-marketing@aaron` (or pick it from `/plugin`) to actually enable the skills and commands. Single skill on generic hosts: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`.

If your host supports automatic skill routing, try a natural-language request:

```text
Research keywords for my SaaS product targeting small teams
```

```text
Find TikTok creators for a skincare launch and score their fit
```

Slash-command entrypoint when your host exposes `./commands/`:

```text
/aaron-marketing:auto audit https://example.com/blog/my-article
```

Optional tools are documented in [CONNECTORS.md](CONNECTORS.md); every skill also works at Tier 1 with user-provided data.

## Operating Model

Every skill follows the same activation contract: Quick Start, Skill Contract, Handoff Summary, Data Sources, Instructions, Reference Materials, and Next Best Skill. Four cross-cutting skills form the protocol layer:

| Protocol skill | Role |
|----------------|------|
| `content-quality-auditor` | 80-item CORE-EEAT publish gate |
| `domain-authority-auditor` | 40-item CITE trust gate |
| `entity-optimizer` | Canonical entity profile |
| `memory-management` | HOT/WARM/COLD project memory (capture · promote · demote · archive · query) |

Two more auditor-class gates emit to memory alongside the two above: `content-reviewer` (C³ ART gate → `memory/audits/influencer/`) and `ad-account-auditor` (ROAS RQS gate → `memory/audits/paid/`).

Shared refs: [skill-contract.md](references/skill-contract.md), [state-model.md](references/state-model.md), [auditor-runbook.md](references/auditor-runbook.md).

## Skills

### Search — SEO/GEO (26)

| Phase | Skills |
|-------|--------|
| Research | [keyword-research](research/keyword-research/SKILL.md), [competitor-analysis](research/competitor-analysis/SKILL.md), [serp-analysis](research/serp-analysis/SKILL.md), [content-gap-analysis](research/content-gap-analysis/SKILL.md) |
| Build | [seo-content-writer](build/seo-content-writer/SKILL.md), [geo-content-optimizer](build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](build/schema-markup-generator/SKILL.md), [programmatic-seo](build/programmatic-seo/SKILL.md), [parasite-seo](build/parasite-seo/SKILL.md), [comparison-page-builder](build/comparison-page-builder/SKILL.md), [local-seo](build/local-seo/SKILL.md) |
| Optimize | [on-page-seo-auditor](optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](optimize/internal-linking-optimizer/SKILL.md), [content-refresher](optimize/content-refresher/SKILL.md), [site-architecture](optimize/site-architecture/SKILL.md) |
| Monitor | [rank-tracker](monitor/rank-tracker/SKILL.md), [backlink-analyzer](monitor/backlink-analyzer/SKILL.md), [performance-reporter](monitor/performance-reporter/SKILL.md), [alert-manager](monitor/alert-manager/SKILL.md), [ai-traffic](monitor/ai-traffic/SKILL.md) |
| Cross-cutting | [content-quality-auditor](cross-cutting/content-quality-auditor/SKILL.md), [domain-authority-auditor](cross-cutting/domain-authority-auditor/SKILL.md), [entity-optimizer](cross-cutting/entity-optimizer/SKILL.md), [memory-management](cross-cutting/memory-management/SKILL.md) |

### Influencer — IMPACT (18)

| Phase | Skills |
|-------|--------|
| Insight | [audience-analyzer](insight/audience-analyzer/SKILL.md), [niche-researcher](insight/niche-researcher/SKILL.md), [trend-spotter](insight/trend-spotter/SKILL.md) |
| Map | [influencer-discovery](map/influencer-discovery/SKILL.md), [fit-scorer](map/fit-scorer/SKILL.md), [competitor-tracker](map/competitor-tracker/SKILL.md) |
| Plan | [campaign-planner](plan/campaign-planner/SKILL.md), [brief-generator](plan/brief-generator/SKILL.md), [budget-optimizer](plan/budget-optimizer/SKILL.md) |
| Activate | [outreach-manager](activate/outreach-manager/SKILL.md), [content-reviewer](activate/content-reviewer/SKILL.md), [contract-helper](activate/contract-helper/SKILL.md) |
| Convert | [content-amplifier](convert/content-amplifier/SKILL.md), [ugc-repurposer](convert/ugc-repurposer/SKILL.md), [landing-optimizer](convert/landing-optimizer/SKILL.md) |
| Track | [performance-analyzer](track/performance-analyzer/SKILL.md), [roi-calculator](track/roi-calculator/SKILL.md), [report-generator](track/report-generator/SKILL.md) |

### Paid Ads (8)

Phases are the conceptual ROAS loop (Research → Orchestrate → Activate → Scale); skills live flat under `paid/`.

| Phase | Skills |
|-------|--------|
| Research | [campaign-architect](paid/campaign-architect/SKILL.md), [audience-segment-builder](paid/audience-segment-builder/SKILL.md) |
| Orchestrate | [ad-creative-builder](paid/ad-creative-builder/SKILL.md), [ad-test-designer](paid/ad-test-designer/SKILL.md) |
| Activate | [ad-account-auditor](paid/ad-account-auditor/SKILL.md), [conversion-signal-qa](paid/conversion-signal-qa/SKILL.md) |
| Scale | [paid-measurement-loop](paid/paid-measurement-loop/SKILL.md), [attribution-reconciler](paid/attribution-reconciler/SKILL.md) |

Reused cross-discipline: [budget-optimizer](plan/budget-optimizer/SKILL.md) (spend + bid-pacing mode), [landing-optimizer](convert/landing-optimizer/SKILL.md), [roi-calculator](track/roi-calculator/SKILL.md), [report-generator](track/report-generator/SKILL.md), [performance-analyzer](track/performance-analyzer/SKILL.md).

## Commands

Five commands cover the search workflow end-to-end; influencer skills are reached by name or via `/aaron-marketing:auto` routing.

| Command | Use it for |
|---------|-----------|
| `/aaron-marketing:auto` | Describe any goal — infers intent and runs the smallest useful workflow (`--deep` for exhaustive/stress-test) |
| `/aaron-marketing:research` | Keyword demand, SERP intent, competitors, content gaps, site/topic/entity maps |
| `/aaron-marketing:create` | Brief, write, series, refresh, CMS-neutral publish package (`--brief`/`--series`/`--refresh`/`--publish`/`--meta`/`--schema`) |
| `/aaron-marketing:audit` | On-page + CORE-EEAT quality, technical SEO, AI visibility, domain authority (`--full`/`--tech`/`--visibility`/`--authority`) |
| `/aaron-marketing:track` | Rankings, alerts, performance reports, project memory (`--alert`/`--report`/`--remember`) |

Daily work normally starts with `/aaron-marketing:auto`, which runs the workflow implied by your goal and stops only at blocking decisions. The other four are explicit mode entrypoints.

Breaking rename note: this library's commands use `/aaron-marketing:`. Older `/seo:*` and `/aaron-seo-geo:*` names recover via `/aaron-marketing:auto` — for example, `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` returns `/aaron-marketing:audit https://example.com/blog/post`.

Command files: [commands/](commands/).

## Recommended Workflow

**Search (SEO/GEO):**
1. Research: `keyword-research` -> `competitor-analysis` -> `content-gap-analysis`.
2. Build: `seo-content-writer` -> `geo-content-optimizer` -> `meta-tags-optimizer` / `schema-markup-generator`.
3. Optimize: `content-quality-auditor` -> `on-page-seo-auditor` -> `technical-seo-checker`.
4. Monitor: `rank-tracker` -> `performance-reporter` -> `alert-manager`.

**Influencer (IMPACT):**
1. Insight: `audience-analyzer` -> `trend-spotter` -> `niche-researcher`.
2. Map: `influencer-discovery` -> `fit-scorer` (scored on C³ ACE) -> `competitor-tracker`.
3. Plan: `campaign-planner` -> `brief-generator` -> `budget-optimizer`.
4. Activate: `outreach-manager` -> `content-reviewer` (ART gate) -> `contract-helper`.
5. Convert: `content-amplifier` -> `ugc-repurposer` -> `landing-optimizer`.
6. Track: `performance-analyzer` -> `roi-calculator` -> `report-generator`.

For a full trust review, pair `content-quality-auditor` with `domain-authority-auditor` for a 120-item assessment. If `memory-management` is active, handoffs and open loops are retained in HOT/WARM/COLD memory.

## References

| Reference | Purpose |
|-----------|---------|
| [core-eeat-benchmark.md](references/core-eeat-benchmark.md) | 80-item content quality benchmark (CORE-EEAT) |
| [cite-domain-rating.md](references/cite-domain-rating.md) | 40-item domain authority benchmark (CITE) |
| [c3-benchmark.md](references/c3-benchmark.md) | Influencer Creator/Content/Campaign benchmark (C³ · ACE/ART/ROI) |
| [roas-benchmark.md](references/roas-benchmark.md) | Paid ads Return/Offer/Audience/Spend-efficiency benchmark (ROAS · RQS rollup) |
| [auditor-runbook.md](references/auditor-runbook.md) | Auditor handoff schema, cap arithmetic, artifact gate |
| [CONNECTORS.md](CONNECTORS.md) | Optional MCP/tool connector tiers |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Release state is tracked in [VERSIONS.md](VERSIONS.md); security guidance is in [SECURITY.md](SECURITY.md).

## Disclaimer

These skills assist SEO/GEO and influencer-marketing workflows but do not guarantee rankings, AI citations, traffic, engagement, or business outcomes. Influencer-compliance checks (FTC disclosure, claim integrity) are guidance, not legal advice. Verify recommendations with qualified professionals before relying on them for major strategy or legal decisions.

## License

Apache License 2.0

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
