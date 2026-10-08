# Chapter 7. Discussion

This chapter says what the results of Chapters 4 to 6 mean, how far they can be pushed, how the tool compares with the other ways a site engineer could keep a masonry risk register, and what could make the conclusions wrong. It repeats results only where the argument needs them. All numbers carry a Source label; those labelled Derived Calculation come from `analysis/out/` or from the scripts in `report/scripts/`, and those labelled Literature are values printed in the surveys.

## What was found, and how strongly

Four findings carry the report. Table 7.1 states each with the evidence behind it and the strength with which it can be said.

**Table 7.1.** Principal findings and the strength of the evidence. Source: Chapters 4 to 6; `analysis/out/` (Derived Calculation); `docs/Audit_Corrections_2026-10-08.md`; Appendix E.

| Finding | Evidence | Strength |
|---|---|---|
| The 182 transcribed RII values and ranks match the printed papers; errors found were in metadata and notes | Row-by-row check against the PDFs on 2026-10-08, listed in the audit file | Strong for the rows entered. The values of A11 and P1-23 were not re-checked, and the seed is a subset of the factors printed in several papers (A14 5 of 39, A15 5 of 32, A02 14 of 35) |
| Published RII rankings agree only weakly with one another on the risks they share | Held-out comparison: M10 rho 0.28 (n = 19), M15 0.63 (n = 11), M14 -0.18 (n = 13). Leave-one-study-out cross-prediction among seed studies: M01 0.09 (n = 13), A02 0.37 (n = 10), M06 0.64 (n = 9). Kendall's W 0.40, permutation p = 0.15 (4 studies, 6 risks) | Weak, low-powered and inconclusive: no comparison is significant after correction, and the overlaps are small enough that only large correlations could be detected |
| The class a seeded risk receives depends on banding and study choices; the level a risk receives from entered numbers depends more on probability class and thresholds than on the delay range | Seed variants: 6.7% to 80.0% of the 30 classes change across the pre-specified variants; example: no delay multiplier from 0.5 to 1.5 changes any of 7 levels, whereas halving every probability changes 6 of 7 (analyses S3 and S1) | Descriptive of the rules; says nothing about real risks, because the example inputs are placeholders |
| The software does what the documents say | 513 tests passed, 3 skipped, 0 failed (Appendix E); worked example in Chapter 6 | Verification only. Not validation, and not a guarantee for the defects still listed as open in the audit file |

What was not found matters as much. No site data were collected, no expert was asked, and no user has been observed using the tool. The report therefore contains no evidence that the tool improves a decision, that its levels correspond to delay on a real site, or that a site engineer finds it usable. These are the open questions that Chapter 8 turns into future work.

## Reading the weak agreement between surveys

The agreement analysis was built to ask how far the literature can stand in for project data. The honest answer is that it cannot be said, and the reasons deserve to be separated, because they lead to different remedies.

**Real heterogeneity.** The surveys differ in country, in the kind of project, in who answered and in what was asked. Two are Sri Lankan, one pools ten Middle Eastern studies, one is Brazilian, one Indonesian. M14 is the only held-out study to correlate negatively with the seed (rho -0.18), and its authors split respondents into managers and workers; why the order differs is a hypothesis that this project cannot test. If the surveys really rank risks differently because the sites differ, then a pooled ordering describes no particular site, and the case for replacing it with local data is stronger.

**Sampling noise.** The RII of one item carries sampling error. For M01 (N = 44) an interval of about plus or minus 0.06 around a single RII is reasonable (Derived Calculation, `docs/Project_Handoff_Summary.md` section 8.12), while neighbouring seed risks differ by far less: the top six risks lie within 0.019 of each other, the top 24 within 0.096, and ranks 12 and 13 (R-TOOL and R-INC) differ by 0.0008 (Derived Calculation, audit file F30 and F02). The order of most risks is therefore not resolved by the data, and the sampling error would produce disagreement between surveys even if the true order were identical.

**Different things being rated.** An RII measures how important respondents rated a factor on a Likert scale. One survey may ask about causes of delay, another about causes of lost labour productivity (M01, A02, M06, A15 and M14 are productivity surveys; A14, A10, A21 and M15 are about delay). The same word, for example "material shortage", can then carry different weight in the two lists. Mixing 1 to 4 and 1 to 5 scales also moves values, though rescaling changed only 2 of 30 seeded classes (6.7%, analysis S3), so scale mixing is the smallest of these concerns.

**Selection of what is printed.** M01 prints only factors with RII of 0.700 or more (28 of 38). A14 and A15 are represented by their top factors (5 of 39 and 5 of 32 entered). A risk whose only evidence comes from a top-factors list is pulled upwards by construction. Dropping A14 changes 6.7% of the classes and dropping A15 10.0% (analysis S3), which is small, but A02 is influential: dropping it changes 13 of the 27 classes of the risks that remain (48.1%).

**Low power.** With few shared risks, only a large correlation can be distinguished from chance. Figure 7.1 shows the smallest correlation that would be two-sided significant at 5% for each overlap (Derived Calculation, `report/scripts/critical_rho.py`: 0.62 at n = 11, 0.56 at n = 13, 0.46 at n = 19) together with the observed values. M15's rho of 0.63 at n = 11 sits just beyond the line (raw permutation p = 0.045), while the others lie well inside. After Holm correction over the three held-out comparisons (Holm, 1979), the adjusted p-values are 0.13 (M15), 0.48 (M10) and 0.55 (M14); over all six testable leave-one-study-out comparisons of analysis S4 the adjusted value for M15 is 0.27. None is significant. A non-significant result with this power is not evidence of disagreement either: it leaves the question open.

![Figure 7.1. Smallest absolute Spearman correlation that could be called significant (two-sided, 5%) at each overlap of shared risks, with the observed leave-one-study-out correlations. Derived Calculation from `analysis/out/s4_leave_one_study_out.csv` and `report/scripts/out/critical_rho.csv`.](figures/fig7_1_detectable_rho.png)

Taken together, the results support a narrow statement: the literature gives a coarse order, with a few risks (material availability, skilled labour) near the top in several lists and a few (social environment, training, client decisions) clearly lower, but it does not give a stable ranking of the middle. The bootstrap over the five seed studies agrees: three risks reach the top band in at least 80% of the 2,000 resamples (R-MAT, R-SAFE and R-SKILL), and R-SAFE rests on a single study (Derived Calculation, analysis S3). Resamples that omit a study drop its risks, so these shares are conditional on the risk being present. This is the reason the tool shows seeded risks as a labelled, uncounted "literature tier" and asks for entered numbers, instead of treating the seed as an estimate.

The disagreement also has a use. Because the surveys do not converge, the report can offer a methods point that does not depend on any site: rankings of delay factors from a handful of South Asian RII surveys are not stable enough to be copied into a risk register as if they were probabilities. This is a modest, checkable observation and the one the audit trail best supports.

## What the matrix level means

The tool multiplies a probability class by an impact class and labels the product Low, Moderate, High or Extreme. This is a conventional device and it has known weaknesses. Cox (2008) lists poor resolution, errors in ranking, suboptimal resource allocation and ambiguous inputs and outputs as problems of risk matrices, and Duijm (2015) gives recommendations on their design; both are cited here for the general critique, and only the abstract of Cox was read in this project. Three of those concerns are visible in the tool.

First, **resolution is coarse**. Only five classes per axis exist, so risks with quite different entered numbers share a cell. In the ILLUSTRATIVE example, five of seven risks share the cell probability class 2 by impact class 4 (Chapter 6), although their probabilities range from 0.20 to 0.35 and their expected delays from 2.3 to 2.7 days.

Second, **the score is symmetric and class 1 on either axis always gives Low**. A risk with a probability below 0.2 is Low whatever its consequence, since 1 x 5 = 5. The tool prints this as an Assumption and also lists impact-class-5 risks separately, as a filter and not a score, so that a rare but severe risk is not lost.

Third, **the result depends on the edges**. In the example, replacing the probability edges with alternative sets changes between 2 and 7 of the 7 levels, and changing the level thresholds over 2,024 admissible triples changes a median of 5 of 7 (IQR 1 to 6; analysis S2). By contrast, scaling the impact edges between 0.5 and 2 changes the impact class of between 1 and 7 of the 7 risks but never a level, because the probability class caps the score. Two things follow. The level is less sensitive to the entered delay than a reader might expect; and the one number that moves the example most is a probability sitting exactly on an edge (R-WX, p = 0.20, which the tool places in class 2 under its lower-edge-inclusive convention). A reader should therefore treat the level as a prompt for discussion, and the probability class edges and thresholds as parameters that deserve a stated reason, which for this tool is that they are Assumptions (Appendix H).

For risks that carry only a literature tier, the weakness is larger. Using one band as both axes squares the rank (diagonal scores 1, 4, 9, 16 and 25), so a risk at the top fifth of an importance list scores 25. That is not a statement about probability or impact, and the earlier version of the tool coloured such placements Extreme, High or Low as if it were. After the committee review these placements are grey, dashed and excluded from the level totals. The more conservative option, removing level colours and the one-class step for rule flags altogether, remains a decision for the supervisor (audit file, F02).

## Comparison with other ways of keeping a register

Three alternatives are realistic for a site engineer: a spreadsheet register, a schedule-risk package used by the planning office, and no formal register. The comparison below is limited to what could be established without testing commercial products. The project did not install or evaluate Primavera Risk Analysis or any other package, and the account of schedule-risk software rests on how it is described in the case studies of the corpus: Gheewala et al. (2025) used Primavera P6 with Risk Analyzer and Ichsan et al. (2025) used @RISK, in both cases on project schedules with distributions supplied by the study team. Anything not stated in those papers or visible in the repository is marked "not assessed".

**Table 7.2.** Features of the tool compared with a spreadsheet register and with schedule-risk software as used in two cited case studies. Source: tool column from the repository (`README.md`, `docs/case_schema.md`, Appendices B to D); software column from Gheewala et al. (2025) and Ichsan et al. (2025) as summarised in Chapter 2; spreadsheet column describes what a plain sheet is, not any particular template. No commercial product was tested.

| Capability | This tool | Spreadsheet register | Schedule-risk software (as used in the cited studies) |
|---|---|---|---|
| Masonry-specific risk library with evidence IDs | Yes: 46 risks, 30 with a survey seed value, 16 without | Only if the author builds one | Not assessed; the studies built their risk lists from surveys or focus groups |
| Source label required on every number | Yes: six labels; a number without one is rejected | Only if the author adds a column and keeps it | Not reported in the papers read |
| Site facts flag risks | Yes: 22 rules, Source Assumption, no numbers | Possible with formulas written by the author | Not assessed |
| Probability-impact matrix | Yes, with edges and thresholds printed as Assumptions | Possible; edges are whatever the author chose | Not assessed |
| Schedule simulation | Optional layer, entered numbers only, no defaults | Not in a plain sheet | Yes in both studies; distributions and probabilities supplied by the user (Chapter 2) |
| Whole-project schedule network | No: one activity | No | Yes: project-level in both studies |
| Works offline on one computer | Yes (local server or desktop window) | Yes | Not assessed |
| Evidence of use on real projects | None: verified by tests only; no user evaluation | Not assessed | Published case studies exist (two cited) |

The differences are practical, not methodological. This tool contains no calculation that a competent engineer could not build in a spreadsheet, and it does not contain the project-level scheduling that the packages offer. What it adds is a particular discipline: a referenced list of masonry risks to start from, a prompt from site conditions, and an output that cannot show a number without its source. Whether that discipline helps a site engineer is not known. The closest published prior art for the optional quantitative layer is activity-level residual-risk simulation after mitigation (Ichsan et al., 2025, who took response effects from a five-person focus group); the response types in the register follow the avoid, reduce, transfer, accept classification used in the risk-response literature (Dey, 2011; Baker et al., 1999). No claim of novelty is made for any of these mechanics.

## Implications for site engineers

The findings have practical consequences even though the tool has not been evaluated with users.

**Use the library and the rules as a checklist, not as a forecast.** The 46 risks and the rule prompts are the part most likely to help. A flag such as "stock on site runs out before a new delivery can arrive" asks a question the engineer can answer in a minute. It costs nothing to check and it is derived from facts the engineer entered. The flag says that the condition holds, not that a delay will follow.

**Enter your own numbers, and say where they come from.** A literature tier is a starting point for a conversation about which risks to look at first. As soon as the engineer has an estimate of a probability and a delay range, the estimate replaces the tier and carries its own Source label. An estimate from the engineer's own experience is Expert Judgment; a count from the site diary is Historical Data. Both are better than a survey rank, and both are visible as such in the register and its exports.

**Do not read the level as a measurement.** The example shows that the level can change when a probability moves across an edge, and that the delay range has little influence on it. The ordering inside a level is not meaningful. A high-consequence risk of low probability appears in the separate impact-class-5 list for that reason.

**Use the response fields.** The register asks for an owner, an early-warning sign, a response type and a review date. These are text fields and carry no numbers, and they are what turns a ranked list into something a site team can act on. Several of the committee's recommendations concerned exactly these fields, and the report treats them as at least as valuable as the matrix.

**Treat the optional cost layer with caution.** It compares responses using the engineer's own costs and effects. If those effects are guesses, the output is a guess presented with a command word. The wording "preferred under the stated criterion" is deliberate, and a stability check across random seeds is built in, but neither guards against poor inputs.

**Time and effort were not measured.** The tool needs entry of facts and numbers for each activity. How long this takes, and whether a busy engineer would do it daily, is a question for the pilot in Chapter 8.

## Threats to validity

**Table 7.3.** Threats to validity, their likely effect and what has been done or remains to do. Source: methods review of 2026-10-08, audit file, and the authors' assessment.

| Type | Threat | Likely effect | Done so far | Still needed |
|---|---|---|---|---|
| Construct | An RII is importance, not likelihood or days; the seed puts one band on both axes | A seeded placement has no quantitative meaning | Labelled Assumption everywhere; shown as an uncounted, grey literature tier; wording "starting position" | Expert likelihood and impact ratings on separate axes |
| Construct | Multiplicative matrix compresses range and depends on edges | Levels differ under other edges or thresholds | Edges and thresholds printed as Assumptions; sensitivity reported (analyses S1, S2) | Practitioner view on edges; option of dropping level colours for seeded risks |
| Internal | Single coder for the factor-to-risk mapping; some decisions inconsistent (F12) | The seed depends on one person's judgment | Mapping rule documented; Direct versus Related distinguished | Second coder and Cohen's kappa (Appendix G) |
| Internal | Analysis choices made after seeing the 10-risk data; the 38-risk run was a second look | Forking paths | One pre-specified family of variants; all variants reported | Re-run once on a reconciled mapping with the plan fixed in advance |
| Statistical conclusion | Five seed studies; 14 of 30 seeded risks rest on one; overlaps of 5 to 19 risks | Low power; unstable ranks; intervals understate uncertainty | Exact or permutation p-values; Holm correction; power shown (Figure 7.1) | More studies; complete the omitted A14, A10 and A21 factors and re-run once |
| Statistical conclusion | Surveys are not independent (M10 pools ten studies); M14 printed RII on a basis that differs from its stated scale | Agreement may be over- or understated | Noted; values kept as printed | Recompute M14 on its stated basis if the supervisor agrees |
| External | General building-construction surveys, two from Sri Lanka, one road-heavy (A14 26.4% road respondents), manager-dominated | Seed may not describe Indian masonry | Stated in every table note | Masonry-specific expert survey |
| Reliability of the tool | Defects listed in the engine audit (for example NaN accepted by the command-line writer, booleans accepted as numbers) | Wrong output on malformed input | Several fixed and tested after the review; 513 tests pass | Close the remaining items before any release |
| Ecological | No site data; example is ILLUSTRATIVE; no user evaluation | No evidence that levels match what happens on site | Claims limited accordingly | Site pilot and usability sessions (Chapter 8) |
| Corpus | Three corpus sizes appear in the project records (F08) | Reported search coverage uncertain | The three versions are listed with their source files in the audit file | Re-run the corpus statistics once against the database and keep one figure |

One threat deserves a sentence of its own. The report was written after the tool, and several of its checks, such as the audit of the seed, the held-out comparison and the guard tests, were produced by reviewers who were asked to find faults. That is a strength for integrity and a weakness for independence: the same team that built the tool prepared the corrections. An outside reader should treat the audit trail as evidence of care, not as an independent evaluation.

## What can and cannot be claimed

**Table 7.4.** Claims, whether the evidence supports them, and the wording to use. Source: `docs/Project_Handoff_Summary.md` section 8.11 and 8.12 (withdrawn and replacement wording), extended by this report.

| Claim | Supported? | Wording to use |
|---|---|---|
| The tool predicts delay or labour productivity | No | "orders risks"; "starting position" |
| The literature seed has been validated | No | "agreement check with held-out surveys: weak, low-powered and inconclusive" |
| Published rankings agree | Not shown | "weak agreement, not distinguishable from chance" |
| The seed values are probabilities | No | "an importance rank used as an ordinal tier, an Assumption" |
| Every number in an export has a source | Yes, by design and by test G-5 | "each number is printed with its Source" |
| The AI supplies no numbers | By design and guard; fixed after the audit | "the AI can propose names, mechanisms and evidence IDs only; numeric fields are rejected" |
| The tool is accurate on real sites | No evidence | not claimed |
| The tool is useful to site engineers | Not evaluated | "intended to help; to be evaluated" |
| A first or new framework | Not claimed | "an evidence-traceable tool; no new method" |
| Published agreement shows masonry-specific importance | No; surveys are general | "general building-construction surveys" |

The conclusion of this chapter is that the project delivers a transparent, offline, verified tool and an honest account of how little published rankings can carry, and that it stops short of everything that would need data from people or from sites.
