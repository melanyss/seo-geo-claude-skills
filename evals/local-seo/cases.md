```yaml
{id: local-seo-sim-001, type: eval-case, status: simulated, target_skill: local-seo, scenario: "Single-location storefront wants full local SEO.", input_summary: "Do local SEO for Bella's Cafe, 12 Main St, Austin TX, one storefront, phone provided.", expected_behavior: ["Confirm inputs and set one canonical NAP string with format choices noted.", "Produce GBP checklist covering category, description (keyword in first 100 chars), hours, address, photos.", "Return citation list ordered GBP > Apple Maps > Yelp/Bing/Facebook > BBB/Foursquare/Nextdoor > niche, with status per source.", "Hand off location page to on-page-seo-auditor."], failure_modes: ["Skips NAP consistency and jumps to citations.", "Mass-submits to every directory instead of priority order.", "Treats a service-area business as a storefront."]}
```

```yaml
{id: local-seo-sim-002, type: eval-case, status: simulated, target_skill: local-seo, scenario: "Service-area business across multiple cities.", input_summary: "HVAC company, no storefront, covers 5 cities; plan GBP and location pages.", expected_behavior: ["Hide address in GBP and define the 5 service areas.", "Plan distinct service-area pages with area-specific content, not duplicated boilerplate.", "Keep one canonical NAP across all pages and listings."], failure_modes: ["Publishes a physical address for an address-less business.", "Creates near-duplicate city pages.", "Recommends a P.O. box address."]}
```

```yaml
{id: local-seo-sim-003, type: eval-case, status: simulated, target_skill: local-seo, scenario: "NAP audit only.", input_summary: "Audit NAP consistency and give a citation priority list for an existing business.", expected_behavior: ["Compare current NAP across GBP and known directories against a canonical string.", "Flag duplicate entries and missing listings.", "Recommend fixing inconsistencies before adding new citations.", "Label each field Measured or User-provided."], failure_modes: ["Adds new citations before fixing existing errors.", "Presents estimated values as verified.", "Ignores duplicate listings."]}
```

```yaml
{id: local-seo-sim-004, type: eval-case, status: simulated, target_skill: local-seo, scenario: "Missing required NAP input — NEEDS_INPUT.", input_summary: "User says 'optimize my Google Business Profile' but provides no address, phone, or business type.", expected_behavior: ["Stop and ask for name, address, phone, and storefront-vs-service-area before building.", "Return status NEEDS_INPUT naming exactly what is missing.", "Do not fabricate an address or category."], failure_modes: ["Guesses an address or NAP format.", "Produces a citation list with no verified NAP.", "Proceeds silently with placeholders."]}
```

```yaml
{id: local-seo-sim-005, type: eval-case, status: simulated, target_skill: local-seo, scenario: "Inconsistent NAP across sources — guardrail before citations.", input_summary: "Address shows as '12 Main Street' on GBP but '12 Main St, Ste 4' on Yelp; user wants 50 new citations.", expected_behavior: ["Detect the NAP mismatch and stop before mass citation building.", "Require one agreed canonical string first.", "Explain that inconsistent NAP can split the listing into separate entities."], failure_modes: ["Builds 50 citations on top of an unresolved mismatch.", "Picks a canonical string without user confirmation.", "Treats the two formats as equivalent without flagging."]}
```
