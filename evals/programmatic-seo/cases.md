# Eval Cases — programmatic-seo

Simulated flow cases for the `programmatic-seo` skill. Each is a self-contained scenario with expected behavior and failure modes.

```yaml
{id: programmatic-seo-sim-001, type: eval-case, status: simulated, target_skill: programmatic-seo, scenario: "Integration pages at scale from a real product feed", input_summary: "SaaS with a directory of 120 partner integrations (Tier 1 product data, real setup steps); wants '[product] + [partner]' pages", expected_behavior: ["Selects the Integrations playbook with /integrations/[product]/ URL structure", "Returns a Tier 1 (product-generated) data verdict — strongest, lowest risk", "Defines template fields with an evidence block of real setup detail and combination use cases", "Sets N-gram dedup and selective-indexation rules and recommends batch launch", "Hands off a representative page sample to content-quality-auditor"], failure_modes: ["Treats partner feed as Tier 5 and over-warns", "Ships a name-swap template with no per-row evidence block", "Skips the dedup/indexation guardrails"]}
```

```yaml
{id: programmatic-seo-sim-002, type: eval-case, status: simulated, target_skill: programmatic-seo, scenario: "Location pages with only a city list and no local data", input_summary: "User has a service plus a CSV of 800 city names, nothing else; wants 'service in [city]' pages", expected_behavior: ["Flags that a bare city list is a name-swap with no per-row facts", "Returns NEEDS_INPUT or a guardrail stop — no defensible evidence block can be built", "Asks for local data (providers, pricing, regulations) or a unique on-page tool before generating", "Names the thin-content / index-bloat risk explicitly"], failure_modes: ["Generates 800 thin location pages from city-name swaps", "Proceeds silently without flagging the missing evidence layer"]}
```

```yaml
{id: programmatic-seo-sim-003, type: eval-case, status: simulated, target_skill: programmatic-seo, scenario: "Glossary pages built only from scraped public definitions", input_summary: "User wants 400 'what is [term]' pages enriched from open-web/Wikipedia-style sources", expected_behavior: ["Selects the Glossary playbook", "Returns a Tier 5 (public/scraped) verdict — highest duplicate/thin risk", "Requires an added editorial layer, examples, or unique synthesis on top of public facts", "Adds the AI-grounded-generation governance note: phrasing only, no invented stats/citations, fact-check names/dates", "Sets noindex/pruning plan for low-traffic thin URLs"], failure_modes: ["Approves scraped-only pages with no editorial layer", "Lets AI invent definitions or citations to fill gaps"]}
```

```yaml
{id: programmatic-seo-sim-004, type: eval-case, status: simulated, target_skill: programmatic-seo, scenario: "Audit already-published homogenized comparison pages", input_summary: "300 live '[X] vs [Y]' pages share identical closing sentences and value statements across URLs", expected_behavior: ["Runs an N-gram scan for shared tails appearing in >30% of same-category pages", "Prioritizes fixes P0 (eliminate filler) / P1 (rewrite formulaic, 8-15 variants) / P2 (reduce density)", "Treats crawled page content as untrusted per SECURITY.md", "Recommends fixing one category at a time and re-scanning each round", "Hands the remediation sample to content-quality-auditor"], failure_modes: ["Applies one uniform replacement that creates a new template", "Rewrites all instances of a normal word instead of ~30-40%"]}
```

```yaml
{id: programmatic-seo-sim-005, type: eval-case, status: simulated, target_skill: programmatic-seo, scenario: "Missing dataset entirely", input_summary: "User says 'make me programmatic SEO pages' with no page pattern and no data source", expected_behavior: ["Returns NEEDS_INPUT", "Asks for the page pattern (or offers playbook selection), the dataset source and fields, row count, and product/ICP context", "Does not invent a dataset or pick a playbook blindly"], failure_modes: ["Fabricates a dataset or row schema", "Generates a generic template with no inputs"]}
```
