# Chapter 8. Conclusions, Limitations and Future Work

## Conclusions

The project set out to build and verify an offline tool that helps a site engineer identify, register and prioritise delay risks in a brick or block masonry activity, with every value traceable to its source and with published survey evidence used only as a labelled ordinal starting point. Table 8.1 states what was concluded for each objective of Chapter 1, and how far.

**Table 8.1.** Conclusions mapped to the objectives. Source: Chapters 3 to 7; `docs/Audit_Corrections_2026-10-08.md`; Appendix E (Derived Calculation and Literature, as labelled in those chapters).

| Objective | Conclusion | How far it goes |
|---|---|---|
| 1. Compile and verify a masonry delay-risk library with a documented, inter-coder-checked mapping | A library of 46 risks (38 original, 8 added on 2026-10-08) was built, 30 of them with a survey seed value and 16 without. 182 RII rows from 11 studies (5 seed, 6 held-out) were transcribed; every value and rank matches the printed papers. The mapping rule and its Direct / Related distinction are documented | **Partly met.** One coder made all mappings, and some decisions are inconsistent (audit finding F12). The second-coder check and kappa have not been done (Appendix G). The seed is a subset of the printed factors (A14 5 of 39, A15 5 of 32, A02 14 of 35), and the surveys are general building-construction surveys, not masonry surveys |
| 2. Implement site-condition rules, a source-labelled register and a 5 x 5 matrix with assumptions stated | 22 site-fact rules, a register in which each number carries one of six Source labels (and in which text fields record owner, early-warning sign, response type, action and review date), a 5 x 5 matrix, and exports (Markdown, CSV, HTML, SVG, case file) were implemented. The assumptions that shape the output (equal-count bands, one band on both axes, probability edges, level thresholds, the one-class step for a rule flag) are listed in Appendix H and printed on every export | **Met as software.** The rule conditions and the matrix edges are Assumptions that no practitioner has yet endorsed |
| 3. Analyse how consistent published RII rankings are, to establish how far literature can stand in for project data | Agreement between surveys is weak and not distinguishable from chance: held-out correlations 0.28, 0.63 and -0.18 on 19, 11 and 13 shared risks, none significant after Holm correction; leave-one-study-out cross-prediction 0.09 to 0.64; Kendall's W 0.40 (permutation p = 0.15). Band and study choices change 6.7% to 80.0% of seeded classes. Only a coarse order can be read from the literature | **Met, with a negative result.** The check is low-powered, so it cannot show that surveys disagree either. It supports the limited use of the seed as a starting position |
| 4. Verify the software and evaluate it with practitioners; define site validation as future work | The suite passes 513 tests (3 skipped because the literature database is not in the repository) in 17 files; a worked example is given in Chapter 6. Site validation is defined below | **Verification met; evaluation not done.** No expert rating, usability session or site case exists |

Four general conclusions follow.

1. **The most defensible contribution is the traceability.** Every number in a register carries a Source, every assumption is named, and the claims that the audit withdrew are recorded with the reason. A reader can see which numbers are evidence and which are placeholders.
2. **A survey importance index cannot stand in for a probability.** The seed is an ordinal starting position and nothing more. The weak agreement among surveys shows that even the order of the middle of the list is not settled by the data in hand.
3. **The matrix is a prompt for discussion.** Its levels depend on edges and thresholds that are Assumptions and, in the example, depend more on the probability class than on the delay entered. It helps a team look at the same list of risks at the same time; it does not measure them.
4. **The registered title promised more than was done.** Productivity prediction, a rules matrix giving probability and cost, and the financial decision command were not built as described, because no site data existed to feed them. Chapter 1 gives the term-by-term account. The optional quantitative layer added on 2026-10-08 runs only on numbers the user enters and has been verified only as software.

## Limitations

The limitations that bear on every result are these.

- **No primary data.** No site was visited, no site record collected, and no practitioner consulted. No number in this report is Historical Data, and no number is an expert rating.
- **The seed is secondary and indirect.** The RII surveys are general building-construction surveys from India and Sri Lanka (plus held-out studies from other countries); none is masonry-specific. The transcribed factors are a subset. M01 prints only RII of 0.700 or more. Scales differ between studies and the scale of two is not recorded. Fourteen of the 30 seeded risks rest on one study.
- **One coder.** The factor-to-risk mapping has no second coder and no agreement statistic.
- **The agreement check is low-powered.** With 5 to 19 shared risks only a correlation of about 0.5 to 0.9 could be detected (Figure 7.1). The analysis was first run on a 10-risk set and then on the 38-risk library, so the second run is a second look, and the library has since grown to 46 risks, the 8 new ones having no survey rows.
- **Assumptions drive the placement.** Equal-count bands, one band on both axes, equal study weights, averaging within a study first, and alphabetical tie-breaking are choices of the team (Appendix H).
- **The tool has not been used by anyone but its authors.** Usability, time to complete a case and acceptability are unknown. The Anthropic path of the optional AI feature was never run against the live service; the Google path was.
- **Open defects.** The engine audit lists defects that were fixed and tested after the committee review, and others that still need a code change (Audit Corrections, sections 4 and 6; for example NaN in the command-line JSON writer and booleans accepted as numbers). The corpus-size figure has three versions that are not reconciled (F08). Legacy productivity code with a known norms defect remains in the repository, unused.
- **The registered title has not been changed.** The decision belongs to the project guide.

## Recommendations

**For a site engineer who wants to try the tool.** Use it on one masonry activity at a time. Start with the site facts and the rule prompts; treat the literature tier as a list of things to think about, not as a ranking of danger; replace it with your own estimates as soon as you have them, with the right Source label; fill in owner, early-warning sign and review date; and keep the exported register with its stated assumptions. Do not use the optional cost layer to justify spending unless the costs and effects entered have a source you can show.

**For the project guide (decisions recorded as open).** (i) Retitle the work to match what was done, or keep the registered title with the scope-revision table of Chapter 1. (ii) Decide whether to drop the one-class step for rule flags and to show seeded risks with no level colour (F02, F18). (iii) Decide whether to enter the omitted A14, A10 and A21 factors and re-run the statistics once, with the analysis plan fixed in advance (F03); the basis of the seed must not be chosen by which agreement figure looks better. (iv) Decide how to treat the truncated M01 list (F13) and whether to recompute M14 on its stated basis. (v) Approve the second-coder check before any mapping is changed (F12). (vi) Reconcile the corpus count with one re-run (F08).

**For the maintainers of the code.** Close the open items of the engine audit that touch integrity (NaN, booleans, missing delay Source, malformed input shapes); move the unused productivity, norms and legacy simulation modules to a folder marked as legacy so that no reader mistakes them for the deliverable; and keep the guard tests of Appendix E, which tie the counts and the wording rules in the documents to the data files.

## Future work

The next steps are ordered by how much each adds for the effort. The first three need no site access.

### 1. Expert survey

Administer the 15-item instrument of Appendix F (frequency and severity rated separately, with N/A and Don't know, neutral wording, randomised order, profile questions) to practitioners who have supervised masonry, with the analysis plan dated before the first reply. The target is at least 30 respondents, because 10 to 15 would be a pilot: with a planning standard deviation of one Likert point (Assumption AS-18) the half-width of one item's index is about 0.10 at n = 15 and 0.07 at n = 30, while neighbouring seed risks differ by 0.001 to 0.02. Results would be labelled Expert Judgment with n, response rate and respondent profile, never converted to probabilities or days, and compared with the seed by Spearman correlation on the items with a one-to-one mapping, as an exploratory check with the detectable correlation stated in advance. The same survey can ask respondents to endorse the rule conditions and to name causes the library lacks. Institutional ethics approval and consent text must be settled first; neither has been sought.

### 2. Second coder

Carry out the protocol of Appendix G: freeze the coding manual, have a coder who did not build the mapping code the blinded rows, compute Cohen's kappa for the risk assignment and a weighted kappa for the strength, apply the pre-committed rule that kappa below 0.60 triggers a revision of the manual (Cohen, 1960; Landis & Koch, 1977), log every change, and re-run the seed table and the statistics once, reporting the original and reconciled results side by side.

### 3. Face validity and usability session

Ask 5 to 8 site engineers to complete a case on the example activity and then on one of their own, observe where they hesitate, and collect a standard usability questionnaire such as the System Usability Scale (Brooke, 1996). Report the real number of participants and no synthetic ones. This is the only form of tool evaluation possible before site data exist, and it would show whether the rule prompts, the Source labels and the register fields are understood.

### 4. Site pilot

A site pilot would collect a daily diary for each masonry activity, with cause codes equal to the library risk identifiers: date, masons and helpers present, quantity laid (in one unit chosen at the start), hours lost and cause, rain and heat, hoist, scaffold and mixer status, material received, hold points passed; plus a start-of-activity snapshot of every rule fact. The project records plan three to five completed activities for a first phase. With so few activities only descriptive comparisons are possible, and the report should say so. The four comparisons planned in the project records are: (a) did the tool's flags include the risks that happened (hit rate); (b) does the order of the matrix match the days lost (Spearman correlation); (c) do entered probabilities match how often risks occurred, which needs many activities; and (d) only if the quantitative layer is used, did the actual delay fall inside the simulated range. All diary numbers would be Historical Data. Site access and permission are the main obstacles.

### 5. Prerequisites for the parts of the registered title that were not built

**Table 8.2.** What each deferred part of the registered title would need before it could be built or switched on honestly. Source: `docs/Project_Handoff_Summary.md` sections 6 and 8; `Research_Notes/` (productivity and norms notes); committee reviews of 2026-10-08. Nothing in the third column exists yet.

| Part | Needs | Why the present data cannot supply it |
|---|---|---|
| Labour-productivity model | Measured output per crew per day on masonry activities (unit chosen in advance), crew size and mason-to-helper ratio, wall height and number of openings, weather and working hours, supervision time | The seed surveys rate importance; they contain no output measurements. CPWD and BIS labour norms are planning norms, not measured productivity, and the legacy norms file has a documented defect |
| Prediction from managerial factors | Many activities with managerial factors recorded (supervision hours, material staging, crew ratio) and an observed outcome for each, in enough number to fit and test a model out of sample | There are no projects and no outcomes. Fitting a model to survey importance values would produce a number without meaning |
| Monte Carlo schedule simulation on real risks | For each risk, a frequency from several activities or an elicited probability, and a delay distribution from days lost per event, each with a Source | RII is not a probability or days; the tool refuses to use seed placements in the simulation. The layer already runs on entered numbers, but nothing entered so far is evidence |
| Expected-monetary-value command | Cost of one delay day from the contract (liquidated damages, site overheads), cost quotations for each response, and an observed or elicited effect of each response on probability or delay | No cost or effect size exists in the project; the tool deliberately supplies none |
| Rules matrix of 27 states | A source for every cell, or a replacement by rules with practitioner endorsement | The original cells had no source; the present 22 rules carry no numbers |

None of these is a coding task. Each is a data-collection task, and the pilot in item 4 is its first step.

### 6. A single clean re-run of the seed statistics

When the second coder has reported and the omitted factors of A14, A10 and A21 have been entered, re-run the secondary-data analysis once with the family of tests fixed in advance, permutation p-values, Holm correction and held-out studies kept out of any reference they are compared with. Correct the generator text of the corpus scripts (F19, F20) and the circular figures that the older statistics scripts still print (F01), so that a re-run does not reintroduce withdrawn wording.

### 7. Routes to a paper

The work supports two modest routes, and not a claim of a validated predictive framework. The first is a paper that combines the expert survey (item 1) with a face-validity and usability evaluation of the tool (item 3). The second is a methods note on how unstable RII-based rankings of delay factors are across South Asian surveys, and what that means for seeding a risk register, built on the secondary-data analysis already done and the single clean re-run of item 6. Either needs the corresponding primary data or the re-run first. Publication in a particular indexed journal is not claimed here.

## Closing statement

What has been built is a small, careful instrument: a library of masonry delay risks tied to the surveys that support them, a set of site-fact prompts, a register in which no number appears without its Source, and a record of what was checked and what was withdrawn. What it has not done is show that any of this changes a decision on a site. The most useful next step is to put it in front of site engineers and to record, with their permission and with real numbers, what happens on their next masonry activities.
