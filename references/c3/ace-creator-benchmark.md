# ACE — Creator Benchmark

> Scores a **creator** as a portable, brand-independent partnership asset — *"is this creator worth partnering with?"*
> Tier-2 rubric of the [C³ Scoring System](scoring-architecture.md). A creator's channel is a portable, brand-independent asset — score once, reuse across campaigns.
> **3 dimensions × ~4 items = 12 checks.**

---

## 1. Dimensions

| Dim | Question | Threshold |
|-----|----------|-----------|
| **A — Audience** | Who follows them — real, compositionally understood, and stable? | relative |
| **C — Credibility** 〔veto〕 | Is the creator safe, honest, reliable? | absolute |
| **E — Engagement** | Do they actually move their audience? | relative |

**Boundary rule (intra-ACE MECE):** fake **followers** → A (audience isn't real); fake **interaction** → E (engagement isn't real); creator **conduct** (safety, disclosure, reliability) → C. No realness signal is scored twice.

---

## 2. Checklist

### A — Audience

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| A1 | Audience Composition & Stability | Composition is measured on a stated window and materially stable | partial/older composition evidence | verified instability or material contradiction |
| A2 | Real-Follower Rate 〔**VETO**〕 | ≥ 85% estimated real | 70–84% | verified < 70% |
| A3 | Reach Reliability | Typical reach is stable relative to the creator's tier × platform × niche cohort | variable but explainable | persistently unreliable against the locked cohort |
| A4 | Growth Integrity | Organic growth curve | 1–2 explainable spikes | bought-follower spikes |

### C — Credibility 〔veto home〕

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| C1 | Brand Safety 〔**VETO**〕 | No disqualifying content | minor / old, contextual | hate / illegal / active controversy |
| C2 | Disclosure History | Sponsored posts consistently disclosed (#ad etc.) | usually | routinely undisclosed |
| C3 | Professional Reliability | Clean delivery & comms record | minor issues | ghosting / disputes / missed deadlines |
| C4 | Commercial Saturation & History | Sponsored density and disclosed category history are healthy for the cohort | elevated but transparent | materially saturated or repeatedly undisclosed commercial history |

### E — Engagement

| ID | Item | Pass (10) | Partial (5) | Fail (0) |
|----|------|-----------|-------------|----------|
| E1 | Engagement Rate | ≥ niche × tier × platform median | below median but active | far below / declining |
| E2 | Engagement Authenticity 〔**VETO**〕 | Organic comments / saves | minor anomalies | pod / bought engagement |
| E3 | Repeat Audience Action | Repeat saves, shares, replies, or other audience actions are observed on a stated window | one-off/directional action | verified absence or deterioration of repeat action |
| E4 | Relationship Depth | Meaningful comment sentiment + creator replies | mixed | shallow / negative |

---

## 3. Scoring

- Item: **Pass 10 · Partial 5 · Fail 0**
- Dimension = mean(items) × 10 → 0–100
- **ACE = A·w_A + C·w_C + E·w_E** (weights by campaign goal — see [architecture §6](scoring-architecture.md#6-weights-by-campaign-goal-scope-level))
- Bands: 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor
- A score requires complete applicable evidence. Missing/refused tool access is `unknown`, never Partial or Fail.
- **Veto:** one verified failure of **A2**, **E2**, or **C1** caps ACE at 59; 2+ verified vetoes produce `BLOCK` with no final score.

---

## 4. Data sources (be honest about availability)

| Item | Assessable from a public profile? | Needs a tool |
|------|:----------------------------------------:|--------------|
| A1, A3 | partial evidence only (visible audience/reach cues) | audience analytics for composition and windowed reach reliability |
| A2, A4 | ⚠️ no | fake-follower auditor (HypeAuditor / Modash-class) |
| C1, C2, C4 | partial evidence (review recent posts / disclosures) | longer commercial-history export where available |
| C3 | partial | CRM / references |
| E1 | ✅ computable from public counts | benchmark data for the niche median |
| E2, E3, E4 | partial evidence (read the comments) | engagement/authenticity export for rigor |

> When a tool-dependent item cannot be verified, mark it `unknown` and do not emit ACE. Never convert missing evidence to Partial, Fail, or Pass.

---

## 5. Calibration — E1 Engagement Rate

- **Pass**: a 40K-follower beauty micro-creator at 6.2% average engagement, where the beauty-micro median is ~4%. Above the niche benchmark.
- **Partial**: the same creator at 3.1% — active but below the ~4% niche median.
- **Fail**: 1.2% engagement on 40K followers, trending down over 90 days — well below benchmark, audience disengaged.

> Engagement rate is tier- and niche-relative: 6% is great for a 40K micro, mediocre for a 2K nano, and exceptional for a 2M mega. **Always compare within tier × niche × platform** — never against a fixed number.

## 6. Intra-ACE quick reference

| Concept | Lives in | Veto? |
|---------|----------|-------|
| Fake followers / bought audience | A2 | ✅ |
| Brand safety / scandal | C1 | ✅ |
| Pod / bought engagement | E2 | ✅ |
| Reach reliability (tier × platform × niche) | A3 | — |
| Creator × brand fit / exclusivity conflict | ROI.O1 | — |
| Campaign conversion | ROI.I2 | — |
| Real influence (engagement rate) | E1 | — |
