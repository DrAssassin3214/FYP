# Chapter 4. Secondary-Data Analysis

This chapter reports every analysis defined in Section 3.8, with the numbers as the scripts produced them. All tables and figures are Derived Calculations: their inputs are Literature values (the 182 seed rows) or the Assumption inputs of the illustrative example case, as each caption states, and every caption gives n. The scripts are in `analysis/` and `report/scripts/`; the outputs are in `analysis/out/`; the figures are copies of the files there, with chapter-based names. Two rules govern how the results are worded. RII is an importance rating, so every analysis concerns the order of risks and never a probability or a number of days. The surveys are few and overlap little, so a result that is not significant is described as low-powered and inconclusive, not as evidence that agreement is absent.

## 4.1 What was run

Table 4.1 gives the inventory. The rows follow the order of the sections below, which is the order of the question set in Section 3.1.

**Table 4.1.** Analyses reported in this chapter (Derived Calculation; counts of risks, runs, draws or resamples as shown)

| Section | Analysis | Inputs | n |
|---|---|---|---|
| 4.2 | Seed table and two worked examples | 66 direct seed values | 30 seeded risks |
| 4.3 | Behaviour of the bands and of the 5x5 rule | seed classes; thresholds | 30 risks; 969 cut-off triples |
| 4.4 | Example-case sensitivity (S1) | ILLUSTRATIVE example, Assumption inputs | 7 risks; 84 one-at-a-time runs; 25 grid cells; 5000 draws |
| 4.5 | Edge and threshold sensitivity (S2) | same example | 7 risks; 55 scenarios; 5000 draws |
| 4.6 | Seed-band sensitivity (S3) | Literature | 30 risks; 14 variants |
| 4.7 | Bootstrap and jackknife tiers (S3) | Literature | 30 risks; 5 seed studies; 2000 resamples |
| 4.8 | Non-circular inter-study agreement (S4) | Literature | 11 studies; 55 pairs; 13 tested |
| 4.9 | RII uncertainty (S5) | Literature | 30 seeded risks; 11 studies |

## 4.2 The 30-risk literature seed

Table 4.2 is the seed as `app.literature_seed.seed_table()` returns it, with the library name of each risk. The study means are the per-study averages of Step 2 of Section 3.6. The "Level" column applies the 5x5 rule to a risk whose probability class and impact class are both equal to its seed class (Assumption, AS-6); it is shown to document what the tool does and is not a finding about the risk.

**Table 4.2.** The literature seed, 30 seeded risks (Derived Calculation from Literature values; n = 30 risks, 66 direct values from 5 seed studies; classes and levels are Assumptions of the tool)

| Rank | Risk | Library name | Seed studies (n) | Seed mean RII | Class | Level if p-class = i-class | Study means (Literature, averaged per study) |
|--:|---|---|--:|--:|--:|---|---|
| 1 | R-MAT | Brick / block / mortar material shortage or late delivery | 3 | 0.7889 | 5 | Extreme | A02 0.7800, A14 0.8098, M01 0.7770 |
| 2 | R-SAFE | Unsafe conditions or work at height | 1 | 0.7865 | 5 | Extreme | M01 0.7865 |
| 3 | R-SKILL | Unskilled or unqualified labour | 3 | 0.7831 | 5 | Extreme | A02 0.7870, A15 0.8033, M01 0.7590 |
| 4 | R-PLAN | Poor planning or unrealistic scheduling | 2 | 0.7771 | 5 | Extreme | M01 0.7910, M06 0.7632 |
| 5 | R-PAY | Payment delay | 3 | 0.7733 | 5 | Extreme | A02 0.7758, M01 0.7730, M06 0.7711 |
| 6 | R-DIS | Poor labour discipline or weak site leadership | 2 | 0.7700 | 5 | Extreme | A15 0.7900, M01 0.7500 |
| 7 | R-LAB | Labour absenteeism or shortage | 3 | 0.7662 | 4 | Extreme | A02 0.7510, A14 0.8245, M01 0.7230 |
| 8 | R-SCP | Unclear scope or inadequate project formulation | 1 | 0.7642 | 4 | Extreme | M06 0.7642 |
| 9 | R-SITE | Poor site access, clearance or conditions | 2 | 0.7611 | 4 | Extreme | A02 0.7510, M06 0.7711 |
| 10 | R-DES | Design changes or incomplete documentation | 2 | 0.7585 | 4 | Extreme | M01 0.7320, M06 0.7851 |
| 11 | R-RWK | Rework due to workmanship or defects | 2 | 0.7561 | 4 | Extreme | M01 0.7360, M06 0.7761 |
| 12 | R-TOOL | Tools and equipment delay | 2 | 0.7528 | 4 | Extreme | A02 0.7600, M01 0.7455 |
| 13 | R-INC | Inadequate wages or incentives | 1 | 0.7520 | 3 | Moderate | M01 0.7520 |
| 14 | R-STR | Labour strikes or disputes | 1 | 0.7493 | 3 | Moderate | M06 0.7493 |
| 15 | R-CTR | Contractual disputes and claims | 1 | 0.7468 | 3 | Moderate | M06 0.7468 |
| 16 | R-SUP | Inadequate supervision or monitoring of workers | 1 | 0.7440 | 3 | Moderate | M01 0.7440 |
| 17 | R-MOT | Low motivation, morale or labour turnover | 1 | 0.7360 | 3 | Moderate | M01 0.7360 |
| 18 | R-MGT | Poor site management and coordination | 2 | 0.7331 | 3 | Moderate | M01 0.7090, M06 0.7572 |
| 19 | R-CST | Cost control and budget updating problems | 1 | 0.7184 | 2 | Low | M06 0.7184 |
| 20 | R-OVT | Overtime and long working hours | 2 | 0.7063 | 2 | Low | M01 0.7250, M06 0.6876 |
| 21 | R-ACC | Accidents and injuries on site | 2 | 0.7045 | 2 | Low | A02 0.6500, M01 0.7590 |
| 22 | R-MTH | Construction method or design complexity | 1 | 0.7000 | 2 | Low | M01 0.7000 |
| 23 | R-STO | Poor material storage or handling | 1 | 0.7000 | 2 | Low | A02 0.7000 |
| 24 | R-WX | Rain / monsoon stoppage | 4 | 0.6934 | 2 | Low | A02 0.7000, A14 0.6528, M01 0.7640, M06 0.6567 |
| 25 | R-COM | Poor communication or misunderstanding on site | 2 | 0.6793 | 1 | Low | A02 0.6800, M06 0.6786 |
| 26 | R-PRC | Material price escalation | 2 | 0.6695 | 1 | Low | A02 0.5500, A14 0.7890 |
| 27 | R-ECO | Economic conditions, inflation or interest rates | 1 | 0.6612 | 1 | Low | M06 0.6612 |
| 28 | R-WAT | Water shortage | 1 | 0.6500 | 1 | Low | A02 0.6500 |
| 29 | R-FAT | Worker fatigue, age or personal problems | 1 | 0.6100 | 1 | Low | A02 0.6100 |
| 30 | R-SOC | Social or community environment | 1 | 0.5940 | 1 | Low | M06 0.5940 |

Source: `app.literature_seed.seed_table()` (basis "seed"); `data/literature_seed.json`; risk names from `data/risk_library_masonry.json`. R-MTH and R-STO tie at 0.7000 and are ordered by id.

Six features of the table matter for everything that follows.

*The spread is small.* The seed means run from 0.594 (R-SOC) to 0.789 (R-MAT), a range of 0.195. Ranks 1 to 6 lie within 0.019 of each other (0.7889 to 0.7700), and ranks 1 to 24 within 0.096. The median gap between adjacent ranks is 0.0034 (S5). The class of a risk therefore depends on small differences in a mean of at most four numbers.

*Fourteen of the 30 risks rest on a single study*: R-CST, R-CTR, R-ECO, R-FAT, R-INC, R-MOT, R-MTH, R-SAFE, R-SCP, R-SOC, R-STO, R-STR, R-SUP and R-WAT (S0). For those the "average across studies" is one study's number.

*Sixteen library risks have no seed.* R-CLI, R-DEF, R-FIN, R-GOV, R-PRD, R-QLT, R-SUB and R-TRN have no direct value in the seed studies, and eight further risks added on 2026-10-08 (R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT) were written without seed rows. They stay off the matrix until numbers are entered. Several of the omitted risks (work-front release, scaffolding, the hoist) are the ones a site manager might most expect, and no seed study has a direct value for them.

*Six per class is a rule, not a result.* Equal-count banding puts exactly six risks in each class whatever the data (S0 confirms 6, 6, 6, 6, 6).

*Seed studies differ in kind.* M01 lists only items rated 0.70 or higher; A14 and A15 contribute four values each; A02 is on a 1-4 scale. The class of a risk reflects which of these studies happened to report it.

*One tie exists* (R-MTH and R-STO at 0.7000), broken alphabetically.

**Worked example 4.1: one risk placed on the matrix by hand.** R-LAB has seed class 4 (Worked example 3.2). Both axes take the class: probability class 4, impact class 4. The score is $4 \times 4 = 16$. The level thresholds are 5, 10 and 15; a score of 16 exceeds 15, so the level is Extreme (the code takes `bisect_right([5,10,15], 16 - 1)`, which is 3, the fourth name). If a site-fact rule marks R-LAB as elevated, the probability class becomes $\min(5, 4 + 1) = 5$, the score $5 \times 4 = 20$, and the level stays Extreme. The returned placement agrees: `seed_for("R-LAB")` gives p class 4, impact class 4, and `seed_for("R-LAB", elevated=True)` gives p class 5, impact class 4, with `raised_by_rule` true. For contrast, a risk with entered numbers is placed from its inputs. In the illustrative example R-MAT has p = 0.5 and a PERT delay with minimum 1, most likely 3 and maximum 8 days, so the expected delay if it occurs is $(1 + 4 \cdot 3 + 8)/6 = 3.5$ days. The planned duration is 16 days, so the ratio is $3.5/16 = 0.21875$. With impact edges 0.02, 0.05, 0.10 and 0.20, the ratio has reached all four, so the impact class is 5. With probability edges 0.2, 0.4, 0.6 and 0.8, p = 0.5 has reached two, so the probability class is 3. The score is 15, which is High. The tool returns p class 3, impact class 5, score 15, High (S1, base case). All inputs of the second calculation are Assumptions (ILLUSTRATIVE); the first uses Literature values and the assumed rule.

## 4.3 Behaviour of the bands and of the 5x5 rule

Section 3.7 showed that the rule has 10 Low, 7 Moderate, 4 High and 4 Extreme cells (Derived Calculation, n = 25 cells; `ch34_build.py` recounts them from `matrix_level`). Applied to the seeded risks, with the same class on both axes, the effect is stark (Table 4.3).

**Table 4.3.** Levels of the 30 seeded risks under the repo rule (Derived Calculation; n = 30 risks; classes from Table 4.2; same class on both axes is an Assumption)

| Case | Low | Moderate | High | Extreme |
|---|--:|--:|--:|--:|
| Placed as the tool does, no rule flag | 12 | 6 | 0 | 12 |
| Hypothetical: every seeded risk carries an "elevated" flag (probability class + 1, cap 5) | 6 | 6 | 6 | 12 |

Source: `ch34_build.py` (facts in `report/scripts/out/facts.json`). The second row is a structural illustration of Assumption AS-7, not a scenario that occurs in the example case.

With no flag, no seeded risk can be High, and risks in classes 4 and 5 are all Extreme, so the twelve most important risks by seed rank are all "Extreme" although their seed means differ by at most 0.0361 (R-MAT 0.7889 to R-TOOL 0.7528). The boundary between ranks 12 and 13 shows the label's arbitrariness: R-TOOL (0.7528, class 4, Extreme) and R-INC (0.7520, class 3, Moderate) differ by 0.00075 in mean RII, which is smaller than the change in an M01 RII caused by one respondent moving one Likert point (0.0045 at N = 44; Handoff Section 8.2). One flag lifts a class 3 risk from Moderate to High and a class 2 risk from Low to Moderate, so in the flagged row six risks are High.

The levels also depend on the cut-offs. Table 4.4 gives the effect of six named alternatives on the seeded placements, and Figure 4.1 shows the distribution over all 969 admissible triples $t_1 < t_2 < t_3$ in 2 to 20.

**Table 4.4.** Levels of the 30 seeded risks under alternative level cut-offs (Derived Calculation; n = 30 risks per row; cut-offs are the upper score of Low, Moderate and High; same class on both axes is an Assumption)

| Cut-offs (Low/Mod/High upper score) | Risks changing level (of 30) | Low | Moderate | High | Extreme |
|---|--:|--:|--:|--:|--:|
| 5/10/15 (repo) | 0 | 12 | 6 | 0 | 12 |
| 4/9/15 | 0 | 12 | 6 | 0 | 12 |
| 4/9/16 | 6 | 12 | 6 | 6 | 6 |
| 4/8/12 | 6 | 12 | 0 | 6 | 12 |
| 6/12/16 | 6 | 12 | 6 | 6 | 6 |
| 3/8/14 | 12 | 6 | 6 | 6 | 12 |
| 5/10/20 | 6 | 12 | 6 | 6 | 6 |

Source: `ch34_build.py`.

![Figure 4.1. Number of the 30 seeded risks whose level changes when the cut-offs change, over all 969 triples (Derived Calculation; n = 30 risks x 969 triples).](figures/ch4_seed30_cutoff_histogram.png)

Over the 969 triples the median number of changed levels is 6 of 30 (interquartile range 6 to 12, range 0 to 18); in 10.8% of triples no seeded level changes. Because six risks share each diagonal score, a cut-off that moves past one diagonal score changes six labels at once. The levels of seeded placements are therefore a function of the assumed thresholds as much as of the evidence, which is consistent with the application's decision to draw them as an ordinal tier and exclude them from level totals.

## 4.4 Example-case sensitivity (S1)

S1 uses the illustrative example case, which has 7 risks, a planned duration of 16 days, probabilities from 0.10 to 0.50 and PERT delays of 1 to 8 days, all placeholders (Assumption, ILLUSTRATIVE; Table 4.5). It tests how the classification rule responds to its inputs. It says nothing about how a real site behaves. With 7 risks, the counts below are descriptions of one small case, not a sample.

**Table 4.5.** The example case as classified (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks; planned duration 16 days; impact edges 0.02/0.05/0.10/0.20 of planned duration)

| Risk | p (Assumption) | Distance of p to nearest p edge | Expected delay / planned duration | Distance of ratio to nearest impact edge | p class | Impact class | Level |
|---|--:|--:|--:|--:|--:|--:|---|
| R-MAT | 0.5 | 0.1 | 0.2188 | 0.0938 | 3 | 5 | High |
| R-LAB | 0.35 | 0.05 | 0.1562 | 0.2188 | 2 | 4 | Moderate |
| R-RWK | 0.25 | 0.05 | 0.1458 | 0.2708 | 2 | 4 | Moderate |
| R-WX | 0.2 | 0.0 | 0.1667 | 0.1667 | 2 | 4 | Moderate |
| R-PLAN | 0.1 | 0.1 | 0.0833 | 0.1667 | 1 | 3 | Low |
| R-SAFE | 0.3 | 0.1 | 0.1562 | 0.2188 | 2 | 4 | Moderate |
| R-SKILL | 0.22 | 0.02 | 0.1458 | 0.2708 | 2 | 4 | Moderate |

Source: `analysis/out/s2_edge_margins.csv`; inputs from `examples/example_case.json`. Expected delay is the mean of the PERT delay (a + 4m + b)/6.

Five risks (R-LAB, R-RWK, R-WX, R-SAFE, R-SKILL) are probability class 2 and impact class 4 and are Moderate (score 8). R-MAT is High (score 15) and R-PLAN Low (score 3). R-WX has p = 0.20, exactly on the first probability edge, so under the lower-edge-inclusive rule it is class 2 and any shift of that edge or of p flips it. This single placeholder drives many of the counts below.

**One at a time.** Each risk's p, its delay days (a, m, b together) or both were multiplied by 0.5, 0.8, 1.2 and 1.5 (p capped at 1), with the other six risks unchanged. 84 runs were made. No run changed the level of any other risk (`oat_other_risks_ever_changed` is 0): the matrix is per-risk and independent.

**Table 4.6.** Number of the 7 risks whose level changes when one input is scaled, one risk at a time summed over risks (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks x 4 factors per input; 84 runs in all)

| Input changed | x0.5 | x0.8 | x1.2 | x1.5 |
|---|--:|--:|--:|--:|
| p | 6 | 2 | 2 | 3 |
| delay | 0 | 0 | 0 | 0 |
| p+delay | 6 | 2 | 2 | 3 |

Source: `analysis/out/s1_summary.json`. Each cell counts risks, 7 at most, whose own level changed when that risk alone was scaled by the factor shown.

The level responds to probability and not to delay. Scaling every risk's delay by 0.5 to 1.5 changes no level, because the probability class caps the score: a risk of probability class 2 scores at most $2 \times 5 = 10$, still Moderate. Delay changes the impact class (for example R-MAT drops from impact class 5 to 4 at 0.91 times its delay) but not the level. Table 4.7 gives the break-even multiplier, the smallest scaling of one input within 0.30 to 2.00 (step 0.01) at which a class or level first changes.

**Table 4.7.** Break-even multipliers, one input of one risk at a time (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks; grid 0.30 to 2.00 in steps of 0.01)

| Risk | Input | Up: first multiplier changing class | Down: first multiplier changing class | Up: first multiplier changing level | Down: first multiplier changing level |
|---|---|--:|--:|--:|--:|
| R-MAT | p | 1.2 | 0.79 | 1.2 | 0.79 |
| R-MAT | delay | none in 0.30-2.00 | 0.91 | none in 0.30-2.00 | 0.45 |
| R-LAB | p | 1.15 | 0.57 | 1.15 | 0.57 |
| R-LAB | delay | 1.28 | 0.63 | none in 0.30-2.00 | 0.31 |
| R-RWK | p | 1.6 | 0.79 | 1.6 | 0.79 |
| R-RWK | delay | 1.38 | 0.68 | none in 0.30-2.00 | 0.34 |
| R-WX | p | 2.0 | 0.99 | 2.0 | 0.99 |
| R-WX | delay | 1.2 | 0.59 | none in 0.30-2.00 | none in 0.30-2.00 |
| R-PLAN | p | 2.0 | none in 0.30-2.00 | 2.0 | none in 0.30-2.00 |
| R-PLAN | delay | 1.2 | 0.59 | none in 0.30-2.00 | none in 0.30-2.00 |
| R-SAFE | p | 1.34 | 0.66 | 1.34 | 0.66 |
| R-SAFE | delay | 1.28 | 0.63 | none in 0.30-2.00 | 0.31 |
| R-SKILL | p | 1.82 | 0.9 | 1.82 | 0.9 |
| R-SKILL | delay | 1.38 | 0.68 | none in 0.30-2.00 | 0.34 |

Source: `analysis/out/s1_breakeven.csv`. "none in 0.30-2.00" means no change anywhere on the grid.

Probability changes a level at multipliers between 0.57 and 2.0, risk by risk: R-MAT at +20% or -21%, R-LAB at +15%, R-SAFE at +34%. R-WX flips down at 0.99, because it sits on the edge. Delay changes a level only for decreases of 55% to 69% (multipliers 0.31 to 0.45), and not at all within the grid for R-WX and R-PLAN. Delay increases up to double change no level.

**Joint changes.** Scaling all probabilities and all delays together on a 5x5 grid (25 cells) and drawing each input's factor independently from U(0.5, 1.5) 5000 times (seed 20261008) give the same picture as the single-input runs (Figure 4.3; grid and per-risk shares in `analysis/out/s1_joint_grid_summary.csv` and `s1_joint_random_by_risk.csv`). On average 2.48 of the 7 levels change per draw, and in 4% of draws none does.

![Figure 4.2. One-at-a-time sensitivity of the matrix score (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks; 84 runs). Dashed lines are the level cut-offs.](figures/ch4_s1_oat_scores.png)

![Figure 4.3. Joint sensitivity: risks with a level change on the 5x5 grid (left) and share of random draws with a level change by risk (right) (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks; 25 cells; 5000 draws).](figures/ch4_s1_joint.png)

The grid and the draws agree with the single-input results. Scaling all probabilities by 0.5 changes 6 of 7 levels whatever the delay factor; by 0.8, 2; by 1.2, 2 (1 at a delay factor of 0.5); by 1.5, 3 (1 at a delay factor of 0.5). Delay only matters at the margins of the grid: a probability factor of 1.2 or 1.5 together with a delay factor of 0.5 gives 1 changed level instead of 2 or 3, because the shorter delay offsets the higher probability for one risk. In the random draws, R-PLAN never changes level (p = 0.10 and a short delay keep it Low), R-MAT changes in 59% of draws, R-WX in 50% (its edge position), and R-LAB and R-SAFE can move up or down.

What this shows is how the rule responds to inputs: the ordinal level is governed by the probability class, and a change of the assumed probabilities by 20 to 50% changes the level of between 2 and 6 of 7 risks. It does not show that any real risk is sensitive to probability, and the example's numbers are placeholders.

## 4.5 Edge and threshold sensitivity (S2)

S2 varies the classification edges and thresholds on the same example, in 55 named scenarios and 5000 random edge draws. For each scenario it counts how many of the 7 risks change class and how many change level. Both counts are reported, because counting levels alone hides class changes (Table 4.8).

**Table 4.8.** Level changes under edge and threshold scenarios (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks per scenario; 55 scenarios in 7 groups)

| Scenario group (ILLUSTRATIVE example, 7 risks) | Scenarios | Levels changed: min-median-max (of 7) | Max p classes changed | Max impact classes changed |
|---|--:|---|--:|--:|
| One p edge shifted by -0.10, -0.05, +0.05 or +0.10 | 16 | 0-0-3 | 3 | 0 |
| All four p edges shifted together by the same amounts | 4 | 1-2.5-4 | 4 | 0 |
| Alternative p-edge sets (4) | 4 | 2-4.5-7 | 7 | 0 |
| One impact edge scaled (x0.5 to x2) | 16 | 0-0-0 | 0 | 3 |
| All four impact edges scaled (x0.5 to x2) | 5 | 0-0-0 | 0 | 7 |
| Alternative impact-edge sets (3) | 3 | 0-0-6 | 0 | 7 |
| Alternative level cut-offs (7 named triples) | 7 | 0-0-1 | 0 | 0 |

Source: `analysis/out/s2_summary.json` and `s2_threshold_scenarios.csv`. Median of the single-edge group is 0.

*Probability edges.* Shifting all four edges by -0.10 changes four levels (R-MAT, R-LAB, R-PLAN, R-SAFE); by +0.10, three (R-RWK, R-WX, R-SKILL). A low-skewed alternative set (0.05, 0.15, 0.35, 0.65) changes all seven. Shifting a single edge matters only when a risk sits near it: the first edge (0.2) at -0.10 flips R-PLAN (p = 0.10) and at +0.05 flips R-WX and R-SKILL (p = 0.20 and 0.22). The fourth edge (0.8) never matters here because no example risk has p above 0.5.

*Impact edges.* Scaling the impact edges changes the impact class of up to all seven risks (six at x0.5, seven at x2), but changes no level. Again the probability class caps the score: with probability class 2 or lower, even impact class 5 gives at most 10, Moderate, and probability class 1 gives at most 5, Low. Only one alternative changes levels, equal-width impact edges (0.2, 0.4, 0.6, 0.8), which put six risks in a lower level because every impact class falls to 1 or 2 (the delay ratios, 0.08 to 0.22, lie at or just above the first edge of 0.2). The statement "the matrix is robust to the impact edges" would therefore be wrong in general: it holds here because the placeholder probabilities are low.

*Level cut-offs.* Of seven named triples, two change one level (R-MAT, at 4/8/12 and 3/8/14), and five change none. Over all 2,024 admissible triples with cut-offs between 1 and 24 (S2) the median is 5 of 7 risks changing level (interquartile range 1 to 6). The seeded placements in Section 4.3 are more exposed, with a median of 6 of 30.

*Random edges.* Jittering each probability edge independently by up to 0.05 changes at least one level in 48% of 5000 draws (mean 0.77 changed levels, maximum 2); jittering impact edges by up to 50% changes none; jittering both gives the same as probability jitter. By risk, the levels that move are R-WX (48% of draws) and R-SKILL (29%), the two risks whose p lies within 0.02 of an edge (Table 4.5, column 3).

![Figure 4.4. Level and class changes across the 55 named edge and threshold scenarios (Derived Calculation from Assumption inputs, ILLUSTRATIVE; n = 7 risks; 55 scenarios).](figures/ch4_s2_threshold_scenarios.png)

The result is a description of how fragile the level label is near an edge. The margin table (Table 4.5) shows which placeholders sit close to an edge: R-WX at 0.00 and R-SKILL at 0.02 from a probability edge, the rest at 0.05 to 0.10. A real user's numbers will have their own margins.

## 4.6 Seed-band sensitivity (S3)

S3 asks how many seeded risks change class when the banding rule or the data are changed. The 14 variants of Table 4.9 were fixed in advance and are all reported. Percentages are of the risks common to the variant and the base rule (30 unless the variant drops a risk). Spearman's rho is between the variant's per-risk means and the base means; Kendall's tau between the classes.

**Table 4.9.** Class changes under banding and data variants (Derived Calculation from Literature values; n = 30 seeded risks, 5 seed studies; one row per variant)

| Variant | Risks | Changed class | % changed | Spearman of mean RII vs base | Kendall tau of classes | Class counts (class:risks) | Dropped | Added |
|---|--:|--:|--:|--:|--:|---|---|---|
| repo rule: 5 equal-count bands (6 per band) | 30 | 0 | 0.0 | 1.00 | 1.00 | 1:6 2:6 3:6 4:6 5:6 | - | - |
| 3 equal-count bands (tertiles), mapped to classes 1/3/5 | 30 | 12 | 40.0 | 1.00 | 0.86 | 1:10 3:10 5:10 | - | - |
| 4 equal-count bands, mapped to 1-5 | 30 | 9 | 30.0 | 1.00 | 0.90 | 1:7 2:8 4:7 5:8 | - | - |
| 5 equal-width bands on mean RII | 30 | 22 | 73.3 | 1.00 | 0.89 | 1:2 2:3 3:6 4:6 5:13 | - | - |
| fixed RII cut-offs 0.2/0.4/0.6/0.8 | 30 | 24 | 80.0 | 1.00 | 0.23 | 3:1 4:29 | - | - |
| fixed RII cut-offs 0.60/0.65/0.70/0.75 | 30 | 23 | 76.7 | 1.00 | 0.86 | 1:1 2:1 3:5 4:10 5:13 | - | - |
| direct + related mappings | 32 | 8 | 26.7 | 0.96 | 0.88 | 1:6 2:6 3:7 4:6 5:7 | - | R-CLI R-QLT |
| >= 2 seed studies per risk (re-banded) | 16 | 6 | 37.5 | 1.00 | 0.91 | 1:3 2:3 3:3 4:3 5:4 | R-CST R-CTR R-ECO R-FAT R-INC R-MOT R-MTH R-SAFE R-SCP R-SOC R-STO R-STR R-SUP R-WAT | - |
| scale-rescaled (RII-1/k)/(1-1/k) | 30 | 2 | 6.7 | 0.99 | 0.97 | 1:6 2:6 3:6 4:6 5:6 | - | - |
| within-study percentile rank (studies with >= 3 risks) | 30 | 11 | 36.7 | 0.92 | 0.80 | 1:6 2:6 3:6 4:6 5:6 | - | - |
| drop seed study A02 | 27 | 13 | 48.1 | 0.78 | 0.67 | 1:5 2:5 3:6 4:5 5:6 | R-FAT R-STO R-WAT | - |
| drop seed study A14 | 30 | 2 | 6.7 | 0.97 | 0.97 | 1:6 2:6 3:6 4:6 5:6 | - | - |
| drop seed study A15 | 30 | 3 | 10.0 | 0.99 | 0.92 | 1:6 2:6 3:6 4:6 5:6 | - | - |
| drop seed study M01 | 25 | 9 | 36.0 | 0.95 | 0.83 | 1:5 2:5 3:5 4:5 5:5 | R-INC R-MOT R-MTH R-SAFE R-SUP | - |
| drop seed study M06 | 24 | 6 | 25.0 | 0.96 | 0.89 | 1:4 2:5 3:5 4:5 5:5 | R-CST R-CTR R-ECO R-SCP R-SOC R-STR | - |

Source: `analysis/out/s3_band_variants.csv`. Variants with fewer risks list the risks dropped or added.

Three groups of variants differ in meaning.

*Banding rules* change which risks share a class even though the order of the risks is unchanged (Spearman 1.00 in every row). With tertiles mapped to classes 1, 3 and 5, 12 of 30 classes change; with four equal-count bands, 9; with five equal-width bands on mean RII, 22, because 13 risks fall in the top band; with fixed RII cut-offs of 0.2, 0.4, 0.6 and 0.8, 24, because 29 of 30 risks fall in class 4 (all means lie between 0.59 and 0.79). A probability-like fixed scale applied to RII is not informative here. Fixed cut-offs of 0.60, 0.65, 0.70 and 0.75 change 23. These changes are by construction: they show that a class belongs to the rule, not to the risk.

*Data variants.* Adding `related` mappings (32 risks, adding R-CLI and R-QLT) changes 8 of 30 classes (Spearman 0.96, largest rank shift 10). Restricting to risks with at least two seed studies re-bands 16 risks and changes 6 of them. Rescaling each study's RII as $(\mathrm{RII} - 1/k)/(1 - 1/k)$ for scale points k changes 2 (Spearman 0.99): mixing 1-4 and 1-5 scales has a small effect on the order. Replacing RII by within-study percentile rank changes 11 of 30 (Spearman 0.92, largest rank shift 8). Switching the repository's seed basis to "all" (held-out studies and related mappings pooled; S0) changes the class of 24 of the 30 common risks.

*Dropping a seed study.* Dropping A02 changes 13 of the 27 remaining risks (48%; Spearman 0.78, largest rank shift 23) and removes R-FAT, R-STO and R-WAT. Dropping M01 changes 9 of 25, M06 6 of 24, A15 3 of 30 and A14 2 of 30. The class of a seeded risk depends on which studies are present, and most on A02, a study whose N is not reported, whose scale is 1-4 and whose values come from the research notes.

Across all 14 variants between 2 and 24 of the common risks change class (6.7% to 80%); the data variants that keep five bands change between 2 and 13 risks. The order of the means is more stable than the classes: every banding variant keeps Spearman 1.00, and the data variants keep 0.78 to 1.00.

**Table 4.10.** Gaps in seed mean RII at the four band boundaries of the repo rule (Derived Calculation from Literature values; n = 30 risks)

| Band boundary (ranks) | Upper risk | Lower risk | Gap in seed mean RII |
|---|---|---|--:|
| 6-7 | R-DIS | R-LAB | 0.00383 |
| 12-13 | R-TOOL | R-INC | 0.00075 |
| 18-19 | R-MGT | R-CST | 0.01470 |
| 24-25 | R-WX | R-COM | 0.01408 |

Source: `analysis/out/s3_band_boundary_gaps.csv`.

![Figure 4.5. Percentage of risks changing class under each variant (left) and Kendall tau of the study-bootstrap ranking against the base ranking (right) (Derived Calculation from Literature values; n = 30 seeded risks; 5 seed studies; 2000 resamples).](figures/ch4_s3_variants_rank_stability.png)

The boundary between ranks 6 and 7 (R-DIS to R-LAB) is 0.0038 wide; between 12 and 13 it is 0.00075; the two outer boundaries are about 0.014 wide. Two risks on either side of the narrower boundaries differ by less than the effect of one respondent in the smallest-N seed survey with a printed N.

## 4.7 Bootstrap and jackknife tiers (S3)

The seed was rebuilt 2000 times from five studies drawn with replacement. The Kendall tau between the resampled mean ordering and the base ordering averages 0.784 (2.5th to 97.5th percentile 0.476 to 1.000) and Spearman's rho 0.884 (0.60 to 1.00). On average 24.5 of the 30 risks are present in a resample (range 14 to 30), and the share of present risks keeping their base class averages 0.664 (0.316 to 1.000). Five risks keep their base class in fewer than half of the resamples where they are present: R-LAB, R-DES, R-RWK, R-INC and R-DIS. Table 4.11 gives every risk, and Figure 4.6 shows the class distribution.

**Table 4.11.** Class stability of each seeded risk under study resampling (Derived Calculation from Literature values; n = 30 risks, 5 seed studies, 2000 resamples; shares are conditional on the risk being present in the resample)

| Rank | Risk | Base class | Seed studies | Present | P(same class) | P(class 5) | P(top 10) | Rank in resamples (2.5%-median-97.5%) |
|--:|---|--:|--:|--:|--:|--:|--:|---|
| 1 | R-MAT | 5 | 3 | 0.99 | 1.00 | 1.00 | 1.00 | 1-2-4 |
| 2 | R-SAFE | 5 | 1 | 0.67 | 0.97 | 0.97 | 1.00 | 1-2-5 |
| 3 | R-SKILL | 5 | 3 | 0.99 | 0.87 | 0.87 | 0.94 | 1-3-10 |
| 4 | R-PLAN | 5 | 2 | 0.91 | 0.72 | 0.72 | 0.89 | 1-4-11 |
| 5 | R-PAY | 5 | 3 | 0.99 | 0.51 | 0.51 | 0.93 | 4-5-8 |
| 6 | R-DIS | 5 | 2 | 0.92 | 0.43 | 0.43 | 0.72 | 2-6-14 |
| 7 | R-LAB | 4 | 3 | 0.99 | 0.34 | 0.35 | 0.64 | 1-7-19 |
| 8 | R-SCP | 4 | 1 | 0.67 | 0.79 | 0.14 | 0.79 | 6-8-11 |
| 9 | R-SITE | 4 | 2 | 0.93 | 0.77 | 0.07 | 0.57 | 6-8-11 |
| 10 | R-DES | 4 | 2 | 0.91 | 0.38 | 0.27 | 0.52 | 3-10-15 |
| 11 | R-RWK | 4 | 2 | 0.91 | 0.43 | 0.14 | 0.44 | 4-11-14 |
| 12 | R-TOOL | 4 | 2 | 0.93 | 0.68 | 0.00 | 0.27 | 6-10-17 |
| 13 | R-INC | 3 | 1 | 0.67 | 0.37 | 0.00 | 0.30 | 7-10-14 |
| 14 | R-STR | 3 | 1 | 0.67 | 0.91 | 0.00 | 0.01 | 11-13-15 |
| 15 | R-CTR | 3 | 1 | 0.67 | 0.90 | 0.00 | 0.00 | 12-14-16 |
| 16 | R-SUP | 3 | 1 | 0.67 | 0.74 | 0.00 | 0.00 | 10-15-18 |
| 17 | R-MOT | 3 | 1 | 0.67 | 0.64 | 0.00 | 0.00 | 12-17-20 |
| 18 | R-MGT | 3 | 2 | 0.91 | 0.51 | 0.00 | 0.00 | 10-17-20 |
| 19 | R-CST | 2 | 1 | 0.67 | 0.73 | 0.00 | 0.00 | 13-19-21 |
| 20 | R-OVT | 2 | 2 | 0.91 | 0.79 | 0.00 | 0.00 | 15-17-22 |
| 21 | R-ACC | 2 | 2 | 0.93 | 0.54 | 0.00 | 0.09 | 8-19-24 |
| 22 | R-MTH | 2 | 1 | 0.67 | 0.66 | 0.00 | 0.00 | 18-22-24 |
| 23 | R-STO | 2 | 1 | 0.69 | 0.80 | 0.00 | 0.00 | 8-20-24 |
| 24 | R-WX | 2 | 4 | 1.00 | 0.61 | 0.00 | 0.00 | 9-19-25 |
| 25 | R-COM | 1 | 2 | 0.93 | 0.68 | 0.00 | 0.00 | 9-21-25 |
| 26 | R-PRC | 1 | 2 | 0.93 | 0.53 | 0.20 | 0.25 | 1-20-30 |
| 27 | R-ECO | 1 | 1 | 0.67 | 0.81 | 0.00 | 0.00 | 16-26-27 |
| 28 | R-WAT | 1 | 1 | 0.69 | 0.95 | 0.00 | 0.00 | 12-23-28 |
| 29 | R-FAT | 1 | 1 | 0.69 | 1.00 | 0.00 | 0.00 | 13-24-29 |
| 30 | R-SOC | 1 | 1 | 0.67 | 1.00 | 0.00 | 0.00 | 18-27-30 |

Source: `analysis/out/s3_bootstrap_tier_membership.csv`. "Present" is the share of resamples that contain at least one study reporting the risk. "Top 10" is membership of the top third.

![Figure 4.6. Share of resamples placing each risk in each class (Derived Calculation from Literature values; n = 30 seeded risks; 5 seed studies; 2000 study-level bootstrap resamples).](figures/ch4_s3_bootstrap_tier_membership.png)

Reading the table: R-MAT is in class 5 in 99.7% of resamples where present and in rank 1 to 4 in 95% of them, and rests on three studies. R-SAFE is class 5 in 96.8% of resamples but is present in only about 67% of them, because it rests on M01 alone. R-LAB, class 4 at rank 7, is class 5 in 34.5% of resamples, class 4 in 33.9% and ranges over ranks 1 to 19. R-PRC (two studies, 0.55 in A02 and 0.789 in A14) is class 5 in 20% of resamples and class 1 in 53%.

Because five clusters are too few for a reliable percentile interval, the exact leave-one-study-out (jackknife) results are given beside it.

**Table 4.12.** Exact leave-one-study-out rank stability of the seed (Derived Calculation from Literature values; n = 30 risks; five rebuilds)

| Seed study dropped | Risks still seeded | Spearman vs full seed order | Kendall tau | Risks changing class (of 30) |
|---|--:|--:|--:|--:|
| A02 | 27 | 0.78 | 0.77 | 13 |
| A14 | 30 | 0.97 | 0.91 | 2 |
| A15 | 30 | 0.99 | 0.96 | 3 |
| M01 | 25 | 0.95 | 0.84 | 9 |
| M06 | 24 | 0.96 | 0.87 | 6 |

Source: `analysis/out/s3_leave_one_study_out_rank_stability.csv`.

Applying the tier rule of Section 3.8 (class 5 or class 1 to 2 in at least 80% of present resamples, and at least two seed studies) gives Table 4.13, which lists the risks that are not "unresolved".

**Table 4.13.** Tier assignments under the 80% rule, risks that meet a threshold (Derived Calculation from Literature values; n = 30 risks, 2000 resamples; the rule is an Assumption)

| Risk | Base rank | Seed studies (n) | Present in resamples | P(class 5), when present | P(class 1-2), when present | Tier by rule |
|---|--:|--:|--:|--:|--:|---|
| R-MAT | 1 | 3 | 0.993 | 0.997 | 0.000 | Tier 1 (high) |
| R-SAFE | 2 | 1 | 0.665 | 0.968 | 0.000 | high-class but single study (not assessable) |
| R-SKILL | 3 | 3 | 0.988 | 0.868 | 0.000 | Tier 1 (high) |
| R-OVT | 20 | 2 | 0.912 | 0.000 | 0.856 | Tier lower |
| R-MTH | 22 | 1 | 0.665 | 0.000 | 1.000 | low-class but single study (not assessable) |
| R-STO | 23 | 1 | 0.685 | 0.000 | 0.812 | low-class but single study (not assessable) |
| R-WX | 24 | 4 | 1.000 | 0.000 | 0.916 | Tier lower |
| R-COM | 25 | 2 | 0.932 | 0.000 | 0.976 | Tier lower |
| R-ECO | 27 | 1 | 0.668 | 0.000 | 1.000 | low-class but single study (not assessable) |
| R-WAT | 28 | 1 | 0.685 | 0.000 | 1.000 | low-class but single study (not assessable) |
| R-FAT | 29 | 1 | 0.685 | 0.000 | 1.000 | low-class but single study (not assessable) |
| R-SOC | 30 | 1 | 0.668 | 0.000 | 1.000 | low-class but single study (not assessable) |

Source: `ch34_build.py` applied to `s3_bootstrap_tier_membership.csv`.

Only two risks, R-MAT and R-SKILL, meet the rule for the top tier with at least two studies. R-SAFE meets the 80% threshold but rests on one study and so cannot be assessed. Three risks (R-OVT, R-WX, R-COM) meet the rule for the lower tier, and six single-study risks (R-MTH, R-STO, R-ECO, R-WAT, R-FAT, R-SOC) are low but not assessable. The remaining 18 are unresolved. Two cautions apply to the lower tier. R-WX is in class 1 or 2 in 92% of resamples, yet its four seed studies range from 0.653 to 0.764 (M01 ranks "weather conditions" 8th of 28 printed items, A14 30th, M06 37th). The tier states where the mean of the studies falls in the order of the 30 risks, not that weather is unimportant, and the earlier claim that weather is rated lower than the rest was withdrawn (Audit Corrections, F09). Second, the rule ignores mapping uncertainty and scale differences, so it understates uncertainty.

The data therefore support, at most, coarse tiers: two risks in a high tier, a few in a low tier, and an unresolved middle in which the order is not determined by these studies.

## 4.8 Non-circular inter-study agreement (S4)

S4 compares studies without letting a study into the reference it is compared with. For a seed study X the reference is the seed built from the other four seed studies; for a held-out study it is the full five-study seed. A correlation needs at least five shared risks to be tested at all.

**Coverage.** Little overlap exists (`analysis/out/s4_study_coverage.csv`). Of 55 study pairs, 13 share five or more risks; the other 42 share four or fewer (13 pairs share none, 15 share one, 9 share two, 2 share three, 3 share four). The studies contribute these numbers of risks with a direct mapping (items in brackets): M01 18 (25), A02 13 (13), M06 15 (20), A14 4 (4), A15 2 (4), M10 23 (27), M15 13 (18), M14 15 (18), A10 2 (3), A21 2 (2) and HAS25 1 (1).

**Pairwise agreement.** Table 4.14 gives the 13 testable pairs with n, rho, the two-sided permutation p and the Holm-adjusted p over the 13 tests.

**Table 4.14.** Spearman agreement between studies on shared risks, pairs with n >= 5 (Derived Calculation from Literature values; n = 5 to 15 shared risks per pair; 13 tests; exact p for n <= 8, otherwise 20,000 permutations)

| Pair | Roles | n shared risks | Spearman rho | Two-sided p | p method | Holm p (13 tests) |
|---|---|--:|--:|--:|---|--:|
| M01 - A02 | seed / seed | 7 | 0.32 | 0.482 | exact | 1.000 |
| M01 - M06 | seed / seed | 7 | 0.11 | 0.840 | exact | 1.000 |
| M01 - M10 | seed / held-out | 15 | 0.25 | 0.383 | 20000 permutations | 1.000 |
| M01 - M15 | seed / held-out | 10 | 0.15 | 0.679 | 20000 permutations | 1.000 |
| M01 - M14 | seed / held-out | 11 | -0.16 | 0.634 | 20000 permutations | 1.000 |
| A02 - M10 | seed / held-out | 10 | 0.62 | 0.063 | 20000 permutations | 0.694 |
| A02 - M15 | seed / held-out | 5 | 0.70 | 0.233 | exact | 1.000 |
| A02 - M14 | seed / held-out | 7 | -0.18 | 0.713 | exact | 1.000 |
| M06 - M10 | seed / held-out | 8 | 0.29 | 0.501 | exact | 1.000 |
| M06 - M15 | seed / held-out | 6 | 0.89 | 0.033 | exact | 0.400 |
| M10 - M15 | held-out / held-out | 9 | 0.77 | 0.021 | 20000 permutations | 0.270 |
| M10 - M14 | held-out / held-out | 13 | 0.45 | 0.129 | 20000 permutations | 1.000 |
| M15 - M14 | held-out / held-out | 6 | -0.43 | 0.419 | exact | 1.000 |

Source: `analysis/out/s4_pairwise_spearman.csv`. Values within +-0.003 for permutation p.

The median rho over the 13 tested pairs is 0.29 (range -0.43 to 0.89). Only two pairs have a raw p below 0.05, M10 with M15 (rho 0.77, n = 9, p = 0.021) and M06 with M15 (rho 0.89, n = 6, p = 0.033); after Holm the smallest adjusted p is 0.270 and none is significant. The two seed-seed pairs that can be tested are weak: M01 with A02 0.32 (n = 7) and M01 with M06 0.11 (n = 7). Of the untestable seed pairs, A02 with M06 and A02 with A14 show 0.74 and 0.60 on four shared risks each, which a test could not distinguish from chance, and M01 with A14 shows -0.50 on three. The M15-M14 pair is negative (-0.43, n = 6), consistent with the manager-versus-worker explanation that has been offered post hoc, which this data set cannot test.

![Figure 4.7. Pairwise Spearman agreement (cell text: rho and number of shared risks; grey = n below 5, not tested) (Derived Calculation from Literature values; n = 11 studies, 55 pairs; 13 tested).](figures/ch4_s4_pairwise_spearman.png)

**Study against a seed built without it.** Table 4.15 compares each study with a seed that does not contain it. The last two columns show what would have been reported had the study been left inside its own seed (circular): 0.54, 0.91 and 0.87 for M01, A02 and M06, against 0.09, 0.37 and 0.64 without them. The inflation is why the earlier "leave-one-study-out" figures of 0.78 to 0.99 were withdrawn.

**Table 4.15.** Agreement of each study with a seed built without it (Derived Calculation from Literature values; n = 1 to 19 shared risks per study; 6 tests in the Holm family)

| Study X | Role | n shared risks (X vs seed built from the other 4) | Spearman rho | Two-sided p | Holm p | n (circular) | rho if X is inside its own seed (circular, shown only as a warning) |
|---|---|--:|--:|--:|--:|--:|--:|
| M01 | seed | 13 | 0.09 | 0.765 | 1.000 | 18 | 0.54 |
| A02 | seed | 10 | 0.37 | 0.290 | 0.959 | 13 | 0.91 |
| M06 | seed | 9 | 0.64 | 0.066 | 0.329 | 15 | 0.87 |
| A14 | seed | 4 | 0.60 | not tested | - | 4 | 0.60 |
| A15 | seed | 2 |  | not tested | - | 2 | - |
| M10 | held-out | 19 | 0.28 | 0.240 | 0.959 | 19 | - |
| M15 | held-out | 11 | 0.63 | 0.045 | 0.267 | 11 | - |
| M14 | held-out | 13 | -0.18 | 0.549 | 1.000 | 13 | - |
| A10 | held-out | 2 |  | not tested | - | 2 | - |
| A21 | held-out | 1 |  | not tested | - | 1 | - |
| HAS25 | held-out | 1 |  | not tested | - | 1 | - |

Source: `analysis/out/s4_leave_one_study_out.csv`. For held-out studies the reference is the five-study seed, which does not contain them, so there is no circular column.

None of the six testable comparisons is significant after Holm correction over the six (smallest adjusted p 0.267, M15). M15's raw permutation p is 0.045 (the t-approximation in earlier documents gave 0.039); M06 is 0.066. Restricting the family to the three held-out studies, as the handoff did, the adjusted values computed from the printed raw p-values are 0.134 (M15), 0.479 (M10) and 0.549 (M14), still none below 0.05. A15 (n = 2), A10 (2), A21 (1) and HAS25 (1) share too few risks to test. The agreement of the three held-out surveys with the seed is therefore rho 0.28, 0.63 and -0.18: weak, low-powered and inconclusive. M14 is negative, and its basis, W/(5N), is not comparable in level with the others.

![Figure 4.8. Agreement with the seed built without the study (blue) and the circular value (grey) (Derived Calculation from Literature values; n = 11 studies; the n above each bar is the number of shared risks).](figures/ch4_s4_leave_one_study_out.png)

**Detectable agreement.** With 5 to 19 shared risks only large correlations could have been detected. The smallest absolute rho that reaches a two-sided permutation p of 0.05 is 0.52 at n = 15, 0.57 at 13, 0.62 at 11, 0.65 at 10, 0.70 at 9, 0.74 at 8, 0.79 at 7, 0.89 at 6 and only a perfect 1.00 at 5, and 0.46 at 19 (Table 3.8). Most overlaps in Table 4.14 are at or below 10, so only a rho of about 0.65 or more could have been called significant for a typical pair. The check is low-powered, and a non-significant result is neither evidence for nor against agreement.

**Kendall W.** Table 4.16 gives W for every complete block of at least three studies and at least five risks, 14 blocks in all.

**Table 4.16.** Kendall W over complete study-by-risk blocks (Derived Calculation from Literature values; m = 3 or 4 studies, n = 5 to 10 risks per block; 14 blocks; one-sided permutation p, 20,000 permutations; Holm over the 14 blocks, descriptive because blocks overlap)

| Studies (m) | Complete risks (n) | Kendall W | Permutation p | Holm p (14 blocks) |
|---|--:|--:|--:|--:|
| M01 M10 M14 | 10 | 0.488 | 0.126 | 1.000 |
| M01 M10 M15 | 9 | 0.539 | 0.079 | 0.871 |
| A02 M10 M14 | 7 | 0.429 | 0.278 | 1.000 |
| M01 A02 M10 | 7 | 0.733 | 0.010 | 0.122 |
| M01 M06 M10 | 6 | 0.467 | 0.231 | 1.000 |
| M01 M15 M14 | 6 | 0.289 | 0.571 | 1.000 |
| M10 M15 M14 | 6 | 0.441 | 0.275 | 1.000 |
| A02 M10 M15 | 5 | 0.889 | 0.004 | 0.059 |
| M01 A02 M14 | 5 | 0.200 | 0.717 | 1.000 |
| M01 A02 M15 | 5 | 0.638 | 0.083 | 0.871 |
| M01 M06 M15 | 5 | 0.467 | 0.252 | 1.000 |
| M01 M10 M15 M14 | 6 | 0.400 | 0.153 | 1.000 |
| M01 A02 M10 M14 | 5 | 0.263 | 0.411 | 1.000 |
| M01 A02 M10 M15 | 5 | 0.699 | 0.009 | 0.112 |

Source: `analysis/out/s4_kendall_w.csv`.

The block that the earlier analysis reported, M01, M10, M15 and M14 on six risks, gives W = 0.400 with permutation p = 0.153, the same conclusion as the chi-square p of 0.156: not distinguishable from chance. Two blocks that include A02 and M10 reach raw permutation p of 0.004 (A02, M10, M15; five risks; W = 0.889) and 0.009 (M01, A02, M10, M15; five risks; W = 0.699), but their Holm-adjusted p-values are 0.059 and 0.112, and the highest W values come from the blocks with the fewest risks, where a large W is easiest to obtain by chance and the 14 blocks use the same studies repeatedly. No block is significant after correction. W describes consensus on order among the studies in the block; it is not reliability.

**Summary of agreement.** The non-circular evidence is: agreement between studies on shared risks is weak (median rho 0.29), the raw p-values below 0.05 (two pairs, M10 with M15 and M06 with M15, and M15 against the seed) do not survive correction, and the held-out comparison is weak and inconclusive. The agreement that the earlier, circular calculations suggested (pooled rank against the seed 0.73; z order against the seed 0.40 and 0.53) does not appear when the seed studies are excluded from the reference: the held-out-only values are 0.08 and 0.09 (Handoff Section 8.3, quoted, not recomputed here).

## 4.9 RII uncertainty (S5)

S5 compares the spread of RII for the same risk across studies with the gaps between adjacent ranks. The spread is between-study, on unequal scales; it is not the sampling error of any survey.

**Table 4.17.** Spread of RII across studies, seeded risks with at least two seed studies (Derived Calculation from Literature values; n = 16 risks of 30; RII as printed, scales differ)

| Seed rank | Risk | Seed studies | Seed mean RII | Range of seed study means | All studies reporting | Min RII (all) | Max RII (all) | Range (all) |
|--:|---|--:|--:|--:|--:|--:|--:|--:|
| 1 | R-MAT | 3 | 0.7889 | 0.0328 | 7 | 0.508 | 0.810 | 0.302 |
| 3 | R-SKILL | 3 | 0.7831 | 0.0443 | 6 | 0.523 | 0.803 | 0.280 |
| 4 | R-PLAN | 2 | 0.7771 | 0.0278 | 6 | 0.475 | 0.874 | 0.399 |
| 5 | R-PAY | 3 | 0.7733 | 0.0047 | 5 | 0.716 | 0.776 | 0.060 |
| 6 | R-DIS | 2 | 0.7700 | 0.0400 | 2 | 0.750 | 0.790 | 0.040 |
| 7 | R-LAB | 3 | 0.7662 | 0.1015 | 5 | 0.660 | 0.825 | 0.165 |
| 9 | R-SITE | 2 | 0.7611 | 0.0201 | 2 | 0.751 | 0.771 | 0.020 |
| 10 | R-DES | 2 | 0.7585 | 0.0531 | 4 | 0.693 | 0.785 | 0.093 |
| 11 | R-RWK | 2 | 0.7561 | 0.0401 | 4 | 0.736 | 0.776 | 0.040 |
| 12 | R-TOOL | 2 | 0.7528 | 0.0145 | 5 | 0.435 | 0.760 | 0.325 |
| 18 | R-MGT | 2 | 0.7331 | 0.0482 | 3 | 0.520 | 0.757 | 0.237 |
| 20 | R-OVT | 2 | 0.7063 | 0.0374 | 3 | 0.688 | 0.725 | 0.037 |
| 21 | R-ACC | 2 | 0.7045 | 0.1090 | 4 | 0.455 | 0.759 | 0.304 |
| 24 | R-WX | 4 | 0.6934 | 0.1112 | 8 | 0.475 | 0.764 | 0.289 |
| 25 | R-COM | 2 | 0.6793 | 0.0014 | 4 | 0.518 | 0.682 | 0.164 |
| 26 | R-PRC | 2 | 0.6695 | 0.2390 | 2 | 0.550 | 0.789 | 0.239 |

Source: `analysis/out/s5_rii_spread_by_risk.csv`.

The median gap between adjacent seed ranks is 0.0034. For the 16 risks with two or more seed studies the median range of the study means is 0.040, and 15 of the 16 (94%) have a range larger than the median adjacent gap. The widest seed ranges are R-PRC 0.239 (A02 0.55, A14 0.789), R-WX 0.111 (four studies), R-ACC 0.109, R-LAB 0.101 and R-DES 0.053. Using all 11 studies, the median between-study standard deviation over the 26 risks reported by at least two studies is 0.082. The order inside the middle of the list, where the gaps are thousandths, is therefore finer than the studies disagree with each other.

![Figure 4.9. RII of each seeded risk in every study that reports it (marker per study, black tick = seed mean; scales differ) (Derived Calculation from Literature values; n = 30 seeded risks, 11 studies).](figures/ch4_s5_rii_spread.png)

Sampling error within a study is a separate and smaller component. The audit estimated about 0.03 for one M01 RII from that study's own counts, and the planning arithmetic of Table 3.7 gives 0.030 at N = 44 for an SD of one Likert point (Assumption). Against a median adjacent gap of 0.0034, that is roughly nine times larger. No standard error was computed for A02 and A15 (no counts or SDs) or for the other studies in this report; a within-study error draw (analysis A5, part ii) was planned but is not implemented in the analysis package, so the tiers above carry between-study uncertainty only.

## 4.10 Summary of results

**Table 4.18.** What each analysis shows, in the words the evidence allows (Derived Calculation; n as in each section)

| Section | Result | Wording to use |
|---|---|---|
| 4.2 | 30 seeded risks, 14 on one study, 16 unseeded; top six within 0.019 | the seed is an ordinal starting position |
| 4.3 | 12 Low, 6 Moderate, 0 High, 12 Extreme with the same class on both axes; median 6 of 30 levels change over 969 cut-off triples | level labels of seeded risks are artefacts of the rule and thresholds |
| 4.4 | level driven by p, not by delay; p x0.5 changes 6 of 7 levels | shows the rule's response, not site behaviour |
| 4.5 | impact edges change 0 levels but up to 7 classes; p edges change up to 7 levels | level labels depend on assumed edges |
| 4.6 | 2 to 24 of 30 classes change across variants; order of means more stable (Spearman 0.78 to 1.00) | the class depends on banding and on which studies are present |
| 4.7 | tau 0.78 under resampling; only R-MAT and R-SKILL are Tier 1 | at most coarse tiers; middle unresolved |
| 4.8 | median pairwise rho 0.29; none significant after Holm; held-out 0.28, 0.63, -0.18; W 0.40, p 0.15 | weak, low-powered, inconclusive |
| 4.9 | between-study range exceeds the adjacent gap for 15 of 16 risks | order inside the middle is finer than the data |

## 4.11 What this analysis does not show

- It does not validate the seed or show that it predicts anything. RII is importance, not probability or days, and no site data were used.
- It does not show that the seed order is wrong. The agreement check is low-powered; a non-significant correlation on 5 to 19 shared risks is compatible with real agreement and with none.
- It does not give independent evidence that the seed is corroborated. The only independent comparisons are the held-out studies (rho 0.28, 0.63, -0.18) and none survives correction.
- It does not show what drives delay in masonry on Indian sites. Ten of the eleven studies are not masonry-specific, the seed studies are general building or construction surveys, and one held-out study (A10) is infrastructure.
- It does not show that the matrix level of any real risk is stable or unstable. S1 and S2 use one illustrative case of seven risks with placeholder numbers; their counts describe that case and are not a sample.
- It does not make the bootstrap tiers confidence statements. Five clusters, uneven coverage (14 risks on one study), mapping uncertainty ignored and scale differences ignored mean the tiers understate uncertainty.
- It does not measure within-study sampling error beyond the M01 estimate; the third source of error, the single-coder mapping, has not been measured.
- It does not support the withdrawn claims: that weather is rated lower than the rest, that studies agree modestly, or that the pooled order agrees with the seed.
- It is a second look at data first examined on ten risks, so it is exploratory; the 38-risk library was defined after the first look.
- The planned expert survey, second-coder check and site data are the next evidence. Until they exist, the seed is a transparent default ordering and nothing more.
