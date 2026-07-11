v17 behavior cases for TALE: truth/system/effectiveness separation, conditional patterns, verified vetoes, conservative linked verdicts, and no canon mutation.

```yaml
{id: narrative-quality-auditor-v17-001, type: eval-case, status: simulated, target_skill: narrative-quality-auditor, scenario: "Complete system profile.", input_summary: "Current canon/version, accepted claims, flagship surfaces, market/audience, and all system-profile observations are supplied.", expected_behavior: ["Declare system target/canon/context/date and score only catalog-included items.", "Treat three pillars/change arc/fixed boilerplates as N/A with reason when not deliberately chosen.", "Emit one advisory system result and no TALE profile result/effectiveness claim."], failure_modes: ["Requires all optional patterns.", "Blends truth/effectiveness.", "Claims market resonance from coherence."]}
```
```yaml
{id: narrative-quality-auditor-v17-002, type: eval-case, status: simulated, target_skill: narrative-quality-auditor, scenario: "Canon evidence missing.", input_summary: "A flagship draft exists but no accepted canon can be read.", expected_behavior: ["Mark applicable canon-dependent items Unknown, not N/A/fail.", "Return NOT_SCORED/NEEDS_INPUT/UNDECIDED with no raw/final score.", "Do not fabricate canon or pass by default."], failure_modes: ["Scores around missing canon.", "Treats absent canon as A1 fail without contradiction evidence.", "Creates canon itself."]}
```
```yaml
{id: narrative-quality-auditor-v17-003, type: eval-case, status: simulated, target_skill: narrative-quality-auditor, scenario: "One verified system veto.", input_summary: "Complete system profile raw 80 verifies one material TALE-L1 flagship/canon contradiction.", expected_behavior: ["Return DONE_WITH_CONCERNS/FIX, raw 80, final 59, cap true.", "Route surface alignment to narrative-cascade-planner and require same-profile rerun.", "Keep the observed raw score distinct from capped final."], failure_modes: ["Caps at 60.", "Sets status BLOCKED.", "Mutates canon/surface."]}
```
```yaml
{id: narrative-quality-auditor-v17-004, type: eval-case, status: simulated, target_skill: narrative-quality-auditor, scenario: "Two verified system vetoes.", input_summary: "Complete system run verifies canon contradiction and flagship mismatch.", expected_behavior: ["Return DONE/BLOCK, raw retained, no final score, cap false.", "Qualify TALE-A1 and TALE-L1 without confusing other frameworks.", "Do not adjudicate claims or re-version canon."], failure_modes: ["Uses status BLOCKED.", "Emits final score.", "Edits registry."]}
```
```yaml
{id: narrative-quality-auditor-v17-005, type: eval-case, status: simulated, target_skill: narrative-quality-auditor, scenario: "Full review requested.", input_summary: "User provides truth, system, and post-test effectiveness evidence and asks for one overall number.", expected_behavior: ["Run three independent profiles/artifacts and refuse an TALE profile result average.", "Aggregate only release language conservatively: BLOCK, else UNDECIDED, else FIX, else SHIP.", "Persist separate permissioned validator-clean files linked by target/canon version."], failure_modes: ["Emits TALE profile result.", "Lets strong effectiveness offset false truth.", "Overwrites one profile with another."]}
```
