# Scenario files (all ILLUSTRATIVE)

Ten case files built from the built-in analysis example. Every number is a placeholder (Source: Assumption), not evidence and not site data; they show how the model's outputs move when inputs move. Open a file with **Open** in the GUI, or run `python -m app.cli analyze <file> --out out/`.

| Scenario | What changes | High+Extreme / Moderate / Low | Mean, P50, P90 duration (d) | P(finish after deadline) | Command | Preferred option |
|---|---|---|---|---|---|---|
| S01_baseline | Baseline: the built-in ILLUSTRATIVE analysis example, unchanged. | 1 / 5 / 1 | 21.13, 20.9, 25.64 | 0.5981 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| S02_material_crisis | Brick supply crisis: R-MAT probability 0.8, longer worst-case delay, no stock on site. | 1 / 5 / 1 | 22.73, 22.54, 27.49 | 0.7651 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| S03_labour_shortage | Labour shortage: only 3 of 6 workers available; R-LAB 0.7, R-SKILL 0.5. | 3 / 3 / 1 | 22.66, 22.42, 27.2 | 0.7622 | AUTHORIZE MITIGATION | O-M-BUF+M-COV+M-QC |
| S04_heavy_monsoon | Heavy monsoon: R-WX probability 0.6 and delay 2 / 5 / 10 days. | 2 / 4 / 1 | 23.79, 23.67, 29.39 | 0.7958 | AUTHORIZE MITIGATION | O-M-BUF+M-COV+M-QC |
| S05_well_managed_site | Well-managed site: every risk probability scaled by 0.4. | 0 / 1 / 6 | 18.05, 17.58, 21.38 | 0.1931 | ACCEPT RISK | ACCEPT |
| S06_everything_goes_wrong | Everything goes wrong: every probability and every delay scaled by 1.5 (p capped at 0.95). | 3 / 3 / 1 | 27.55, 27.36, 34.44 | 0.9274 | AUTHORIZE MITIGATION | O-M-BUF+M-COV+M-QC |
| S07_tight_deadline_high_penalty | Tight deadline (17 days) with a high liquidated-damages rate (20,000 per day). | 1 / 5 / 1 | 21.13, 20.9, 25.64 | 0.8975 | AUTHORIZE MITIGATION | O-M-BUF+M-COV+M-QC |
| S08_cheap_delay | Delay is cheap: cost per delay day 800 and damages 500 per day. | 1 / 5 / 1 | 21.13, 20.9, 25.64 | 0.5981 | ACCEPT RISK | ACCEPT |
| S09_expensive_responses | Every candidate response costs four times as much as in the baseline. | 1 / 5 / 1 | 21.13, 20.9, 25.64 | 0.5981 | ACCEPT RISK | ACCEPT |
| S10_relaxed_deadline | Relaxed deadline (30 days): the planned duration is 16 days. | 1 / 5 / 1 | 21.13, 20.9, 25.64 | 0.0096 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |

## Same case, different random seeds (simulation noise only)

| Seed | Mean (d) | P50 (d) | P90 (d) | P(after deadline) | Command | Preferred option |
|---|---|---|---|---|---|---|
| 1 | 21.15 | 20.9 | 25.56 | 0.6036 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| 2 | 21.15 | 20.93 | 25.58 | 0.6072 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| 3 | 21.16 | 20.9 | 25.55 | 0.6079 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| 4 | 21.1 | 20.8 | 25.49 | 0.5956 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| 5 | 21.14 | 20.89 | 25.52 | 0.6042 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |
| 12345 | 21.13 | 20.9 | 25.64 | 0.5981 | AUTHORIZE MITIGATION | O-M-BUF+M-QC |

Source of every number in the tables: Derived Calculation from the ILLUSTRATIVE inputs in the case files (10,000 simulated runs per case, seed 12345 unless stated).
