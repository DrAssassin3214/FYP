# PROJECT HANDOFF SUMMARY: "Bricks-ly" (B.Tech Civil Engineering final-year project)

> **To the AI reading this:** this is a handoff summary of a long working session with another AI assistant. Treat it as
> the full context. Continue from the "Where we are now" section. The code lives on one team member's laptop
> (`C:\Users\Omkar\Desktop\FYP`); you cannot see it unless someone pastes files. Do not invent papers, numbers or site
> data. The project's integrity rules (section 3) are strict and the professor will check them.

---

## 1. What the project is

- **Course:** B.Tech Civil Engineering, final-year project, team of 3, India.
- **Topic:** a literature-grounded **decision-support tool for delay risk in ONE construction activity: brick/blockwork masonry** (Indian sites).
- **App name:** **Bricks-ly** (local web app; Python + Flask back end, plain JavaScript front end, runs offline on 127.0.0.1).
- **What the app does now:** risk **identification** → risk **register** → **probability–impact risk matrix** → exports. Nothing else.
- **Scope history:** an earlier, bigger version also had Monte Carlo schedule simulation, cost/EMV, mitigation decisions and productivity models. On 2026-09-28 the scope was cut to identification + register + matrix only. The old code is still on disk (unused) and a full backup exists.

## 2. Methodology (how to describe it in the report)

| Stage | Established method | Where it is in the tool |
|---|---|---|
| Overall process | ISO 31000 (identify → analyse → evaluate → treat) / PMI-PMBOK risk management | The step flow of the app |
| Risk identification | Literature review + checklist + rule-based checks on site conditions + expert input | Risk library (10 risks (superseded, see section 8; the library has 38 risks), 11 site-fact rules, evidence-cited AI suggestions |
| Ranking from surveys | Relative Importance Index (RII), standard in construction delay-cause studies | "Literature seed" |
| Qualitative assessment | Probability–impact matrix (5×5) | Matrix screen and register |
| Quantitative assessment (optional, NOT built now) | PERT three-point delays + Monte Carlo simulation | Old code exists; user said "not now" |

## 3. Integrity rules (non-negotiable)

1. Never invent papers, numbers or site data.
2. Every number carries a **Source** label: Literature, Historical Data, User Input, Expert Judgment, Derived Calculation, Assumption.
3. The AI may **propose risks and cite evidence**, but **never supplies probabilities, delays or costs**.
4. An RII (survey importance score) is **NOT a probability and NOT days of delay**. It only supports a relative ranking.
5. Illustrative/example values are always labelled ILLUSTRATIVE.
6. No novelty over-claims.

## 4. How the tool works (current version)

**Input (a "case"):** project info; activity name + planned duration (working days); site facts; list of risks, each with probability *p* (0–1) and a delay range in days (min / most likely / max, Beta-PERT by default), each with a Source.

**Core risk library (10 risks; the library now has 38, see the expansion note below) (superseded, see section 8):**
R-MAT material shortage / late delivery · R-TOOL tools & equipment delay · R-LAB labour absenteeism/shortage · R-SKILL unskilled labour · R-PLAN poor planning / unrealistic schedule · R-SAFE unsafe conditions / work at height · R-WX rain/monsoon stoppage · R-RWK rework · R-PAY payment delay · R-DES design changes / incomplete drawings.

**Rule engine (11 rules, each flags a risk as "elevated"):**
required_workers > available_workers → R-LAB · material_lead_time_days > material_buffer_days → R-MAT · material_stock_days < planned_duration_days → R-MAT · tools_shortage → R-TOOL · monsoon_overlap → R-WX · work_at_height → R-SAFE · payment_delay_expected → R-PAY · design_incomplete → R-DES · prior_rework_history → R-RWK · schedule_compressed → R-PLAN · skilled_masons_short → R-SKILL.
Flagged risks are **auto-added** to the register (with empty numbers).

**Matrix logic:**
- Probability class from *p* with equal-width edges 0.2 / 0.4 / 0.6 / 0.8 (an Assumption).
- Impact class = expected delay ÷ planned duration, binned by four user-entered "impact bin edges" (e.g. 0.02 / 0.05 / 0.10 / 0.20). These edges are hidden behind a three-dots button on the matrix screen.
- Score = p class × impact class; Low if score ≤ 5, Moderate 6–10, High 11–15, Extreme ≥ 16 (thresholds are Assumptions).
- Ordinal prioritisation only, not a quantity.

**Literature seed (revised 2026-10-05):** library risks with **no numbers entered** are still placed on the matrix from survey RII values. Data: `data/literature_seed.json` (182 rows from 11 studies: 178 factor values and 4 unmapped or group-level rows; the table/page is recorded per study, not per row (superseded, see section 8)), also exported as **`RII_Masonry_Literature.xlsx`** (built by `scripts/build_rii_workbook.py`; the app and the workbook read the same file).
- **Seed studies** (India/Sri Lanka): M01 Karthik & Rao 2019 (India, masonry, N=44), A02 Ponmalar 2018 (Chennai, masonry), M06 Dixit 2019 (India, N=201), A14 Abeysinghe 2022 (Sri Lanka, N=163), A15 Manoharan 2022 (Sri Lanka).
- **Method:** map each factor to a tool risk (Direct / Related; only Direct used) → average each study's direct items → average across studies = seed mean RII → rank → five equal bands of two → class used for BOTH axes → a rule flag raises the p class by 1 → entered numbers replace the seed. Seeded cells: dashed outline, "literature seed".

**Table below: original 10-risk ranks and classes (superseded, see section 8); the 30-risk table is in section 8.2.**

| Risk | Seed mean RII | Rank | Class | Study means |
|---|---|---|---|---|
| R-MAT | 0.7889 | 1 | 5 | M01 0.777, A02 0.780, A14 0.810 |
| R-SAFE | 0.7865 | 2 | 5 | M01 0.787 (unsafe conditions 0.809, work at height 0.764) |
| R-SKILL | 0.7831 | 3 | 4 | M01 0.759, A02 0.787, A15 0.803 |
| R-PLAN | 0.7771 | 4 | 4 | M01 0.791, M06 0.763 |
| R-PAY | 0.7733 | 5 | 3 | M01 0.773, A02 0.776, M06 0.771 |
| R-LAB | 0.7662 | 6 | 3 | M01 0.723, A02 0.751, A14 0.825 |
| R-DES | 0.7585 | 7 | 2 | M01 0.732, M06 0.785 |
| R-RWK | 0.7561 | 8 | 2 | M01 0.736, M06 0.776 |
| R-TOOL | 0.7528 | 9 | 1 | M01 0.746, A02 0.760 |
| R-WX | 0.6934 | 10 | 1 | M01 0.764, A02 0.700, M06 0.657, A14 0.653 |

Spread: nine of the ten risks lie within 0.036 of each other (only R-WX is clearly lower), so the middle of the order is fragile (superseded, see section 8); for 30 risks the top 24 lie within 0.096 and one M01 RII has a standard error of about 0.03).

**Validation already done (superseded, see section 8); the wording 'validation' is withdrawn, it is an agreement check (Spearman rank correlation with held-out studies the model does not use):** M10 Middle East meta-analysis of 10 surveys: rho = 0.40 (n = 9, p = 0.29), weak agreement. M15 Brazil managers: rho = 0.36 (n = 7, p = 0.43), weak agreement. M14 Indonesia **workers**: rho = −0.68 (n = 7, p = 0.09), moderate disagreement. None significant at 5%. Reading: manager-side surveys weakly agree with the seed; workers rank pay, tools and weather higher. A10, A21, Hassoon 2025 overlap with fewer than 4 risks, so they were not tested.

**Statistical analysis (superseded, see section 8) (2026-10-06; `scripts/stats_rii.py`, `docs/Statistical_Analysis.docx`, `docs/rii_statistics.json`):** Kruskal-Wallis across the 10 risks is not significant (H=14.2, p=0.115; without R-WX p=0.35), but R-WX is rated lower than the rest (Mann-Whitney p=0.005). Leave-one-study-out: rho about 0.88 or higher, except dropping M01 (0.72). Bootstrap rank intervals are wide (e.g. R-LAB 2 to 10). Agreement with held-out studies (Spearman, permutation p): M10 0.40 (p=0.30), M15 0.36 (p=0.44), M14 -0.68 (p=0.11); none significant. The studies disagree with each other: mean pairwise rho 0.10 over 13 pairs, Kendall W = 0.16 (p=0.63). Reading: only 'weather is rated lower' is statistically supported; the order of the other nine risks is not. (Withdrawn, see section 8.6.)

**Standardised analysis (superseded, see section 8, especially the seed-vs-pooled correlations) (2026-10-07; `scripts/stats_standardised.py`, `docs/Statistical_Analysis_Standardised.docx`, Standardised sheet in the workbook):** studies put on one level with within-study z-scores (raw RII differs by rating scale: study means 0.59 to 0.75). Only studies with complete factor lists are standardised: Analysis A = M06, M10, M14, M15; Analysis B adds M01 (truncated list, flagged). A, B: no significant difference between risks (two-way model p = 0.23 and 0.49). Pooled order A: rework, design, payment, unskilled labour, planning, material, tools, weather, labour, safety. Seed order vs pooled z order: rho -0.13 (A) and 0.16 (B), unrelated. The earlier 'weather lower' finding weakens (CI includes 0). Decision pending with the supervisor: keep the seed as a weak labelled starting order (current) or move to a standardised pooled ranking. The app was NOT changed.

**Risk library expanded (2026-10-07):** the library is no longer limited to 10 risks. It now has **38 risks in 11 categories** (Labour 11, Management 6, Material 5, Financial 3, Design 3, External 3, Safety 2, Quality 2, Equipment 1, Site 1, Weather 1), built from the factors transcribed so far from the 11 studies (superseded, see section 8); the earlier wording 'every factor' is withdrawn (`data/risk_library_masonry.json`; each factor in `data/literature_seed.json` now maps to a risk, only 4 unclear/group-level factors stay unmapped). Each risk carries a `scope` (activity or project-level) and the paper values behind it. The original 10 risks keep their IDs and mean RII. The seed bands are now cut over the 30 risks that have a seed-study value (6 per band); 8 library risks (R-TRN, R-PRD, R-SUB, R-CLI, R-QLT, R-DEF, R-GOV, R-FIN) have no seed value and stay off the matrix until numbers are entered. UI: the Library tab is grouped by category, filterable, with Add all buttons (numbers stay empty). The earlier worked-calculation and statistics documents describe the original core ten risks; banding the core ten over 30 risks changes their class (e.g. R-PLAN and R-PAY are now class 5, weather class 2). With the larger set the workbook's validation shows M15 rho 0.63 (n=11, p=0.039), M10 0.28 (n=19, p=0.24), M14 -0.18 (n=13, p=0.55): the result depends on which risks are compared; one p below 0.05 out of three tests is not robust to correction.

**Statistics re-run on the 38-risk library (2026-10-07; partly superseded, see section 8.3 to 8.6 for withdrawn wording; supersedes the two statistics paragraphs above, which describe the original ten core risks):** 30 risks have a seed value. Raw RII: Kruskal-Wallis across the 30 not significant (p=0.077); R-WX lower than the rest only borderline (one-sided p=0.049) [WITHDRAWN, see 8.6]. Held-out agreement check, formerly called 'validation' (Spearman, full library): M10 rho 0.28 (19 risks, p=0.24), M15 rho 0.63 (11 risks, p=0.039, would not survive correction), M14 rho -0.18 (13 risks, p=0.55). Studies agree modestly [WITHDRAWN: Kendall W 0.40, p=0.16 is no evidence of agreement]: mean pairwise rho 0.33 over 16 pairs, Kendall W 0.40 (p=0.16); pooled-rank vs seed rho 0.73 [WITHDRAWN: circular, see 8.3]. Standardised (z-score) analysis: risks differ (two-way model p=0.002 for Analysis A, 0.008 for B), but only partly robust when single-study risks are removed (A p=0.015, B p=0.064); seed order vs pooled z order rho 0.40 (p=0.038) for A and 0.53 (p=0.004) for B [WITHDRAWN: circular, see 8.3]; 14 (A) and 13 (B) pooled risks rest on one study. Caveat: the library was extended after a first analysis on ten risks, so this is a second look, treat as exploratory. Documents regenerated: Statistical_Analysis.docx, Statistical_Analysis_Standardised.docx, Worked_Calculations.docx, Review_Preparation_Pack.docx. The Expert_Survey_Form.docx and Site_Data_Collection_Form.docx still list the ten core risks on purpose (a 38-item survey is too long).

**Other features:**
- Evidence browser: about 5,214 OpenAlex literature records + curated notes, searchable.
- AI risk suggestions (Gemini or Anthropic API key in Settings), guarded: cites evidence, never gives numbers.
- Source auto-selection: typing a number into an empty source field sets the Source to "User Input" (never auto-sets "Literature").
- Exports: `report.html` (printable, colour matrix + register; print to PDF), `matrix.png`, `matrix.svg`, `register.md` (colour squares), `register.csv`, case JSON.
- UI styled after thedesignshop.studio (ink/paper, square corners, custom cursor, hover animations). Matrix colours: Low green #4fcf6f, Moderate yellow #ffd93d, High orange #ff9626, Extreme red #ff4b4b.

**Built-in example case (ILLUSTRATIVE numbers, not evidence)** (this paragraph lists 5 risks; the example has 7, see section 8.8)**:** planned 16 working days; R-MAT p 0.50, R-LAB 0.35, R-RWK 0.25, R-WX 0.20, R-PLAN 0.10; impact edges 0.02/0.05/0.10/0.20. Result: R-MAT High (p3 × i5), R-LAB/R-RWK/R-WX Moderate (p2 × i4), R-PLAN Low.

**Run it:** `python -m gui` (opens on port 8765) · tests: `python -m pytest` (133 passing (superseded, see section 8; 137 passed, 3 skipped on 2026-10-08) · CLI: `python -m app.cli template | example | run case.json --out folder`.

## 5. Literature and data

- **Corpus (superseded, see section 8; the three corpus sizes conflict, see 8.9):** OpenAlex harvest of 21,902 records, filtered to **5,214 construction-relevant records** (`data/openalex_corpus.jsonl`). The filter is a keyword rule, so a little noise remains. The removed records and the 6,237 bulk PDFs (11 GB) were moved to a backup folder outside the project (reversible).
- **Curated:** 45 hand-picked PDFs (`Research_Papers/1-5`), research notes (`Research_Notes/*.md`), ranking workbook `Research_Papers_Ranking.xlsx`.
- **Key studies (IDs used in the tool):**
  - **M01** India building-construction labour-productivity survey (N=44; the field case study was AAC block walls; the wording 'brick-wall site survey' is superseded, see section 8): unsafe conditions 0.809, poor planning 0.791, unrealistic scheduling 0.791, material shortages 0.777, payment delay 0.773, work at height 0.764.
  - **A02** Ponmalar et al. 2018, Chennai residential (IJETMR): lack of experience 0.787, absenteeism 0.751, accidents 0.650, lack of material 0.780, lack of tools 0.760, payment delays 0.7758, weather 0.700. Also a real masonry record: 20-day masonry activity, 6–8% work-hour overrun. (Low-tier journal; use with care.)
  - **A14** Abeysinghe & Jayathilaka 2022, Sri Lanka (PLoS ONE, n=163): labour shortage 0.8245, material delivery delay 0.8098, material price 0.789, bad weather 0.6528.
  - **A15** Manoharan et al. 2022, Sri Lanka: skills shortage 0.82.
  - **Not used in the seed (hold-out):** A10 India infrastructure (late material delivery 0.652, material shortage 0.619, weather 0.616); A11 Soundarya et al. 2025 Chennai (importance index: rework 0.55, skilled labour 0.53, design 0.52, climatic 0.37); A21 Thailand (contractor finance 0.777, labour 0.733/0.773). Each overlaps only about 2 of our 10 risks (superseded, see section 8.10).
  - **A09** Guha & Biswas 2008, Kolkata: monsoon added about 5% to project duration and 12% to cost (Monte Carlo study).

## 6. Where we are now (continue from here)

**The problem:** the professor wants the **data analysis part** and "something concrete" by **Wednesday**. **We have no real site data** and cannot get it by then.

**Agreed plan (no fake data):**
1. **Secondary-data analysis (main analysis).** Build one table of RII values that 8–10 published studies give our 10 risks. Compute the combined ranking, agreement between studies (Kendall's W), and India vs other countries. Then **leave-one-study-out**: rebuild the ranking without study X and check whether it predicts study X's order (Spearman). This is the tool's out-of-sample test (superseded, see section 8.4: the computed leave-one-study-out figure is not a prediction test, and 'out-of-sample test' is withdrawn). **Status: a first version is done in `RII_Masonry_Literature.xlsx` (sheets Seed_Calculation and Validation, results in section 4). Adding more studies would strengthen it.**
2. **Sensitivity analysis.** Vary each risk's *p* and delay by ±20–50% and show which risks change matrix level. Needs no outside data.
3. **Quick expert survey (own primary data).** A Google Form asking engineers to rate how often (1–5) and how severe (1–5) each of the 10 risks is. Send to faculty, seniors in industry, contractors. Even 10–15 replies by Wednesday give our own ranking to compare with the literature and the tool. Keep it open to reach 30+.
4. **Roadmap slide.** Real-site validation is phase 2. The site data collection form is ready (`docs/Site_Data_Collection_Form.docx`: activity details, delay events with days lost, Y/N check of all 10 risks, starting site conditions). Target 3–5 completed masonry activities.

**What to tell the professor:** "With no site access yet, the tool is checked against published survey data and an expert survey; real-site validation is phase 2."

**Do not:** invent site numbers, or present RII values as probabilities.

**Later, with real site data, four comparisons:** (a) did the tool flag the risks that happened (hit rate), (b) does the matrix order match days lost (Spearman), (c) do probabilities match how often risks occurred (calibration, needs several activities), (d) only if Monte Carlo is added: did actual delay fall in the predicted P10–P90 range.

## 7. Open decisions / to-do

- Done: RII dataset + seed calculation + validation workbook (`RII_Masonry_Literature.xlsx`). Next: sensitivity analysis (item 2), the Google Form questions (item 3), a 2-page note for the professor.
- Monte Carlo "prediction" step: discussed (it would read the same *p* and delays, show P50/P90 and a tornado ranking, and skip seeded risks). The user said **not now**.
- Old unused code (simulation, cost, decision, productivity, old screens/tests) could be deleted; needs the user's decision.
- `docs/Project_Overview_Report.html` still describes the older, bigger app and is out of date.
- Fonts (Instrument Serif, Sora, Asta Sans) are not bundled; system fallbacks show.

---

## 8. Audit corrections (2026-10-08)

Added after an independent research-methods audit of the repository (findings F01 to F30, row-level checks of all 182 seed rows against the PDFs, and an engine audit). History above is kept; paragraphs that no longer hold are marked "(superseded, see section 8)". Every finding with its status is in `docs/Audit_Corrections_2026-10-08.md`. The audit confirmed that all 182 RII values and ranks in `data/literature_seed.json` match the printed papers; the problems are in metadata, notes, wording and statistics, not in the transcribed values. No `rii`, `rank`, `risk` or `mapping` value was changed.

### 8.1 Main limitation, stated first

An RII measures how important respondents rated a factor. It is not a probability of occurrence and not a number of days (integrity rule 4). The seed therefore supports at most an ordinal starting position for a risk. Placing a survey rank on the probability axis is an **Assumption** of this tool, not a finding from the literature.

### 8.2 Current seed table (30 seeded risks), recomputed from the code on 2026-10-08

Computed with `app.literature_seed.seed_table()` (basis "seed": five seed studies M01, A02, M06, A14, A15; Direct mappings only; each study's direct items averaged first, then studies averaged; ranks 1 to 30; five equal-count bands of six). This replaces the 10-risk Rank and Class columns in section 4, which are stale (for example R-SKILL is class 5 not 4, R-PLAN and R-PAY are class 5, R-LAB is rank 7 class 4, R-DES rank 10 class 4, R-WX rank 24 class 2). Mean RII values of the original ten risks did not change. Ties (R-MTH and R-STO, both 0.7000) are ordered alphabetically by the app.

| Risk | Library name | Seed mean RII | Rank | Class | Study means |
|---|---|---|---|---|---|
| R-MAT | Brick / block / mortar material shortage or late delivery | 0.7889 | 1 | 5 | A02 0.78, A14 0.8098, M01 0.777 |
| R-SAFE | Unsafe conditions or work at height | 0.7865 | 2 | 5 | M01 0.7865 |
| R-SKILL | Unskilled or unqualified labour | 0.7831 | 3 | 5 | A02 0.787, A15 0.8033, M01 0.759 |
| R-PLAN | Poor planning or unrealistic scheduling | 0.7771 | 4 | 5 | M01 0.791, M06 0.7632 |
| R-PAY | Payment delay | 0.7733 | 5 | 5 | A02 0.7758, M01 0.773, M06 0.7711 |
| R-DIS | Poor labour discipline or weak site leadership | 0.7700 | 6 | 5 | A15 0.79, M01 0.75 |
| R-LAB | Labour absenteeism or shortage | 0.7662 | 7 | 4 | A02 0.751, A14 0.8245, M01 0.723 |
| R-SCP | Unclear scope or inadequate project formulation | 0.7642 | 8 | 4 | M06 0.7642 |
| R-SITE | Poor site access, clearance or conditions | 0.7611 | 9 | 4 | A02 0.751, M06 0.7711 |
| R-DES | Design changes or incomplete documentation | 0.7585 | 10 | 4 | M01 0.732, M06 0.7851 |
| R-RWK | Rework due to workmanship or defects | 0.7561 | 11 | 4 | M01 0.736, M06 0.7761 |
| R-TOOL | Tools and equipment delay | 0.7528 | 12 | 4 | A02 0.76, M01 0.7455 |
| R-INC | Inadequate wages or incentives | 0.7520 | 13 | 3 | M01 0.752 |
| R-STR | Labour strikes or disputes | 0.7493 | 14 | 3 | M06 0.7493 |
| R-CTR | Contractual disputes and claims | 0.7468 | 15 | 3 | M06 0.7468 |
| R-SUP | Inadequate supervision or monitoring of workers | 0.7440 | 16 | 3 | M01 0.744 |
| R-MOT | Low motivation, morale or labour turnover | 0.7360 | 17 | 3 | M01 0.736 |
| R-MGT | Poor site management and coordination | 0.7331 | 18 | 3 | M01 0.709, M06 0.7572 |
| R-CST | Cost control and budget updating problems | 0.7184 | 19 | 2 | M06 0.7184 |
| R-OVT | Overtime and long working hours | 0.7063 | 20 | 2 | M01 0.725, M06 0.6876 |
| R-ACC | Accidents and injuries on site | 0.7045 | 21 | 2 | A02 0.65, M01 0.759 |
| R-MTH | Construction method or design complexity | 0.7000 | 22 | 2 | M01 0.7 |
| R-STO | Poor material storage or handling | 0.7000 | 23 | 2 | A02 0.7 |
| R-WX | Rain / monsoon stoppage | 0.6934 | 24 | 2 | A02 0.7, A14 0.6528, M01 0.764, M06 0.6567 |
| R-COM | Poor communication or misunderstanding on site | 0.6793 | 25 | 1 | A02 0.68, M06 0.6786 |
| R-PRC | Material price escalation | 0.6695 | 26 | 1 | A02 0.55, A14 0.789 |
| R-ECO | Economic conditions, inflation or interest rates | 0.6612 | 27 | 1 | M06 0.6612 |
| R-WAT | Water shortage | 0.6500 | 28 | 1 | A02 0.65 |
| R-FAT | Worker fatigue, age or personal problems | 0.6100 | 29 | 1 | A02 0.61 |
| R-SOC | Social or community environment | 0.5940 | 30 | 1 | M06 0.594 |

Not seeded (no direct RII in the five seed studies, so they stay off the matrix until numbers are entered): R-CLI, R-DEF, R-FIN, R-GOV, R-PRD, R-QLT, R-SUB, R-TRN. 14 of the 30 seeded risks rest on a single study.

How much weight the order can bear: the gap between rank 12 (R-TOOL 0.7528, class 4) and rank 13 (R-INC 0.7520, class 3) is 0.0008, while one respondent moving one Likert point changes an M01 RII (N = 44) by 0.0045, and the standard error of a single M01 RII is about 0.03 (the audit's estimate from M01's own counts). The top 6 span 0.019 and ranks 1 to 24 span 0.096. The bands are a display convention (equal-count bands force 6 risks into class 5 whatever the evidence), not a finding.

### 8.3 Circular agreement figures (F01), withdrawn as support

* "Pooled-rank vs seed rho 0.73" pools the seed studies (M01, A02, M06, A14) with the held-out studies and then correlates the pool with the seed. Using the held-out studies only, the pooled rank vs the seed is **rho 0.08 (n = 22, p = 0.73)**.
* "Seed order vs pooled z order rho 0.40 (Analysis A, p = 0.038) and 0.53 (Analysis B, p = 0.004)": Analysis A contains M06 and B contains M01 and M06, both seed studies. Using the held-out studies only (M10, M14, M15), the z-pooled order vs the seed is **rho 0.09 (n = 22, p = 0.70)**. M01 and M06 alone give 0.76, so the agreement comes from the overlap, not from independent evidence.
* Consequence: there is currently no independent evidence that the seed order is corroborated. If the team moves to a standardised pooled ranking, M10, M14 and M15 can no longer serve as a held-out check.

### 8.4 "Leave-one-study-out" is not prediction (F05)

The figure reported (rho 0.78 to 0.99) is the correlation of the ranking without study X with the FULL ranking, which shares four fifths of its data and is high by construction. The real cross-prediction (ranking from the other seed studies vs study X's own order) is: M01 rho 0.09 (n = 13, p = 0.76), A02 0.37 (n = 10, p = 0.29), M06 0.64 (n = 9, p = 0.061), A14 0.60 (n = 4), A15 untestable (n = 2). None is significant. The wording "predicts study X's order" and "the tool's out-of-sample test" is withdrawn.

### 8.5 Held-out agreement, multiple testing, Kendall W (F05, F10, F11)

* Three held-out surveys, 38-risk library: M10 rho 0.28 (19 risks, p = 0.24), M15 rho 0.63 (11 risks, p = 0.039 by the t-approximation; permutation p = 0.045), M14 rho -0.18 (13 risks, p = 0.55). With three tests, the Holm-adjusted p-values are about 0.117 (M15), 0.485 (M10) and 0.553 (M14) (Bonferroni for M15 also 0.117). **None survives correction.** The p-value method also changed between the two statistics paragraphs (permutation in the 10-risk text, t-approximation in the 38-risk text; M14's 10-risk p is printed as 0.09 and as 0.11): use the permutation/exact p throughout. Results moved when the risk set was redefined (M15 0.36 with n = 7 to 0.63 with n = 11), so the 38-risk run is exploratory.
* The word "validation" is withdrawn for this check; it is an agreement check with three surveys. A10, A21 and HAS25 overlap with too few risks to test; a note in the seed now records that A10 and A21 overlap with more risks than first stated, but those rows were not entered.
* Kendall W = 0.40 (chi-square 8.0, df 5, **p = 0.16**) over only 4 studies x 6 risks is **not evidence of agreement**. The mean pairwise rho 0.33 averages 16 overlapping, non-independent correlations, some with n = 4. The wording "studies agree modestly" is withdrawn; use "agreement between studies is weak and not distinguishable from chance".

### 8.6 Weather finding (F09), withdrawn

"R-WX is rated lower than the rest" (Kruskal-Wallis / Mann-Whitney, one-sided p = 0.049) was a hypothesis formed on the 10-risk data where R-WX was last. In the 30-risk set R-WX is rank 24 and six risks are lower, the test treats questionnaire items as independent (66 items from 5 studies), and at study level the Kruskal-Wallis p is 0.25. In the standardised analysis the interval for R-WX includes 0. The finding and the words "weather is rated lower" are withdrawn. "Risks differ (two-way p = 0.002 / 0.008)" is only partly robust: it is driven by single-study risks (with at least two studies per risk, A p = 0.015, B p = 0.064). Say instead: "some risks (for example social environment, training, client decisions) are rated clearly lower; the order of the rest is not resolved".

### 8.7 Assumptions that must be labelled (F02, F18)

* **Same band for both axes (Assumption).** The app uses one band as both the probability class and the impact class. Diagonal scores are 1, 4, 9, 16, 25, so with the thresholds Low <= 5, Moderate 6 to 10, High 11 to 15, Extreme >= 16, 12 of the 30 seeded risks are labelled Extreme, 6 Moderate, 12 Low and none High. Rank 12 (R-TOOL) is "Extreme" and rank 13 (R-INC, 0.0008 lower) "Moderate". The rank is effectively squared and given an absolute-sounding label. A seeded p class 5 means "top fifth of a survey importance list", whereas a quantified p class 5 means p > 0.8; the two are not commensurable. Whether to show seeded cells without level colours is a code/UI decision (see the corrections file).
* **A rule flag raises the probability class by 1 (Assumption).** No source supports the size of this step. This also means the statement "rules never produce probabilities" is no longer strictly true for seeded risks: a flag changes their probability class (capped at 5).
* The probability-class edges (0.2 / 0.4 / 0.6 / 0.8), the level thresholds and the equal-count bands are Assumptions (already stated for the first two).

### 8.8 Example case (F14)

The built-in ILLUSTRATIVE example has **7 risks**, not the 5 listed in section 4: it also contains R-SAFE (p 0.30) and R-SKILL (p 0.22). Result when run: R-MAT High (p3 x i5 = 15); R-LAB, R-RWK, R-WX, R-SAFE and R-SKILL Moderate (p2 x i4 = 8); R-PLAN Low (p1 x i3 = 3). The impact bin edges and delay ranges in the example have no individual Source/ILLUSTRATIVE label (needs an example change, see corrections file).

### 8.9 Corpus size: three versions, decision for supervisor (F08)

The documents quote three different corpus sizes. They are NOT reconciled here and none is chosen; this is marked **decision for supervisor** (re-run `scripts/corpus_statistics.py` against the actual database and keep one figure).

| Version | Harvested / input | Kept | Source file |
|---|---:|---:|---|
| 1 | 21,902 harvested | 5,214 construction-relevant | this file, section 5 (`data/openalex_corpus.jsonl`) |
| 2 | 17,788 harvested | 3,975 in the database | `docs/Literature_Database_Report.md` (`data/literature.db`, rules 2026-10-07.1) |
| 3 | 11,599 input | 3,550 included | `data/screening_report.json` (rules 2026-10-07.1) |

The statement in "Other features" that the evidence browser holds about 5,214 records is therefore unverified.

### 8.10 Data and metadata corrections in `data/literature_seed.json`

Only metadata and notes changed (study fields `authors`, `venue`, `context`, `masonry`, `location`, and appended `note` text; two `other_indices` notes). Highlights: M01 and A02 are general building-construction surveys and the field `masonry` no longer says "Yes" (the M01 field case was AAC blocks); M15 has the full six-author list and a recorded DOI inconsistency inside the PDF (e5194 in footers, e5120 in the how-to-cite box); M10's Man. 20 and Tec. 5 are not rows of Table 7; M14's printed RII equals W/(5N) although the paper states A = 4, so the values are not on the paper's own stated 1-4 basis; M06 n = 201 (abstract/Table 3) vs 206 in the Section 3.1 text; M01 "Bad leadership skill" printed sum/RII (165, 0.750) disagrees with its own counts (164, 0.745) and is kept as printed; A10 location is Table 2 pp.766-767, Table 3 p.767, text p.767 (weather 0.616 only in the text); A21 location is Table 6 p.16 and labour is 0.733 (0.773 only in the abstract). The seed is a **deliberate subset** of the papers: A14 has 5 of 39 factors entered (34 omitted, including Q11 financial difficulties of contractors 0.8233 rank 3, Q39 Covid-19 0.7902 rank 5, Q9 poor planning and scheduling 0.7890 rank 6, Q28 low productivity of labourers 0.7485 rank 11; 26.4% of A14's respondents were on road projects), A15 has 5 of 32, A02 14 of 35, and more of A10's and A21's items overlap with the tool risks than the old note said (about 10 for A10) but were not entered. M01 lists only factors with RII >= 0.700 (28 of 38), which biases risks whose M01 items were cut. A11 is kept out because it uses a different index (frequency x severity), not because the overlap is small. The claim that the library is "built from every factor in the 11 studies" is withdrawn.

### 8.11 Wording withdrawn or replaced

| Withdrawn wording | Why | Use instead |
|---|---|---|
| "validation", "Validation already done", "Held-out validation" | 0 of 3 tests significant after correction; M14 negative | "agreement check with three held-out surveys: weak and not significant" |
| "predicts study X's order", "the tool's out-of-sample test" | leave-one-study-out reported is not prediction; cross-prediction rho 0.09 to 0.64, none significant | "leave-one-study-out cross-prediction is weak" |
| "studies agree modestly" | Kendall W 0.40, p = 0.16 | "agreement between studies is weak and not distinguishable from chance" |
| "weather is rated lower" / "R-WX lower than the rest" | post-hoc, item-level, rank 24 of 30 | drop the claim |
| "pooled-rank vs seed rho 0.73"; "seed vs pooled z rho 0.40 / 0.53" | circular | held-out-only values 0.08 and 0.09, or drop |
| "built from every factor in the 11 studies" | A14 5 of 39, A15 5 of 32, A02 14 of 35 | "from the factors transcribed so far" |
| "every value with its table/page" | location is per study; 4 rows are unmapped/group-level | "182 rows (178 factor values), each with a study-level source location" |
| "M01 India brick-wall site survey" | the RII survey is general building construction; the field case was AAC blocks | "India building-construction labour-productivity survey (field case: AAC block walls)" |
| "predicts", "prediction" for the survey-based seed | RII is importance, not likelihood | "orders", "starting position" |

### 8.12 Suggested honest wording for the report

"The literature seed is a transparent, labelled default ordering of library risks by the mean relative importance index (RII) reported in five India and Sri Lanka surveys. RII is an importance rating, not a probability or a delay, so the placement is an ordinal starting point, and the band used for both matrix axes is an assumption of this tool. The surveys are general building-construction surveys, not masonry-specific. Differences between most risks are smaller than the sampling error of a single survey item (about +-0.06 for M01, N = 44), and the order is not stable: 14 of 30 risks rest on a single study, and leave-one-study-out cross-prediction is weak (rho 0.09 to 0.64). Agreement with three held-out surveys is weak and not significant after Holm correction (rho 0.28, 0.63 and -0.18). The seed is not validated and should be replaced by expert-survey and site data."

### 8.13 Open items

See `docs/Audit_Corrections_2026-10-08.md` for the full list. The items that need a decision or a code change and are not done here: the scope of the official project title (Monte Carlo/EMV) versus the current identification-register-matrix scope; the corpus-size figure (8.9); whether seeded cells keep level colours; whether to enter all 39 A14 rows and re-run the statistics; a second-coder check of the mappings; engine validation defects (NaN, bool, missing delay source, etc.); example-case labels.


### 8.14 Quantitative layer re-connected (2026-10-08)

At the team's request the cost / EMV and decision code is reachable again through `app/analysis.py` (`service.run_analysis`, CLI `analyze`, `POST /api/analyze`). It adds value at stake per risk, per-response break-even targets, a numberless catalogue of candidate responses (`data/mitigation_catalogue.json`, from `Research_Notes/D_mitigation.md` section 6), generated option sets, the AUTHORIZE MITIGATION / ACCEPT RISK / NO ADMISSIBLE OPTION / NO RESPONSE EVALUATED command, a seed-stability check and a cost-per-day sensitivity. Integrity rules are unchanged: no effect size, probability, delay or cost is supplied by the tool or the AI, and the wording never calls a result optimal. The register / matrix flow and its GUI are untouched; the cost, mitigation and decision screens are still not in the navigation. This extends the scope noted in 8.13 and is for the team to confirm with the guide. Tests: `tests/test_options.py`, `tests/test_analysis.py`.

## 9. Committee upgrades 2026-10-08

Implemented after the committee review (engineering/UX, domain expert, methods, examiner). No value in `data/literature_seed.json` changed (the SHA-256 of the `[study, factor, rii, rank]` rows is still `9fc2fe05...e78710`; guard test G-3 pins it). No number was invented, no probability, delay or cost comes from AI, and Monte Carlo/EMV stay out of scope.

**Final counts (read from data, pinned by `tests/test_relevance_guard.py`):** 46 library risks (30 with a literature seed value, 16 without, marked `seed_status`), 182 seed rows, 11 studies (5 seed, 6 held-out), 22 site-fact rules (was 11).

What changed:

1. The withdrawn sentence "No number here was produced by AI" was replaced in the Markdown and HTML exports by: "This tool does not generate probabilities, delays or costs. Each number shown was entered with the Source printed next to it. The AI suggestion feature can propose risk names, mechanisms and evidence IDs only; its numeric fields and any figures in its text are rejected (guard rules G2, G7, G9)."
2. `probability_class` uses the same 1e-9 relative edge tolerance as `impact_class`.
3. Source labels: optional case key `impact_bin_edges_source` (missing gives a warning and "Source: not given"); delay notes are kept on read; every export prints the impact edges with their Source and the default probability edges (0.2 / 0.4 / 0.6 / 0.8) and level thresholds (5 / 10 / 15) as Assumption; the example case is labelled ILLUSTRATIVE on edges and delays.
4. Rules: RL-MAT compares stock days with lead time (`le`, a tie fires); RL-MAT2, RL-WX, RL-FEST, RL-HEAT are `normal` (relevant only) with priority 0; RL-HGT also needs `scaffolding_ready == false`; new RL-WX2 (monsoon and external walls), RL-PACE (planned vs achieved daily output), RL-FRONT, RL-VT, RL-SCAF, RL-MORT, RL-GPAY, RL-OPEN, RL-FEST2. Rules that mix levels on one risk have different priorities (guard G-8). The fact `material_buffer_days` is retired. Eight new library risks (R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT) cite only evidence IDs that exist in the corpus; the masonry-specific form is labelled Expert Judgment, to be confirmed by the expert survey. They have no seed rows, so the 30 seeded risks and the five bands did not move.
5. Seeded cells (the smaller fallback): kept on the grid with their scores, but labelled "literature tier (Assumption)" in the GUI, register, matrix and every export, drawn as grey dashed chips, left out of the level totals (`summary.levels`, KPI strip), `level` empty in the CSV. The "+1 probability class for a rule flag" is labelled Assumption in every export. Probability class 1 is always Low: stated as an Assumption in the legend and exports, the two affected cells are marked, and a high-consequence list (impact class 5, entered numbers only) is a filter, not a score.
6. Register text fields (owner, early-warning trigger, response type avoid / reduce / transfer / accept, action, review date) in the case schema, CSV, Markdown, HTML and the risk card. Text only, no numbers.
7. GUI: Source badges visible on register cards and in the matrix table; chips no longer overlap the level label at 800 px; ILLUSTRATIVE banner on every screen; KPI strip separates entered numbers from literature tier; Source picker for the impact edges; rule table with Source column, no mid-word breaks and a neutral badge for `normal`; nav tooltip hidden after a click; toasts moved to the bottom left, narrower. Checked with screenshots at 1280 and 800 px (no horizontal page overflow, no console errors, no chip over a level label).
8. Withdrawn wording removed: `scripts/stats_tool.py` no longer says "held out for validation" (F23); the docstring of `literature_seed.py` is corrected (F22); `scripts/build_rii_workbook.py` no longer says "built from every factor".
9. `tests/test_relevance_guard.py`: guards G-1 to G-10 (counts from data, docs match data, seed checksums, withdrawn wording, Source on every exported number, legacy modules not imported, example stays ILLUSTRATIVE, rule-base sanity, unseeded risks labelled, no AI numbers path).

Deferred (needs a supervisor decision, not done): event / condition tag (`type`) on library risks; merging R-TRN into R-SKILL and R-OVT with R-FAT, removing R-PRD (they change seed mappings, `n_seeded` and every band); renaming library risks into site language and re-categorising R-SUP (wording is safe for the engine but changes texts); showing seeded risks with no colour at all and dropping the +1 step (option B of the engineering review); entering the omitted A14 rows (changes the seed); the expert survey and usability session; the sensitivity table of thresholds. Not done and still open: running the research-audit generators (`scripts/corpus_statistics.py`, `scripts/stats_corpus.py`) with corrected text (F19, F20), circular figures in the statistics scripts (F01, F21), the optional guard on `response_action` text.
