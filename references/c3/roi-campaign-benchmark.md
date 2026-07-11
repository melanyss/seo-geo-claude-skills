# ROI — Campaign Benchmark

> Scores a whole **campaign** — *"did / will the campaign deliver?"* — and rolls up its creators (ACE) and contents (ART).
> Tier-2 rubric of the [C³ Scoring System](scoring-architecture.md). Rolls up the campaign's creators (ACE) and contents (ART); fed by post-campaign analytics & attribution data.
> **3 dimensions × ~4 items = 12 checks.**

---

## 1. Dimensions

**ROI** reads end-first — *begin with the end in mind*: name the **R**eturn you must earn, **O**rchestrate the campaign to reach it, then measure the **I**mpact delivered.

| Dim | Question | Threshold | When |
|-----|----------|-----------|------|
| **R — Return** | What return must this earn — and did it? | relative | target set **upfront**, result measured **after** |
| **O — Orchestration** | Were the right creators / mix / budget / timing chosen to get there? | absolute | judged **upfront** |
| **I — Impact** | Did it hit the goals, and is that measured rigorously? | relative | measured **after** |

**This is where Fit lives** (O1 — creator-brand fit) and where content **conversion** is actually verified (I2). See [architecture §7](scoring-architecture.md#7-cross-scope-mece-boundaries-no-double-count).

---

## 2. Checklist

### R — Return (efficiency — needs cost + outcome)

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| R1 | ROI / ROAS | ≥ benchmark / clearly positive | ~ breakeven | negative |
| R2 | Cost Efficiency | CPE / CPM / CPA ≤ benchmark | near benchmark | well above |
| R3 | Content Asset Value | Usage rights secured & content repurposed | rights but unused | one-and-done, no rights |
| R4 | Relationship Value | Built a repeatable partnership / pipeline | neutral | damaged / one-off |

### O — Orchestration (decisions — judgeable before spend)

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| O1 | Creator–Brand Fit | Campaign-specific fit is strong using ACE facts plus brand/category evidence | mixed | materially misaligned picks or active conflict |
| O2 | Roster Mix | Tier mix & count suit the goal | workable but lopsided | wrong mix (all-mega for a conversion play) |
| O3 | Budget Allocation | Efficient, justified split incl. paid amplification | defensible but suboptimal | concentrated / unjustified |
| O4 | Timing & Sequencing | Well-timed (trend / season), good cadence & sequencing | ok | poorly timed / clustered / missed window |

### I — Impact (outcomes — needs post-campaign data)

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| I1 | KPI Attainment | Met / exceeded the brief's targets | 70–99% of target | < 70% |
| I2 | Conversion / Action | Drove the target action above benchmark | some action | little / none |
| I3 | Attribution Rigor 〔**flag**〕 | Rigorous attribution (codes / UTM / holdout) | partial / last-click only | unattributable / vanity-only |
| I4 | Earned Amplification | Meaningful organic spread / UGC / brand-lift | some | none beyond paid |

---

## 3. Scoring

- Item: **Pass 10 · Partial 5 · Fail 0**
- Dimension = mean(items) × 10 → 0–100
- **ROI = R·w_R + O·w_O + I·w_I** (weights by campaign goal — see §8)
- Bands: 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor
- **No veto** (per [architecture §5](scoring-architecture.md#5-veto-items-red-lines)). But **I3 Fail raises a "results-unverified" flag** — when attribution is broken, treat I1 / I2 / R1 / R2 as **low-confidence**, not as scored facts.

---

## 4. Rollup & campaign health

A campaign **does not collapse to one number**. Per [architecture §8](scoring-architecture.md#8-fractal-rollup), show three:

```
Creator quality  =  budget-weighted mean of its creators' ACE scores
Content quality  =  mean of its contents' ART scores
Campaign exec    =  ROI  (this rubric)
```

Read them together via the [Creator × Content diagnosis matrix](scoring-architecture.md#9-combined-diagnosis-creator--content).
- **O1 (Creator-Brand Fit)** consumes brand-independent ACE facts plus campaign-specific brand/category evidence; ACE itself does not score fit.
- **I2 (Conversion)** is where the appeal ART scored gets *verified* as real action.

---

## 5. Forecast → Measure → Calibrate (Separate Reads)

The advantage static rubrics lack — ROI has a time axis:

1. **Before spend** — lock the goal, target, assumptions, and an all-forecast ROI run. Items requiring actual outcomes are `na` only where catalog policy permits; otherwise remain Unknown and no forecast scope score is emitted.
2. **After the declared lag** — create a separate all-actual ROI run and compare it with the preserved forecast record.
3. **Calibrate** — test whether version-locked ACE/ART/ROI scores predict preregistered outcomes across a defensible sample. Never tune weights from one campaign or rewrite the forecast in place.

---

## 6. Data sources

| Group | Availability |
|-------|--------------|
| R (Return) | needs **cost data + outcome data** |
| O (Orchestration) | judgeable from the **plan**, upfront — no tooling needed |
| I (Impact) | needs **post-campaign analytics + attribution** tooling |

> ROI is the most data-dependent scope. Keep forecast and actual states separate, provenance-labeled, and linked; never mix them in one score or CVI.

---

## 7. Calibration — I3 Attribution Rigor

- **Pass**: unique promo codes per creator + UTM links + a 2-week geo-holdout; sales lift is attributable to specific creators with confidence.
- **Partial**: a single shared promo code + last-click attribution; directional, but can't separate creator contribution or rule out other channels.
- **Fail**: "we got 2M impressions and sales went up that month" — no codes, no links, no holdout; the uplift is unattributable → **results-unverified flag**.

---

## 8. Weights by campaign goal

| Goal | Return | Orchestration | Impact |
|------|:------:|:-------------:|:------:|
| Awareness | 20% | 40% | 40% |
| Engagement | 25% | 35% | 40% |
| Conversion | 40% | 25% | 35% |
| Brand-building | 25% | 40% | 35% |
