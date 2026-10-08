# Appendix B. Risk library: all 46 risks

The risk library (`data/risk_library_masonry.json`) holds 46 candidate delay risks for one brick or block masonry activity: 38 from the original compilation and 8 added on 2026-10-08 (R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT). 38 are scoped to the activity and 8 to the project as a whole. "Seeded" means at least one direct survey row of a seed study maps to the risk, so the literature seed can place it at an ordinal tier; rank and class are those of `app.literature_seed.seed_table()` on the five seed studies (Derived Calculation, Assumption: five equal-count bands). "Unseeded" risks have no survey value; they stay off the matrix until probability and delay are entered, and carry the `seed_status` text from the library. Evidence IDs point to records in the evidence corpus (`Literature_Evidence_Package.xlsx`, `Research_Notes/`) and support that the risk exists, never its size. The masonry-specific form of the 8 added risks is labelled Expert Judgment, to be confirmed by the expert survey (Appendix F).

**Table B.1.** Library risks by category. Source: Derived Calculation from `data/risk_library_masonry.json`.

| Category | Risks |
|---|---|
| Labour | 13 |
| Management | 6 |
| Material | 6 |
| Design | 4 |
| Equipment | 3 |
| External | 3 |
| Financial | 3 |
| Quality | 2 |
| Safety | 2 |
| Site | 2 |
| Weather | 2 |

**Table B.2.** The 46 library risks. Source: `data/risk_library_masonry.json` (name, category, scope, evidence IDs: Literature); seed status: Derived Calculation from `data/literature_seed.json`.

| ID | Name | Category | Scope | Seed status | Evidence IDs |
|---|---|---|---|---|---|
| R-MAT | Brick / block / mortar material shortage or late delivery | Material | activity | seeded: rank 1 of 30, class 5, 3 studies | M01, M06 |
| R-TOOL | Tools and equipment delay | Equipment | activity | seeded: rank 12 of 30, class 4, 2 studies | M01 |
| R-LAB | Labour absenteeism or shortage | Labour | activity | seeded: rank 7 of 30, class 4, 3 studies | M01, M07, M15 |
| R-SKILL | Unskilled or unqualified labour | Labour | activity | seeded: rank 3 of 30, class 5, 3 studies | M15, M14 |
| R-PLAN | Poor planning or unrealistic scheduling | Management | activity | seeded: rank 4 of 30, class 5, 2 studies | M01 |
| R-SAFE | Unsafe conditions or work at height | Safety | activity | seeded: rank 2 of 30, class 5, 1 study | M01 |
| R-WX | Rain / monsoon stoppage | Weather | activity | seeded: rank 24 of 30, class 2, 4 studies | R08, M01 |
| R-RWK | Rework due to workmanship or defects | Quality | activity | seeded: rank 11 of 30, class 4, 2 studies | M03, M15 |
| R-PAY | Payment delay | Financial | activity | seeded: rank 5 of 30, class 5, 3 studies | M01 |
| R-DES | Design changes or incomplete documentation | Design | activity | seeded: rank 10 of 30, class 4, 2 studies | M06, M13 |
| R-SUP | Inadequate supervision or monitoring of workers | Labour | activity | seeded: rank 16 of 30, class 3, 1 study | M01, M10, M14 |
| R-MOT | Low motivation, morale or labour turnover | Labour | activity | seeded: rank 17 of 30, class 3, 1 study | M01, M10, M14 |
| R-INC | Inadequate wages or incentives | Labour | activity | seeded: rank 13 of 30, class 3, 1 study | M01, M10, M14 |
| R-OVT | Overtime and long working hours | Labour | activity | seeded: rank 20 of 30, class 2, 2 studies | M01, M06, M10 |
| R-FAT | Worker fatigue, age or personal problems | Labour | activity | seeded: rank 29 of 30, class 1, 1 study | A02, M10, M14 |
| R-COM | Poor communication or misunderstanding on site | Labour | activity | seeded: rank 25 of 30, class 1, 2 studies | A02, M01, M06, M10, M14 |
| R-DIS | Poor labour discipline or weak site leadership | Management | activity | seeded: rank 6 of 30, class 5, 2 studies | A15, M01, M06 |
| R-TRN | Inadequate training of workers | Labour | activity | unseeded: no survey RII value; enter probability and delay | M10 |
| R-PRD | Low labour productivity | Labour | activity | unseeded: no survey RII value; enter probability and delay | M15 |
| R-STR | Labour strikes or disputes | Labour | activity | seeded: rank 14 of 30, class 3, 1 study | M06 |
| R-ACC | Accidents and injuries on site | Safety | activity | seeded: rank 21 of 30, class 2, 2 studies | A02, M01, M10, M15 |
| R-MGT | Poor site management and coordination | Management | activity | seeded: rank 18 of 30, class 3, 2 studies | M01, M06, M15 |
| R-SUB | Subcontracting and contract-type problems | Management | activity | unseeded: no survey RII value; enter probability and delay | M10, M14 |
| R-CTR | Contractual disputes and claims | Management | project | seeded: rank 15 of 30, class 3, 1 study | M06, M15 |
| R-SCP | Unclear scope or inadequate project formulation | Design | project | seeded: rank 8 of 30, class 4, 1 study | M06 |
| R-CLI | Client decision delay or pressure | Management | project | unseeded: no survey RII value; enter probability and delay | M06, M14 |
| R-CST | Cost control and budget updating problems | Financial | project | seeded: rank 19 of 30, class 2, 1 study | M06 |
| R-QLT | Inspection and quality-approval delays | Quality | activity | unseeded: no survey RII value; enter probability and delay | M06, M10 |
| R-DEF | Defective or poor-quality material | Material | activity | unseeded: no survey RII value; enter probability and delay | M15 |
| R-SITE | Poor site access, clearance or conditions | Site | activity | seeded: rank 9 of 30, class 4, 2 studies | A02, M06, M10, M14 |
| R-STO | Poor material storage or handling | Material | activity | seeded: rank 23 of 30, class 2, 1 study | A02, M10 |
| R-PRC | Material price escalation | Material | activity | seeded: rank 26 of 30, class 1, 2 studies | A02, A14 |
| R-WAT | Water shortage | Material | activity | seeded: rank 28 of 30, class 1, 1 study | A02 |
| R-MTH | Construction method or design complexity | Design | activity | seeded: rank 22 of 30, class 2, 1 study | M01, M10, M14, M15 |
| R-ECO | Economic conditions, inflation or interest rates | External | project | seeded: rank 27 of 30, class 1, 1 study | M06, M10 |
| R-GOV | Government policies or approvals | External | project | unseeded: no survey RII value; enter probability and delay | M10 |
| R-SOC | Social or community environment | External | project | seeded: rank 30 of 30, class 1, 1 study | M06 |
| R-FIN | Contractor financial difficulties | Financial | project | unseeded: no survey RII value; enter probability and delay | A21 |
| R-FRONT | Work front not released (slab not de-shuttered, props or debris in place, frame not handed over) | Site | activity | unseeded: no survey RII value; enter probability and delay | D01, P1-05 |
| R-VT | Hoist or material lift unavailable or broken (bricks and mortar to upper floors) | Equipment | activity | unseeded: no survey RII value; enter probability and delay | P1-02, P3-02 |
| R-MORT | Mortar materials short or poor (cement, sand, or mixer down) | Material | activity | unseeded: no survey RII value; enter probability and delay | A02, D01 |
| R-GPAY | Gang wages or labour-contractor running bill overdue | Labour | activity | unseeded: no survey RII value; enter probability and delay | A08, D21 |
| R-OPEN | Openings, lintels, door/window frames and MEP sleeves not coordinated | Design | activity | unseeded: no survey RII value; enter probability and delay | M10, M06 |
| R-SCAF | Scaffolding not available, not erected or not passed safe | Equipment | activity | unseeded: no survey RII value; enter probability and delay | P1-05, P3-01 |
| R-FEST | Festival, harvest or election season exodus of the migrant gang | Labour | activity | unseeded: no survey RII value; enter probability and delay | A21, A03, A08 |
| R-HEAT | Peak-summer heat cuts effective working hours | Weather | activity | unseeded: no survey RII value; enter probability and delay | P2-08, M15, P2-06 |

Unseeded risks (16): R-TRN, R-PRD, R-SUB, R-CLI, R-QLT, R-DEF, R-GOV, R-FIN, R-FRONT, R-VT, R-MORT, R-GPAY, R-OPEN, R-SCAF, R-FEST, R-HEAT.
