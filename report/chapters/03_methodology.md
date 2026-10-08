# Chapter 3. Methodology

This chapter states how the evidence was gathered and checked, how the literature seed and the risk matrix are defined, which statistics are used and why, how the software was verified, and what a future expert survey and second-coder check would involve. It describes what was done, not what was hoped for. No site data have been collected and no expert survey has been run; every analysis in Chapter 4 therefore uses published survey values (Literature) or an illustrative example case whose inputs are placeholders (Assumption). Chapter 4 reports the results; this chapter fixes the rules before they are applied.

## 3.1 Research design and scope

The work is a tool-development project with a secondary-data analysis attached to it. The tool is an offline register for delay risks in one activity, brick and block masonry. It supports risk identification from a library, a risk register, and an ordinal probability-impact matrix. The secondary-data analysis asks how much weight the published survey values can carry when they are used as the starting position of a risk on that matrix. The design follows the stages of the ISO 31000 risk-management process in a reduced form: identification (risk library and site-fact rules), analysis (ordinal classes and a score), evaluation (matrix levels) and recording (register and exports). The risk-matrix technique itself is one of the assessment techniques catalogued in IEC 31010. Communication, treatment and monitoring are outside what this project can evaluate without site users.

Five questions guide the analysis. They are questions about the order of risks and about the behaviour of the software's classification rule, not about delay in days or probability of occurrence.

1. How is a risk's seed class obtained from the survey values, and with which assumptions?
2. How much does a risk's class change when the banding rule, the data variant or the set of seed studies changes?
3. Which risks keep a high or low class under study resampling, and which cannot be assessed because they rest on one study?
4. Do the surveys agree with each other on the order of the risks they share, and by how much could a check of this kind detect agreement?
5. How does the matrix level of a risk with entered numbers react to its inputs and to the assumed edges and thresholds?

The design deliberately excludes four things. Monte Carlo schedule simulation, expected monetary value and the productivity models exist in the repository as optional or legacy code (the decision layer was re-connected on 2026-10-08 and uses only numbers the user enters). They are not analysed here because no input for them has a source: no delay distribution, cost or mitigation effect has been measured. A survey importance index is never converted into a probability or a number of days. The original project title promised labour-productivity and delay-risk prediction; Chapter 1 explains the scope revision, and nothing in this chapter or the next claims prediction.

## 3.2 The evidence corpus and the corpus count

Three documents in the repository give three different corpus sizes, and the repository also contains a fourth number, the count of curated evidence records that the application loads. The audit logged the conflict as finding F08 and left it as a decision for the supervisor (Audit Corrections, 2026-10-08, F08 and Section 5). This report does not reconcile the figures and does not choose one. Table 3.1 lists all four with their sources.

**Table 3.1.** Corpus and record counts found in the repository (Literature-search bookkeeping; n as stated per row; source labels: counts copied from the files named, not recomputed except the last row)

| Version | Harvested or input | Kept | Where it is stated |
|---|--:|--:|---|
| 1 | 21,902 harvested | 5,214 construction-relevant | `docs/Project_Handoff_Summary.md` Section 5 and 8.9 (`data/openalex_corpus.jsonl`, not in the repository) |
| 2 | 17,788 harvested | 3,975 in the database | `docs/Literature_Database_Report.md`, `docs/Corpus_Statistical_Analysis.md` (`data/literature.db`, not in the repository; screening rules 2026-10-07.1) |
| 3 | 11,599 input | 3,550 included | `data/screening_report.json` (screening rules 2026-10-07.1) |
| 4 | not applicable | 472 curated evidence records | Derived Calculation: `build_full_store()` in `app/ai_layer/corpus.py`, run on 2026-10-08 on this checkout; it reports "TOTAL: 472 evidence records" |

Source: the files named in the last column; row 4 re-run for this report. The same figure (472) was seen in the application's health check during the committee review.

Three points matter for how the corpus is used in this report.

First, the 472 records are not a screened search result. They are the records the application can retrieve: 48 from `Literature_Evidence_Package.xlsx`, records parsed from the research notes in `Research_Notes/`, benchmark and model registries, and 54 full-text review files. The OpenAlex bulk file (`data/openalex_corpus.jsonl`) and the screening database are excluded from version control by `.gitignore`, so a fresh clone loads 472 records and not thousands. The relationship between the 472 records and versions 1 to 3 has not been documented, and no relationship is assumed here.

Second, none of the three screening counts can be turned into a single PRISMA flow with confidence. Versions 2 and 3 carry the same rule version label (2026-10-07.1) but differ by 6,189 records in input and 425 in records kept, and no script output in the repository explains the difference. A PRISMA-style flow diagram would require re-running the harvest and screening scripts against one frozen input, which has not been done. The counts are therefore reported as a conflict and the corpus is treated as a source of background reading, not as the evidence base of any statistic in this report.

Third, the corpus statistics in `docs/Corpus_Statistical_Analysis.md` describe a database of N = 3,975 records (version 2) and use regular-expression matching on titles and abstracts. They show how many abstracts mention a term, not how many studies used a method, and the "sufficiency" bootstrap in that document is a subsample illustration of a census, not evidence that the corpus is large enough (audit correction, F19). Where Chapter 2 quotes those figures it must carry the same limit. The statistics that matter for this report are computed on a much smaller object: the 182 rows of `data/literature_seed.json`, described next.

## 3.3 Study selection for the RII data

The quantitative evidence is the relative importance index (RII) values that published surveys report for delay or productivity-loss factors. RII, as defined in these papers, is the sum of the respondents' ratings divided by the highest possible rating times the number of respondents:

$$\mathrm{RII} = \frac{\sum_{i=1}^{A} w_i n_i}{A \cdot N}$$

where $w_i$ is the rating weight, $n_i$ the number of respondents giving it, $A$ the highest weight and $N$ the number of respondents. It lies between $1/A$ and 1 and measures how important respondents rated a factor. It is not a probability of occurrence and not a number of days.

Eleven studies are in the dataset. The seed file records no formal inclusion criteria, so none is claimed. What the entries show is that each study reports RII (or an RII-like importance index on a stated scale) for factors that map to at least one library risk, and that the team had its full text or abstract; the PDF folders named in the file (`5_Masonry_Productivity_Delay`, `6_Ranking_Studies_OpenAccess`) are collections the team assembled, not the output of a systematic screen. Two further sources were recorded but not used: Soundarya et al. (2025), because it reports a frequency-times-severity index, not RII, and Karthik and Rao (2022 or 2019, the year differs between sources), for which only a factor-group average of 0.784 is available from the abstract and which may report the same survey as M01 (`other_indices` in the seed file).

Each study carries a role in the dataset: five are **seed** studies (M01, A02, M06, A14, A15) and six are **held-out** studies (M10, M15, M14, A10, A21, HAS25). The seed file stores the held-out role under the older label `validation`; this report uses "held-out" because the check is an agreement check, not a validation (Audit Corrections, F05). Seed studies are Indian or Sri Lankan surveys; held-out studies come from the Middle East (pooled), Brazil, Indonesia, India (infrastructure), Thailand and Iraq. Only seed studies feed the placement of a risk. Held-out studies are used only to compare orders.

The date at which these roles were assigned relative to the first agreement calculation is not recorded. The earliest committed version of the seed file (commit `ed97aab`, 2026-10-07) already contains the roles, but the handoff summary records agreement results on a ten-risk set dated 2026-10-06 and 2026-10-07, and the library was widened from 10 to 38 risks after that first look. The role assignment therefore cannot be shown to precede all analysis, and the agreement results in Chapter 4 are labelled exploratory for that reason. Table 3.2 lists the studies.

**Table 3.2.** The 11 studies in `data/literature_seed.json` (Literature; n = 11 studies, 182 rows)

| ID | Study (as recorded in the seed file) | Country | N respondents | Scale | Masonry-specific? | Role | Rows | Entered subset |
|---|---|---|---|---|---|---|--:|---|
| M01 | Karthik and Rao (2019a) | India (Telangana) | 44 | 1-5 | No (field case: AAC blocks) | seed | 28 | only factors with RII >= 0.700 are printed (28 of 38); truncated list |
| A02 | Ponmalar et al. (2018) | India (Chennai) | not reported | 1-4 | No | seed | 14 | 14 of 35 factors |
| M06 | Dixit et al. (2019) | India | 201 (206 in text) | 1-5 | No | seed | 40 | 40 table rows |
| A14 | Abeysinghe and Jayathilaka (2022) | Sri Lanka | 163 | 1-5 | No (26.4% of respondents on road projects) | seed | 5 | 5 of 39 factors |
| A15 | Manoharan et al. (2022) | Sri Lanka | 90 firms | not recorded | No | seed | 5 | 5 of 32 factors; two-decimal summary values |
| M10 | Adebowale and Agumba (2023) | Middle East, pooled | 10 studies | pooled RII | No | held-out | 33 | Table 7, 33 rows |
| M15 | Almeida et al. (2021) | Brazil | 47 | 1-4 | No | held-out | 24 | not stated |
| M14 | Loekito et al. (2026) | Indonesia | 83 (workers) | 1-4 stated; printed RII = W/(5N) | No | held-out | 23 | not stated |
| A10 | Pinky Devi and Sindhu (2025) | India (infrastructure) | 72 | 1-5 | No (roads, bridges) | held-out | 6 | subset; about 10 tool risks overlap |
| A21 | Ouansrimeang and Wisaeang (2024) | Thailand | 380 (30 projects) | 1-5 | No | held-out | 2 | subset; more items overlap |
| HAS25 | Hassoon et al. (2025) | Iraq | not recorded | not recorded | Yes (abstract only) | held-out | 2 | abstract |

Source: `data/literature_seed.json` (study fields, corrected 2026-10-08) and `docs/Audit_Corrections_2026-10-08.md`, Sections 3. Row counts: Derived Calculation from the file (n = 182). N for M06: 201 in the abstract and Table 3, 206 in Section 3.1 of the paper.

Three features of this table limit what the seed can mean. Only one study (HAS25) is masonry-specific, and it contributes two rows from an abstract. M01 and A02 are general building-construction surveys; masonry appears only in their field observations. Scales differ (1-4, 1-5, pooled, not recorded), and M14 prints RII as $W/(5N)$ although its text states $A = 4$, so its absolute RII level is not comparable with other studies. Ranks within M14 are unaffected.

## 3.4 Extraction and verification protocol

Each RII value was copied by the team from the published table into one row of the seed file with the fields study, factor, RII, printed rank, mapped risk and mapping strength (`direct`, `related` or none). The source location is recorded per study, not per row (for example "Table 3, p.61" for M01), so the claim that every value carries its table and page is withdrawn; the accurate statement is 182 rows (178 factor values mapped to a risk, four unmapped or group-level rows), each with a study-level source location (Audit Corrections, F25).

The audit then compared the rows with the papers. Its summary states that all 182 `rii` and `rank` values match the printed papers, that no seed row is absent from its paper, and that the 182 rows were identical before and after the audit's edits (only metadata and notes changed). A test, `test_g3_seed_rows_are_frozen`, pins a SHA-256 hash of the study, factor, RII and rank fields so that a later edit cannot change a value silently.

One discrepancy must be stated. The audit's description of its source list names eight studies for the row-level check against PDFs: M01, M06, A14, M10, M15, M14, A10 and A21. Those eight studies hold 161 of the 182 rows. The seed file records A02 (14 rows) and A15 (5 rows) as taken from research notes, with the PDF not in the project folder, and HAS25 (2 rows) as taken from an abstract. This report therefore treats 161 rows as checked against PDFs and 21 rows as checked only against notes or an abstract, until the audit's author confirms otherwise. A02 and A15 matter: A02 contributes 13 direct values to the seed and A15 four. Table 3.3 gives the position study by study.

**Table 3.3.** Provenance of the 182 seed rows (Derived Calculation from the seed file's `obtained` field; n = 182 rows)

| Provenance recorded in the seed file | Studies | Rows |
|---|---|--:|
| Read from the PDF | M01 (28), M06 (40), A14 (5), M10 (33), M15 (24), M14 (23), A10 (6), A21 (2) | 161 |
| From research notes (PDF not in project folder) | A02 (14), A15 (5) | 19 |
| From the abstract only | HAS25 (2) | 2 |

Known inconsistencies inside the papers were kept as printed and noted in the seed file. Examples: M01 "Bad leadership skill" prints a sum of 165 and RII 0.750, while the paper's own counts $[1,5,5,27,6]$ over $N = 44$ give $1\cdot1 + 2\cdot5 + 3\cdot5 + 4\cdot27 + 5\cdot6 = 164$ and $164/(5 \times 44) = 0.745$; M06 gives $N$ as 201 and 206 in different places; M15 prints two DOIs; M10's Table 7 has 33 rows and two further items appear only in text. None of these changes a seed value by more than 0.005 where it can be quantified. The values of A11 and of the group average P1-23 were not verified and are not used.

The seed file is a deliberate subset of its papers. A14 enters 5 of 39 factors, and the omitted ones include financial difficulties of contractors (RII 0.8233, rank 3) and Covid-19 (0.7902, rank 5); the audit estimated that adding the omitted A14 rows would move 14 of 35 classes. The statement that the library was "built from every factor in the 11 studies" is withdrawn; the accurate statement is "from the factors transcribed so far".

## 3.5 Mapping protocol

Each factor was assigned by the team to a library risk with a strength: `direct` (the factor is the risk or a clear synonym), `related` (an overlapping concept), or none (group-level or unmappable). The library holds 46 risks, of which 30 have at least one direct value in a seed study; 16 have none and stay off the matrix until numbers are entered (eight of the original 38 and the eight added on 2026-10-08). Only direct mappings from seed studies enter the seed: 66 values (M01 25, A02 13, M06 20, A14 4, A15 4), which combine into 30 per-risk means.

The mapping is one coder's judgment (Expert Judgment, single coder). The audit found inconsistent decisions, for example for "poor site management" in M10, "training" in M06, "age" in A02 and "changing jobs" in M14 (finding F12), and recommended a second-coder check before any mapping value changes. That check has not been run. Until it is, every statistic that depends on the mapping carries the label "single coder, agreement not measured". The planned protocol is in Section 3.10.

## 3.6 Seed construction

The procedure is the one implemented in `app/literature_seed.py`. Figure 3.1 summarises it and the following steps state it exactly.

![Figure 3.1. Steps from the 182 seed-file rows to a seed class (Derived Calculation; n = 30 seeded of 46 library risks; labels show the source label of each step).](figures/ch3_seed_construction_steps.png)

1. **Select rows.** Keep rows whose study has role seed and whose mapping is `direct` and which carry a risk id. This gives 66 rows.
2. **Average within a study.** For each risk and each seed study, take the arithmetic mean of that study's direct items. A study then counts once for the risk, however many of its items map to it (Assumption, AS-9 below).
3. **Average across studies.** The seed mean RII of a risk is the arithmetic mean of its study means, with equal weight for each study (Assumption, AS-8).
4. **Rank.** Order the 30 seeded risks by seed mean RII, highest first. Ties are broken by risk id in alphabetical order (Assumption, AS-12). Exactly one tie exists, R-MTH and R-STO at 0.7000.
5. **Band.** For rank $r$ among $n = 30$ risks the class is
$$ \text{class} = 5 - \left\lfloor \frac{(r-1)\cdot 5}{n} \right\rfloor $$
so ranks 1 to 6 are class 5, ranks 7 to 12 class 4, and so on down to class 1 (ranks 25 to 30): five equal-count bands of six (Assumption, AS-5). The number of bands, five, is chosen to match the five classes of the matrix axes.
6. **Place.** The class is used as both the probability class and the impact class of the matrix, because a survey importance index measures neither probability nor days (Assumption, AS-6). A rule flag marked "elevated" raises the probability class by one, capped at 5 (Assumption, AS-7). A seeded placement is an ordinal starting position. A user who enters both a probability and a delay for the risk replaces it.

Two worked examples follow. The first shows the RII definition applied to counts. The second applies steps 2 to 5 to one risk.

**Worked example 3.1: RII from counts (Literature counts, Derived Calculation).** M01 "Bad leadership skill": 44 respondents on a 1-5 scale with counts 1, 5, 5, 27 and 6 for ratings 1 to 5. The weighted sum is $1(1) + 2(5) + 3(5) + 4(27) + 5(6) = 164$, the maximum possible sum is $5 \times 44 = 220$, so RII $= 164/220 = 0.7455$. The paper prints 165 and 0.750; the seed uses the printed 0.750.

**Worked example 3.2: from RII to class for R-LAB (labour absenteeism or shortage).** Direct items: A02 "Absenteeism" 0.751; A14 "Shortage of labourers (skilled, semi-skilled, unskilled)" 0.8245; M01 "High workforce absenteeism" 0.723. Each study has one direct item, so the study means are 0.751, 0.8245 and 0.723. The seed mean RII is $(0.751 + 0.8245 + 0.723)/3 = 0.7662$ (code: 0.7662). In the order of 30 means, 6 risks have a higher mean, so the rank is 7. Then class $= 5 - \lfloor 6 \cdot 5 / 30 \rfloor = 5 - 1 = 4$. The code returns rank 7 and class 4. The same calculation for a risk with several items in one study, R-SUP in M01 (0.759, 0.759, 0.714), gives a study mean of $2.232/3 = 0.744$, which equals the value in the seed table. The check was run by `report/scripts/ch34_build.py`, which asserts both results against `seed_table()`.

## 3.7 Matrix definitions and thresholds

The matrix classifies each risk on two axes with five classes each and combines them into a level. The definitions, all from `app/engine/matrix.py`, are:

- **Probability class** from a probability $p$ with edges 0.2, 0.4, 0.6, 0.8: class = 1 + the number of edges that $p$ has reached. A value on an edge goes to the higher class (lower-edge-inclusive), with a relative tolerance of $10^{-9}$ so that binary rounding does not move a value that is meant to lie on an edge. The edges are equal-width bins (Assumption, AS-1).
- **Impact class** from the conditional expected delay divided by the planned activity duration, with four ascending edges entered by the user. The tool has no default, and the example case uses 0.02, 0.05, 0.10 and 0.20 (Assumption, ILLUSTRATIVE, AS-3). The same lower-edge-inclusive convention and tolerance apply (AS-4).
- **Score** is the product of the two classes.
- **Level** is Low for scores up to 5, Moderate for 6 to 10, High for 11 to 15 and Extreme for 16 and above (thresholds 5, 10, 15, Assumption, AS-2).

Table 3.4 and Figure 3.2 show the level of all 25 cells. The structure follows from the rule and is a property of the chosen scoring rule, not a finding about risk. Row 1 and column 1 are always Low, because the largest score on them is $1 \times 5 = 5$. High needs both classes of at least 3. The score is symmetric, so the rule treats probability and impact as interchangeable. Cox (2008) discusses these properties of multiplicative matrices (poor resolution and range compression), and Duijm (2015) gives recommendations for matrix design; the choices here follow neither as a standard, and the sensitivity analyses of Chapter 4 test how far the thresholds matter.

**Table 3.4.** Score and level of each cell of the 5x5 rule (Derived Calculation from `matrix_level`; n = 25 cells; L = Low, M = Moderate, H = High, E = Extreme)

|  | i class 1 | i class 2 | i class 3 | i class 4 | i class 5 |
|---|---|---|---|---|---|
| p class 5 | 5 L | 10 M | 15 H | 20 E | 25 E |
| p class 4 | 4 L | 8 M | 12 H | 16 E | 20 E |
| p class 3 | 3 L | 6 M | 9 M | 12 H | 15 H |
| p class 2 | 2 L | 4 L | 6 M | 8 M | 10 M |
| p class 1 | 1 L | 2 L | 3 L | 4 L | 5 L |

Source: `app.engine.matrix.matrix_level`, thresholds 5/10/15 (Assumption).

![Figure 3.2. Level map of the 5x5 scoring rule; the blue outline marks the cells a seeded risk can occupy (Derived Calculation; n = 25 cells; thresholds are an Assumption).](figures/ch3_level_map_5x5.png)

With the same class on both axes, a seeded risk can only land on the diagonal: scores 1, 4, 9, 16 and 25, hence levels Low, Low, Moderate, Extreme and Extreme. Six risks in each class give 12 Low, 6 Moderate, 0 High and 12 Extreme (counted in Chapter 4). The effect is that the rank is effectively squared and given an absolute-sounding label, which the audit raised as finding F02. The application now labels seeded placements as "literature tier (Assumption)", draws them as grey dashed chips and excludes them from the level totals; whether to hide the level colour entirely remains a supervisor decision.

### The Assumption register

The labels AS-1 to AS-16 are local to this chapter and Chapter 4; the full register in Appendix H uses its own numbering (AS-01 to AS-18), and the two are not the same list. Table 3.5 lists every assumption that changes a number in this report, where it is used, why it was made, and which analysis tests it. Items AS-1 to AS-7 define the tool; AS-8 to AS-13 define how literature values are combined; AS-14 to AS-16 concern the analysis itself.

**Table 3.5.** Assumption register (Source label of every row: Assumption)

| ID | Assumption | Where used | Reason | Tested by |
|---|---|---|---|---|
| AS-1 | Probability edges 0.2/0.4/0.6/0.8 (equal width) | probability class of risks with entered p | simplest neutral bins; no source | S2 (example case) |
| AS-2 | Level thresholds 5/10/15 on the product of classes | matrix level | no source | S2 (example), A1 extra (seeded, 969 triples) |
| AS-3 | Impact = expected delay / planned duration with four user-entered edges (example 0.02/0.05/0.10/0.20, ILLUSTRATIVE) | impact class of risks with entered delay | puts delay on a duration-relative scale | S2 |
| AS-4 | Lower-edge-inclusive classes, relative tolerance $10^{-9}$ | both class functions | removes float artefacts at an edge | S0 probes; S1 break-even (R-WX) |
| AS-5 | Five equal-count bands, six risks per band | seed class | five classes on the axes | S3 band variants |
| AS-6 | Same class on both axes | seeded placements | RII is neither probability nor days | structural analysis (Chapter 4); not testable with these data |
| AS-7 | A rule flag adds one probability class, cap 5 | seeded risks with an elevated rule | lets site facts move a seeded risk; no source for the step size | structural analysis (Chapter 4); not testable with these data |
| AS-8 | Each seed study has equal weight | seed mean RII | avoids weighting by N across unequal designs | S3 (study bootstrap, drop-one-study) |
| AS-9 | A study's direct items are averaged first | seed mean RII | one study counts once for a risk | not varied |
| AS-10 | Only `direct` mappings enter the seed | seed rows | `related` rows are weaker matches | S3 (direct + related) |
| AS-11 | Raw RII from 1-4 and 1-5 scales is averaged | seed mean RII | no common scale is available | S3 (rescaled; percentile rank) |
| AS-12 | Ties are ordered by risk id | rank | needs a deterministic rule | one tie (R-MTH, R-STO), reported |
| AS-13 | Seed and held-out roles as listed in the seed file | agreement analysis | see Section 3.3 | S4 (non-circular comparison) |
| AS-14 | Sensitivity ranges (x0.5 to x2, edge shifts, cut-off triples), the 80% tier rule, B = 2000, seed 20261008 | all of Chapter 4 | analysis design; fixed before reporting | all variants reported |
| AS-15 | Planning SD of one Likert point for survey precision | Section 3.10 | M01's counts give about 0.96 | not applicable (planning only) |
| AS-16 | Every probability, delay and the planned duration of the example case | S1, S2 | placeholders for a demonstration | S1, S2 |

## 3.8 Analysis plan

The committee's methods review fixed one family of analyses, A1 to A7, before the results of the final scripts were produced. The scripts are in `analysis/` (S0 to S5) and one further script, `report/scripts/ch34_build.py`, adds the structural counts of A1, the cut-off analysis for the seeded placements, the tier rule, the critical correlations and the worked-example checks. Table 3.6 maps the plan to the scripts.

**Table 3.6.** Analysis family A1 to A7 and where each is implemented (Source: methods plan of 2026-10-08 and `analysis/README.md`)

| ID | Question | Method | Implemented in | Input label |
|---|---|---|---|---|
| A1 | What does the 5x5 rule imply by itself? | enumerate 25 cells; count levels; apply to the seeded diagonal | `ch34_build.py`; S0 probes | Assumption |
| A2 | How does the level of a risk with entered numbers respond to its inputs? | one-at-a-time and joint scaling (x0.5, 0.8, 1.2, 1.5), 5x5 joint grid, 5000 random joint draws, break-even multipliers | S1 | Assumption (ILLUSTRATIVE) |
| A3 | How do edges and thresholds matter? | shift each probability edge, scale impact edges, alternative sets, 5000 random edge draws, cut-off triples | S2 (example); `ch34_build.py` (seeded: 969 triples) | Assumption |
| A4 | How stable are seed classes under banding and data variants? | 14 variants, drop-one-study, boundary gaps | S3 | Literature |
| A5 | Which risks keep a coarse tier under study resampling? | study-level bootstrap (2000), exact jackknife, tier rule | S3; tier rule in `ch34_build.py`; spread in S5 | Literature |
| A6 | Do studies agree on order, without circularity? | pairwise Spearman with n, permutation p, Holm; study vs seed from the other studies; Kendall W blocks | S4 | Literature |
| A7 | Are the RII values comparable across studies? | scale and selection checks reported as limits | S3 (rescaled, percentile, drop-one), S5; Table 3.2 | Literature |

**Statistics used.**

- *Spearman's rho* between two orders over the risks that both orders contain. Every correlation is reported with its n. A correlation with fewer than five shared risks is not tested.
- *Permutation p-values.* For n up to 8 the two-sided p is exact, by enumeration of all n! permutations. For larger n, 20,000 random permutations are drawn and p = (count + 1)/(20,000 + 1), where count is the number of permutations with $|\rho^*| \ge |\rho|$. Monte Carlo error is about $\pm 0.003$. Permutation tests are preferred to the t-approximation because n is small and the ranks contain ties.
- *Kendall's W* (Kendall & Babington Smith, 1939) for m studies ranking n risks that all of them contain, with a tie correction. The test statistic is $W = 12S/[m^2(n^3 - n) - m\sum T]$, where $S$ is the sum of squared deviations of the risk rank sums and $T$ the tie term. The p-value is a permutation p (20,000 permutations, one-sided, with the +1 correction), because the chi-square approximation is unreliable at n of 5 to 10. W measures consensus about order, not reliability.
- *Holm's step-down correction* (Holm, 1979) within each family of tests: the sorted p-values are multiplied by $k, k-1, \dots, 1$ and made monotone. Three separate families are used: the 13 pairwise correlations with n of at least 5; the leave-one-study-out comparisons; and the 14 Kendall W blocks. The W blocks share studies and risks, so their adjusted p-values are descriptive.
- *Study-level bootstrap.* The five seed studies are resampled with replacement 2000 times, a study drawn twice has weight 2, and the seed is rebuilt each time. A risk is absent from a resample if all its studies were left out; class shares are therefore conditional on presence, and the share of resamples in which a risk is present is reported. Bands are cut over the risks present in the resample. With five clusters a percentile bootstrap is crude, so the exact leave-one-study-out (jackknife) is reported beside it, and the bootstrap is descriptive.
- *Tier rule* (Assumption, AS-14). A risk is in Tier 1 if it is in class 5 in at least 80% of the resamples in which it is present and it rests on at least two seed studies; "Tier lower" is the same with classes 1 and 2; a risk that meets a threshold but rests on one study is flagged "not assessable"; all others are "unresolved".
- *Critical correlations.* For each n the smallest $|\rho|$ whose two-sided permutation p is at most 0.05, so that the reader knows what a check of that size could detect.

All random draws use one generator seed, `numpy.random.default_rng(20261008)`. All variants named in the plan are reported, whether or not they look favourable. Software: Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2 (versions read from the interpreter used for this report). The command `PYTHONPATH=/usr/local/lib/python3.13/dist-packages python analysis/run_all.py` clears `analysis/out/`, reruns S0 to S5 in about 32 seconds, asserts that every output carries the label "Derived Calculation" and an n, and writes a manifest of SHA-256 hashes. The command was run twice for this report and the two manifests were identical. Because `analysis/out/` is excluded from version control, the result could not be compared with an earlier run of the same files; the check that remains is the identical second run and agreement with the figures of the committee plan where those are quoted.

**What was and was not pre-specified.** The family was written down in the committee plan on 2026-10-08, after the ten-risk analyses and after the library was widened to 38 risks. It is therefore a specification made after the data were known, not a pre-registration. Its protection against forking paths is that the variants are enumerated, none is dropped and every one is reported. The 38-risk run is a second look at data first examined on 10 risks and is exploratory.

**Excluded on purpose.** The earlier scripts computed a number of statistics that this report does not repeat: item-level Kruskal-Wallis and Mann-Whitney tests (pseudo-replication and post hoc), any pooled order that contains the seed studies compared with the seed (circular), "mean pairwise rho" as an agreement statistic, a two-way model whose headline p depends on single-study risks, and any conversion of RII into a probability. The audit's findings F01, F05, F09 and F10 list them.

## 3.9 Software verification method

Verification asks whether the software does what its specification says. Validation would ask whether its output helps a site manager or matches site reality, and no validation has been done. The verification used four methods.

1. **Automated tests.** The pytest suite covers the engine, matrix, rules, service, exports, AI guard and the optional analysis layer. On 2026-10-08, with the command `python -m pytest -q`, it reported 513 passed and 3 skipped in about 29 seconds; the three skips need the screening database, which is not in the repository. This count is reported as read at that time, not as a fixed property: other counts (46 library risks, 30 seeded, 182 seed rows, 11 studies, 5 seed studies, 22 site-fact rules) are pinned through `tests/test_relevance_guard.py`, which reads each count from the data files and fails when a document or data file changes without a conscious update.
2. **Guard tests.** Ten guards G-1 to G-10 check that counts agree across data and documents, that the seed rows are frozen (a hash), that withdrawn wording is absent from current documents, that every exported number has a source, that the example stays labelled ILLUSTRATIVE, and that unseeded risks carry a status and no seed rows and the AI path carries no numbers.
3. **Hand calculation against the tool.** Chapter 6 compares hand calculations with tool output for a worked case. Within this report, Worked examples 3.2 and 4.1 recompute a seed class and a matrix placement by hand and compare them with the code's output.
4. **Cross-implementation checks inside the analysis package.** S3 re-implements the RII-to-class rule and asserts equality with `seed_table()` for all 30 seeded risks. S1 and S2 use a faster path through the matrix functions and assert equality with `run_case` on all 84 one-at-a-time runs, on 100 random draws, on the baseline and on every impact-edge variant. No mismatch occurred (`fast_path_vs_run_case_mismatches` is 0).

S0 probes small behaviours of the repository code. Results relevant here: `run_case` does not expose the probability edges (classification uses the default edges, although a docstring suggests otherwise), so S2 varies them through the matrix functions and asserts agreement at the defaults; the example case's R-WX, with p = 0.20, lies exactly on the first probability edge; and switching the seed basis to "all" (held-out studies and related mappings pooled) changes the class of 24 of the 30 common risks. The S0 output also stores a finding text about a missing probability tolerance, which is stale: the tolerance was added after the committee review (Audit Corrections, Section 6), and the probe's recorded class for 0.1 + 0.7 is 5, as the tolerant rule expects.

Engine defects found by the audit (H1, M1 to M10, L1 to L14) were partly fixed on 2026-10-08. Those still open are listed in the audit and in Chapter 6; NaN and boolean inputs are now rejected by the case validator. None of them affects the seed or the analyses reported here.

## 3.10 Future expert survey and second-coder design

Neither of the following has been done. They are described so that the analysis can be pre-registered before any data arrive.

### 3.10.1 Expert survey

The design is a short questionnaire of 15 neutral-worded causes of masonry delay (for example bricks or blocks not on site, masons absent, hoist unavailable, rain stopping external masonry), each rated for **frequency** (1 never or almost never to 5 on almost every masonry activity) and for **severity** (1 no noticeable slip to 5 holds up following trades), with "not applicable" and "don't know" options. The anchor wording is the team's own (Assumption) and is never converted to days or probability. Item order is randomised, the literature ranks and the tool's matrix are not shown, one attention-check item is included, team members do not respond, and a three-cause ranking question gives a check independent of the rating scales. The respondent profile records role, years of masonry supervision, building types, unit types, region and employer type, without names. A pilot with two or three site engineers tests wording.

*Pre-registration.* A dated file in the repository, written before data arrive, will fix the items, the item-to-library mapping, the exclusion rules (failed attention check, under one year of masonry supervision), the handling of N/A (pairwise, never imputed) and the analysis list below.

*Analysis list.*

- Per item: n answering, median, IQR, frequency index (FI) and severity index (SI) by the RII formula, importance FI x SI, with a respondent-bootstrap 95% interval (B = 5000), and ranks with bootstrap rank intervals.
- Kendall's W across respondents on complete cases, separately for frequency and severity, and by group (contractor-side, client or consultant side) when a group has at least 8 respondents.
- Reliability of the item order, not only Cronbach's alpha (Cronbach, 1951): random split-half of respondents, Spearman of the two halves' FI orders corrected by the Spearman-Brown formula, averaged over 1000 splits; alpha is reported for convention only, because the 15 causes are a checklist and not one reflective construct.
- Group differences per item by Mann-Whitney with Holm over 15 items and a rank-biserial effect size, only if each group has at least 10 respondents.
- Comparison with the seed by Spearman rho on the items that have a pre-registered one-to-one mapping (about 10 expected), exact p; labelled "agreement check, exploratory".

*Precision and sample size.* The sample will be purposive or snowball, so no population margin of error is claimed. With a planning SD of one Likert point (Assumption; M01's counts give about 0.96), the standard error of one item's index is about $\mathrm{SD}/(5\sqrt{n})$: Table 3.7 gives the values and the half-width of a 95% interval. The gaps between neighbouring seed risks are 0.001 to 0.02, so an expert sample of 10 to 15 is a pilot and cannot resolve order inside a band. A target of at least 30, with response rate and respondent profile reported, is stated in advance. With n = 10 shared items, the smallest $|\rho|$ that would reach p of 0.05 is 0.648 (Table 3.8), so the detectable agreement is stated before the survey, not after.

**Table 3.7.** Planning precision of one importance index (Derived Calculation from the Assumption SD = 1 Likert point; formula $\mathrm{SE} = \mathrm{SD}/(5\sqrt{n})$)

| n respondents | SE of one index | Half-width of 95% interval (1.96 x SE) |
|--:|--:|--:|
| 15 | 0.052 | 0.101 |
| 30 | 0.037 | 0.072 |
| 44 (M01's N) | 0.030 | 0.059 |

**Table 3.8.** Smallest absolute Spearman correlation reaching two-sided permutation p <= 0.05 (Derived Calculation; exact for n up to 9, 200,000 random permutations with seed 20261008 above that; n = number of shared items or risks)

| n shared risks | Smallest absolute rho with two-sided permutation p <= 0.05 |
|--:|--:|
| 5 | 1.000 |
| 6 | 0.886 |
| 7 | 0.786 |
| 8 | 0.738 |
| 9 | 0.700 |
| 10 | 0.648 |
| 11 | 0.618 |
| 13 | 0.566 |
| 15 | 0.521 |
| 19 | 0.460 |

Source: `report/scripts/ch34_build.py`. Values are discrete for small n; n = 5 admits only a perfect rank agreement.

Frequency answers and the optional "out of the last 10 activities" counts will not be converted into probabilities in the analysis. They can be entered later, risk by risk, as Expert Judgment with n stated.

### 3.10.2 Second-coder protocol for the mapping

1. Freeze a coding manual first: the risk definitions (name, scope, inclusion and exclusion examples), the decision rule for direct, related and none, and a rule for "unmappable".
2. The second coder is a person who did not build the mapping (a team member who did not code, or a faculty member). The coder is blind to the first coder's assignments and to the RII and rank columns; only the factor text and study context are exported.
3. Calibrate on 15 to 20 rows from a study that is not in the agreement sample (for example A10 or A21 items not yet entered), discuss, amend the manual once and freeze it.
4. Code all 178 mapped factor rows and any newly entered rows.
5. Statistics: Cohen's kappa (Cohen, 1960) for risk assignment across the library categories plus none, with percent agreement and a bootstrap 95% interval over rows; linearly weighted kappa for strength (direct, related, none); and the same for the subset that feeds the seed (seed studies, direct). Report prevalence. Landis and Koch (1977) descriptors are used only as labels.
6. Pre-committed rule: kappa below 0.60 means revise the manual and recode a fresh sample; otherwise resolve disagreements by discussion and log every change (row, old, new, reason).
7. Re-run A4 to A6 once on the reconciled mapping and report original and reconciled results side by side.

## 3.11 Ethics

No human participants have been involved in the work reported here. All data are published survey values, and the example case is made up. The planned expert survey will involve adults who volunteer information about their own professional experience. Before it starts, the team will: obtain whatever institutional approval or exemption NICMAR requires for a questionnaire study (the requirement has not been confirmed with the supervisor and no approval number exists); show an information sheet stating purpose, voluntary participation, the right to stop, the anonymity of responses and the uses of the data; obtain informed consent as the first item of the form; collect no names, employer names or contact details in the response file (invitations are sent separately); store the response file on institutional or team-controlled storage and share only aggregated results; and report n, response rate and respondent profile truthfully. A site data collection phase would need a separate approval and the consent of the site owner. The AI evidence layer of the tool is not used to produce numbers.

## 3.12 Threats to validity

Table 3.9 collects the threats by type, with what has been done and what remains open. Chapter 7 returns to them.

**Table 3.9.** Threats to validity (Assumption and Literature labels as in the text)

| Type | Threat | Handling in this report | Status |
|---|---|---|---|
| Construct | RII measures importance, not likelihood or days; the same band is used on both matrix axes; multiplicative matrices compress range (Cox, 2008) | seed labelled ordinal and Assumption; A1 and S2 show what the rule implies; no RII-to-probability conversion | open by design |
| Internal | One coder for the mapping | kappa protocol designed | open |
| Internal | Analysis choices after seeing the ten-risk data; many variants | one enumerated family, all reported, 38-risk run called exploratory | mitigated, not removed |
| Internal | M01 prints only RII >= 0.70; A14 and A15 give top factors only; selection on outcome pulls these risks up | dropping A14 and A15 together is one variant in S3 | reported |
| Internal | Mixed scales, M14 printed basis, A15 scale not recorded | rescaling and percentile-rank variants | reported |
| Statistical conclusion | 5 seed studies; 14 of 30 seeded risks rest on one study; overlaps of 1 to 19 risks give low power; multiple testing | exact or permutation p, Holm, n for every statistic, critical rho | reported |
| Statistical conclusion | Intervals ignore mapping and scale uncertainty, so they understate it | stated with each interval | open |
| External | General building surveys, not masonry-specific; two Sri Lankan studies; road projects in A14; manager-dominated respondents; dated surveys | study table and limits stated | open |
| Reliability of the tool | Engine defects (NaN, booleans, edge rounding) | partly fixed, tests, S0 probes | partly open (NaN, booleans, edge rounding fixed) |
| Ecological | No site data; example is ILLUSTRATIVE; no user evaluation | no claim of accuracy on real sites | open |
| Corpus | Three corpus counts and a fourth record count unreconciled | reported, not resolved | open (supervisor decision) |

## 3.13 Integrity rules and source labels

Every number in this report has a source label: **Literature** (as printed in a published study), **Expert Judgment** (the team's single-coder mapping, and, in future, survey ratings with n), **Derived Calculation** (computed from inputs of the other kinds, which are named; a value derived from Assumption inputs inherits the label ILLUSTRATIVE) and **Assumption** (a choice made by the team and listed in Table 3.5). Historical Data and User Input do not occur in this report, because no site data or user entries exist. Tables and figures of Chapter 4 carry the label and the n in their captions. RII is described as importance and never as probability or days; the seed as an ordinal starting position; the held-out comparison as an agreement check that is weak, low-powered and inconclusive. The wording withdrawn in the audit (Handoff Section 8.11) is not used.
