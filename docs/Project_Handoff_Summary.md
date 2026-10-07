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
| Risk identification | Literature review + checklist + rule-based checks on site conditions + expert input | Risk library (10 risks), 11 site-fact rules, evidence-cited AI suggestions |
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

**Core risk library (10 risks; the library now has 38, see the expansion note below):**
R-MAT material shortage / late delivery · R-TOOL tools & equipment delay · R-LAB labour absenteeism/shortage · R-SKILL unskilled labour · R-PLAN poor planning / unrealistic schedule · R-SAFE unsafe conditions / work at height · R-WX rain/monsoon stoppage · R-RWK rework · R-PAY payment delay · R-DES design changes / incomplete drawings.

**Rule engine (11 rules, each flags a risk as "elevated"):**
required_workers > available_workers → R-LAB · material_lead_time_days > material_buffer_days → R-MAT · material_stock_days < planned_duration_days → R-MAT · tools_shortage → R-TOOL · monsoon_overlap → R-WX · work_at_height → R-SAFE · payment_delay_expected → R-PAY · design_incomplete → R-DES · prior_rework_history → R-RWK · schedule_compressed → R-PLAN · skilled_masons_short → R-SKILL.
Flagged risks are **auto-added** to the register (with empty numbers).

**Matrix logic:**
- Probability class from *p* with equal-width edges 0.2 / 0.4 / 0.6 / 0.8 (an Assumption).
- Impact class = expected delay ÷ planned duration, binned by four user-entered "impact bin edges" (e.g. 0.02 / 0.05 / 0.10 / 0.20). These edges are hidden behind a three-dots button on the matrix screen.
- Score = p class × impact class; Low if score ≤ 5, Moderate 6–10, High 11–15, Extreme ≥ 16 (thresholds are Assumptions).
- Ordinal prioritisation only, not a quantity.

**Literature seed (revised 2026-10-05):** library risks with **no numbers entered** are still placed on the matrix from survey RII values. Data: `data/literature_seed.json` (182 RII values from 11 studies, every value with its table/page), also exported as **`RII_Masonry_Literature.xlsx`** (built by `scripts/build_rii_workbook.py`; the app and the workbook read the same file).
- **Seed studies** (India/Sri Lanka): M01 Karthik & Rao 2019 (India, masonry, N=44), A02 Ponmalar 2018 (Chennai, masonry), M06 Dixit 2019 (India, N=201), A14 Abeysinghe 2022 (Sri Lanka, N=163), A15 Manoharan 2022 (Sri Lanka).
- **Method:** map each factor to a tool risk (Direct / Related; only Direct used) → average each study's direct items → average across studies = seed mean RII → rank → five equal bands of two → class used for BOTH axes → a rule flag raises the p class by 1 → entered numbers replace the seed. Seeded cells: dashed outline, "literature seed".

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

Spread: nine of the ten risks lie within 0.036 of each other (only R-WX is clearly lower), so the middle of the order is fragile.

**Validation already done (Spearman rank correlation with held-out studies the model does not use):** M10 Middle East meta-analysis of 10 surveys: rho = 0.40 (n = 9, p = 0.29), weak agreement. M15 Brazil managers: rho = 0.36 (n = 7, p = 0.43), weak agreement. M14 Indonesia **workers**: rho = −0.68 (n = 7, p = 0.09), moderate disagreement. None significant at 5%. Reading: manager-side surveys weakly agree with the seed; workers rank pay, tools and weather higher. A10, A21, Hassoon 2025 overlap with fewer than 4 risks, so they were not tested.

**Statistical analysis (2026-10-06; `scripts/stats_rii.py`, `docs/Statistical_Analysis.docx`, `docs/rii_statistics.json`):** Kruskal-Wallis across the 10 risks is not significant (H=14.2, p=0.115; without R-WX p=0.35), but R-WX is rated lower than the rest (Mann-Whitney p=0.005). Leave-one-study-out: rho about 0.88 or higher, except dropping M01 (0.72). Bootstrap rank intervals are wide (e.g. R-LAB 2 to 10). Agreement with held-out studies (Spearman, permutation p): M10 0.40 (p=0.30), M15 0.36 (p=0.44), M14 -0.68 (p=0.11); none significant. The studies disagree with each other: mean pairwise rho 0.10 over 13 pairs, Kendall W = 0.16 (p=0.63). Reading: only 'weather is rated lower' is statistically supported; the order of the other nine risks is not.

**Standardised analysis (2026-10-07; `scripts/stats_standardised.py`, `docs/Statistical_Analysis_Standardised.docx`, Standardised sheet in the workbook):** studies put on one level with within-study z-scores (raw RII differs by rating scale: study means 0.59 to 0.75). Only studies with complete factor lists are standardised: Analysis A = M06, M10, M14, M15; Analysis B adds M01 (truncated list, flagged). A, B: no significant difference between risks (two-way model p = 0.23 and 0.49). Pooled order A: rework, design, payment, unskilled labour, planning, material, tools, weather, labour, safety. Seed order vs pooled z order: rho -0.13 (A) and 0.16 (B), unrelated. The earlier 'weather lower' finding weakens (CI includes 0). Decision pending with the supervisor: keep the seed as a weak labelled starting order (current) or move to a standardised pooled ranking. The app was NOT changed.

**Risk library expanded (2026-10-07):** the library is no longer limited to 10 risks. It now has **38 risks in 11 categories** (Labour 11, Management 6, Material 5, Financial 3, Design 3, External 3, Safety 2, Quality 2, Equipment 1, Site 1, Weather 1), built from every factor in the 11 studies (`data/risk_library_masonry.json`; each factor in `data/literature_seed.json` now maps to a risk, only 4 unclear/group-level factors stay unmapped). Each risk carries a `scope` (activity or project-level) and the paper values behind it. The original 10 risks keep their IDs and mean RII. The seed bands are now cut over the 30 risks that have a seed-study value (6 per band); 8 library risks (R-TRN, R-PRD, R-SUB, R-CLI, R-QLT, R-DEF, R-GOV, R-FIN) have no seed value and stay off the matrix until numbers are entered. UI: the Library tab is grouped by category, filterable, with Add all buttons (numbers stay empty). The earlier worked-calculation and statistics documents describe the original core ten risks; banding the core ten over 30 risks changes their class (e.g. R-PLAN and R-PAY are now class 5, weather class 2). With the larger set the workbook's validation shows M15 rho 0.63 (n=11, p=0.039), M10 0.28 (n=19, p=0.24), M14 -0.18 (n=13, p=0.55): the result depends on which risks are compared; one p below 0.05 out of three tests is not robust to correction.

**Statistics re-run on the 38-risk library (2026-10-07; supersedes the two statistics paragraphs above, which describe the original ten core risks):** 30 risks have a seed value. Raw RII: Kruskal-Wallis across the 30 not significant (p=0.077); R-WX lower than the rest only borderline (one-sided p=0.049). Held-out validation (Spearman, full library): M10 rho 0.28 (19 risks, p=0.24), M15 rho 0.63 (11 risks, p=0.039, would not survive correction), M14 rho -0.18 (13 risks, p=0.55). Studies agree modestly: mean pairwise rho 0.33 over 16 pairs, Kendall W 0.40 (p=0.16); pooled-rank vs seed rho 0.73. Standardised (z-score) analysis: risks differ (two-way model p=0.002 for Analysis A, 0.008 for B), but only partly robust when single-study risks are removed (A p=0.015, B p=0.064); seed order vs pooled z order rho 0.40 (p=0.038) for A and 0.53 (p=0.004) for B; 14 (A) and 13 (B) pooled risks rest on one study. Caveat: the library was extended after a first analysis on ten risks, so this is a second look, treat as exploratory. Documents regenerated: Statistical_Analysis.docx, Statistical_Analysis_Standardised.docx, Worked_Calculations.docx, Review_Preparation_Pack.docx. The Expert_Survey_Form.docx and Site_Data_Collection_Form.docx still list the ten core risks on purpose (a 38-item survey is too long).

**Other features:**
- Evidence browser: about 5,214 OpenAlex literature records + curated notes, searchable.
- AI risk suggestions (Gemini or Anthropic API key in Settings), guarded: cites evidence, never gives numbers.
- Source auto-selection: typing a number into an empty source field sets the Source to "User Input" (never auto-sets "Literature").
- Exports: `report.html` (printable, colour matrix + register; print to PDF), `matrix.png`, `matrix.svg`, `register.md` (colour squares), `register.csv`, case JSON.
- UI styled after thedesignshop.studio (ink/paper, square corners, custom cursor, hover animations). Matrix colours: Low green #4fcf6f, Moderate yellow #ffd93d, High orange #ff9626, Extreme red #ff4b4b.

**Built-in example case (ILLUSTRATIVE numbers, not evidence):** planned 16 working days; R-MAT p 0.50, R-LAB 0.35, R-RWK 0.25, R-WX 0.20, R-PLAN 0.10; impact edges 0.02/0.05/0.10/0.20. Result: R-MAT High (p3 × i5), R-LAB/R-RWK/R-WX Moderate (p2 × i4), R-PLAN Low.

**Run it:** `python -m gui` (opens on port 8765) · tests: `python -m pytest` (133 passing) · CLI: `python -m app.cli template | example | run case.json --out folder`.

## 5. Literature and data

- **Corpus:** OpenAlex harvest of 21,902 records, filtered to **5,214 construction-relevant records** (`data/openalex_corpus.jsonl`). The filter is a keyword rule, so a little noise remains. The removed records and the 6,237 bulk PDFs (11 GB) were moved to a backup folder outside the project (reversible).
- **Curated:** 45 hand-picked PDFs (`Research_Papers/1-5`), research notes (`Research_Notes/*.md`), ranking workbook `Research_Papers_Ranking.xlsx`.
- **Key studies (IDs used in the tool):**
  - **M01** India brick-wall site survey: unsafe conditions 0.809, poor planning 0.791, unrealistic scheduling 0.791, material shortages 0.777, payment delay 0.773, work at height 0.764.
  - **A02** Ponmalar et al. 2018, Chennai residential (IJETMR): lack of experience 0.787, absenteeism 0.751, accidents 0.650, lack of material 0.780, lack of tools 0.760, payment delays 0.7758, weather 0.700. Also a real masonry record: 20-day masonry activity, 6–8% work-hour overrun. (Low-tier journal; use with care.)
  - **A14** Abeysinghe & Jayathilaka 2022, Sri Lanka (PLoS ONE, n=163): labour shortage 0.8245, material delivery delay 0.8098, material price 0.789, bad weather 0.6528.
  - **A15** Manoharan et al. 2022, Sri Lanka: skills shortage 0.82.
  - **Not used in the seed (hold-out):** A10 India infrastructure (late material delivery 0.652, material shortage 0.619, weather 0.616); A11 Soundarya et al. 2025 Chennai (importance index: rework 0.55, skilled labour 0.53, design 0.52, climatic 0.37); A21 Thailand (contractor finance 0.777, labour 0.733/0.773). Each overlaps only about 2 of our 10 risks.
  - **A09** Guha & Biswas 2008, Kolkata: monsoon added about 5% to project duration and 12% to cost (Monte Carlo study).

## 6. Where we are now (continue from here)

**The problem:** the professor wants the **data analysis part** and "something concrete" by **Wednesday**. **We have no real site data** and cannot get it by then.

**Agreed plan (no fake data):**
1. **Secondary-data analysis (main analysis).** Build one table of RII values that 8–10 published studies give our 10 risks. Compute the combined ranking, agreement between studies (Kendall's W), and India vs other countries. Then **leave-one-study-out**: rebuild the ranking without study X and check whether it predicts study X's order (Spearman). This is the tool's out-of-sample test. **Status: a first version is done in `RII_Masonry_Literature.xlsx` (sheets Seed_Calculation and Validation, results in section 4). Adding more studies would strengthen it.**
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
