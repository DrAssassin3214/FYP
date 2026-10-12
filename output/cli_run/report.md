# Risk assessment report: Brick masonry, ground-floor walls

## 1. Executive summary

- Baseline duration T0 = 15.38 days (Derived Calculation).
- Simulated expected duration 19.18 days; expected delay 3.80 days; P80 21.72, P90 23.37, P95 24.70 days.
- Probability of exceeding the 18.0-day deadline under the stated assumptions: 60.5%.
- Expected delay cost 68,305 INR (P90 150,603).
- Decision-support statement: Under the stated criterion and assumptions, 'Buffer stock' is preferred among the 5 admissible options evaluated (total expected cost 66841 INR, P90 duration 22.3 days).
- This is a probabilistic simulation under stated assumptions, not a prediction validated against project outcomes.

## 2. Activity description

| Field | Value | Source |
|---|---|---|
| ID | MAS-01 | |
| Name | Brick masonry, ground-floor walls | |
| Baseline duration (days) | 15.38 | Derived Calculation  |
| Quantity | 1,200.00 m2 | |
| Deadline (days) | 18.00 | Assumption |

## 3. Risk register

| ID | Risk | Status | p | p source | Delay distribution (a, m, b) days | Dist. source | Direct cost | Evidence |
|---|---|---|---|---|---|---|---|---|
| R-MAT | Brick / material shortage | literature-supported | 0.30 | Assumption | pert(1.0, 3.0, 8.0) | Assumption | 0 (Assumption) | M01, M06 |
| R-LAB | Labour absenteeism / shortage | literature-supported | 0.35 | Assumption | pert(1.0, 2.0, 6.0) | Assumption | 0 (Assumption) | M01, M07, M15 |
| R-RWK | Rework due to workmanship | literature-supported | 0.25 | Assumption | pert(1.0, 2.0, 5.0) | Assumption | 8,000 (Assumption) | M03, M15 |
| R-WX | Rain / monsoon stoppage | literature-supported | 0.20 | Assumption | pert(1.0, 2.0, 7.0) | Assumption | 0 (Assumption) | R08 |
| R-PLAN | Poor planning or unrealistic scheduling | literature-supported | 0.15 | Assumption | pert(1.0, 2.0, 4.0) | Assumption | 0 (Assumption) | M01 |

## 4. Literature evidence

- **M01**: Karthik, Rao (2019). Essential factors responsible for loss of labour productivity in building construction in India. Chulalongkorn-hosted PDF; access statement NC
- **M02**: AlJassmi, Abduljalil, Philip (2023). Towards self-recovering construction schedules (NN productivity forecasting). J. Asian Architecture and Building Eng.; Open Access statement present
- **M03**: Mahamid (2020). Relationship between rework and labor productivity in building construction projects. Access statement NC
- **M06**: Dixit, Mandal, Thanikal, Saurabh (NC). Significant factors affecting construction productivity using RII, Indian construction industry. Open access / Creative Commons statement present; year NC
- **M07**: Gupta, Hasan, Jain, Jha (2018). Site amenities and workers' welfare factors, Indian construction projects. ASCE; open-access status NOT stated in PDF
- **M15**: (authors NC) (2021). Study of delays in constructions, private companies in Brasilia. Open Access CC statement; year per filename
- **R08**: Singh et al. (2025). Construction Delays Due to Weather in Cold Regions: SEM + ANN. Buildings 15(11):1916

## 5-6. Probability and impact assessment

Probability p is an event probability during execution of this activity, not an expert score. Impact is the conditional delay distribution in days. Survey rankings (RII) in the cited papers rank importance; they are not probabilities and were not converted to p.

## 7. Risk matrix (prioritisation only)

| Risk | p | p class | Impact class | Score | Level |
|---|---|---|---|---|---|
| R-MAT | 0.30 | 2 | 5 | 10 | Moderate |
| R-LAB | 0.35 | 2 | 4 | 8 | Moderate |
| R-RWK | 0.25 | 2 | 4 | 8 | Moderate |
| R-WX | 0.20 | 2 | 4 | 8 | Moderate |
| R-PLAN | 0.15 | 1 | 4 | 4 | Low |

Matrix bins and thresholds are editable assumptions. The level is not used in the simulation or in EMV.

## 8. Delay distribution assumptions

Delay given occurrence follows the listed distribution; Beta-PERT shape weight lambda = 4 unless stated. Occurrence is Bernoulli(p) per risk.

## 9. Monte Carlo methodology

T = T0 + sum(I_i D_i); I_i ~ Bernoulli(p_i); independent by default. n = 10,000 iterations; seed = 20260927; common random numbers across scenarios; percentiles by empirical quantile with distribution-free 95% intervals.

## 10. Simulation results

| Statistic | Value (days) |
|---|---|
| min | 13.40 |
| mean | 19.18 |
| median | 18.85 |
| std | 3.07 |
| max | 32.62 |
| P10 | 15.42 (95% CI 15.36-15.50) |
| P50 | 18.85 (95% CI 18.78-18.93) |
| P80 | 21.72 (95% CI 21.61-21.84) |
| P85 | 22.52 (95% CI 22.40-22.62) |
| P90 | 23.37 (95% CI 23.26-23.50) |
| P95 | 24.70 (95% CI 24.54-24.88) |
| Standard error of mean | 0.031 |
| P(T > deadline) | 0.605 |
| P(delay > 2 d) | 0.682 |
| P(delay > 5 d) | 0.323 |

## 11. Sensitivity analysis

Spearman rank correlation of each risk's delay with total delay (descriptive, not causal):

| Risk | Spearman rho | Mean contribution (days) | Share of expected delay |
|---|---|---|---|
| R-MAT | 0.55 | 1.07 | 28.1% |
| R-LAB | 0.42 | 0.87 | 22.9% |
| LATENT_PRODUCTIVITY | 0.40 | 0.43 | 11.3% |
| R-RWK | 0.35 | 0.59 | 15.4% |
| R-WX | 0.33 | 0.53 | 13.9% |
| R-PLAN | 0.25 | 0.32 | 8.4% |

## 12-13. Monetary impact and EMV

Cost per delay day = 15,000 INR (Assumption).

| Risk | p | E[delay if occurs] | Conditional cost | Event EMV |
|---|---|---|---|---|
| R-MAT | 0.30 | 3.50 | 52,500 | 15,750 |
| R-LAB | 0.35 | 2.50 | 37,500 | 13,125 |
| R-RWK | 0.25 | 2.33 | 43,000 | 10,750 |
| R-WX | 0.20 | 2.67 | 40,000 | 8,000 |
| R-PLAN | 0.15 | 2.17 | 32,500 | 4,875 |

Sum of event EMV = 52,500; simulated expected cost = 68,305 INR. They agree in expectation only for independent, additive risks with a linear cost model.

## 14-16. Mitigation alternatives, residual risk and post-mitigation simulation

| Option | Mitigations | Cost | Residual E[cost] | TEC | E[duration] | P90 | P(T>deadline) | Admissible | Note |
|---|---|---|---|---|---|---|---|---|---|
| Accept (no response) | - | 0 | 68,305 | 68,305 | 19.18 | 23.37 | 0.605 | True |  |
| Buffer stock | M-A | 12,000 | 54,841 | 66,841 | 18.46 | 22.26 | 0.516 | True |  |
| Standby crew | M-B | 25,000 | 60,062 | 85,062 | 18.75 | 22.69 | 0.550 | True |  |
| Quality checks | M-C | 9,000 | 61,733 | 70,733 | 18.88 | 22.97 | 0.567 | True |  |
| All three | M-A, M-B, M-C | 46,000 | 40,358 | 86,358 | 17.73 | 20.97 | 0.395 | True |  |

- **M-A** (mitigate) targets R-MAT: Hold a buffer stock of bricks on site. Mechanism: Reduces the chance of a stock-out during the activity. Effect source: p_after = Expert Judgment; delay_after = unchanged. Evidence: M01.
- **M-B** (mitigate) targets R-LAB: Standby crew. Mechanism: Backfill labour to shorten a shortage delay. Effect source: p_after = unchanged; delay_after = Expert Judgment. Evidence: M02.
- **M-C** (mitigate) targets R-RWK: Supervisor quality checks each course. Mechanism: Fewer rejected panels. Effect source: p_after = Expert Judgment; delay_after = unchanged. Evidence: M03.

## 17. Decision analysis

**Rule used.** Criterion: minimum total expected cost  TEC = C_mitigation + E[C_residual]. Options evaluated: 5. Constraints: deadline-probability limit = None, mitigation budget = None. Options that are infeasible or violate a constraint are removed before ranking.

**Result.** Under the stated criterion and assumptions, 'Buffer stock' is preferred among the 5 admissible options evaluated (total expected cost 66841 INR, P90 duration 22.3 days).

*Result depends on user/expert inputs marked as assumptions; it is not a claim of optimality.*

## 18. Assumptions and non-literature inputs

| Input | Value | Source | Note |
|---|---|---|---|
| [activity].deadline_days | 18.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][0].p | 0.3 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][0].direct_cost_if_occurs | 0.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][1].p | 0.35 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][1].direct_cost_if_occurs | 0.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][2].p | 0.25 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][2].direct_cost_if_occurs | 8000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][3].p | 0.2 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][3].direct_cost_if_occurs | 0.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][4].p | 0.15 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [risks][4].direct_cost_if_occurs | 0.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [cost].cost_per_delay_day | 15000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [cost].ld_per_day_after_deadline | 5000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [mitigations][0].cost | 12000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [mitigations][0].p_after | 0.1 | Expert Judgment | EXPERT JUDGMENT REQUIRED |
| [mitigations][1].cost | 25000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [mitigations][2].cost | 9000.0 | Assumption | ILLUSTRATIVE placeholder, not evidence |
| [mitigations][2].p_after | 0.12 | Expert Judgment | EXPERT JUDGMENT REQUIRED |

## 19. Limitations

- Probabilities, delay ranges and mitigation effects are subjective unless a source is shown; results inherit that uncertainty.
- Risks are treated as independent and delays as additive unless a correlation is specified; interacting risks can widen the tail.
- Cost per delay day is treated as constant.
- No back-testing against actual project outcomes has been performed, so outputs are simulation results, not validated predictions.

## 20. Evidence references

- M01: Karthik, Rao (2019). Essential factors responsible for loss of labour productivity in building construction in India. Chulalongkorn-hosted PDF; access statement NC
- M02: AlJassmi, Abduljalil, Philip (2023). Towards self-recovering construction schedules (NN productivity forecasting). J. Asian Architecture and Building Eng.; Open Access statement present
- M03: Mahamid (2020). Relationship between rework and labor productivity in building construction projects. Access statement NC
- M06: Dixit, Mandal, Thanikal, Saurabh (NC). Significant factors affecting construction productivity using RII, Indian construction industry. Open access / Creative Commons statement present; year NC
- M07: Gupta, Hasan, Jain, Jha (2018). Site amenities and workers' welfare factors, Indian construction projects. ASCE; open-access status NOT stated in PDF
- M15: (authors NC) (2021). Study of delays in constructions, private companies in Brasilia. Open Access CC statement; year per filename
- R08: Singh et al. (2025). Construction Delays Due to Weather in Cold Regions: SEM + ANN. Buildings 15(11):1916
