# Appendix C. The 22 site-fact rules

The rule base (`data/rules_masonry.json`) turns site facts the engineer already knows (Yes / No / Unknown, or a number entered by the user) into a flag on a library risk. A rule is a logical condition on facts. It contains no probability, no delay and no numeric threshold other than comparisons between two entered facts or a Yes/No fact. All 22 rules carry Source = Assumption (a logical condition proposed by the team); the evidence IDs support that the risk exists, not the rule's size or trigger. Level "elevated" marks an observed shortfall; level "normal" marks the risk as relevant only. Where several rules fire on one risk the highest priority wins; equal priority with different levels is reported as a conflict (guard test G-8). A rule whose facts are missing is shown as "not evaluable", never guessed. For a risk placed from the literature seed, an "elevated" flag raises its probability class by one (cap 5); that step is an Assumption of the tool (register item AS-11, Appendix H). Rule levels: 18 elevated, 4 normal.

**Table C.1.** The 22 rules: condition, flagged risk, level, priority and evidence. Source: `data/rules_masonry.json`. Conditions are rendered from the rule's `all_of` / `any_of` fields; "= yes" is a Boolean fact set to true.

| Rule | Flags risk | Condition | Level | Priority | Source | Evidence IDs | Confidence |
|---|---|---|---|---|---|---|---|
| RL-LAB | R-LAB | required_workers > available_workers | elevated | 0 | Assumption | M01, M07 | Moderate |
| RL-MAT | R-MAT | material_stock_days <= material_lead_time_days | elevated | 1 | Assumption | M01, M06 | Moderate |
| RL-MAT2 | R-MAT | material_stock_days < planned_duration_days | normal | 0 | Assumption | M01 | Low |
| RL-TOOL | R-TOOL | tools_shortage = yes | elevated | 0 | Assumption | M01 | Low |
| RL-WX | R-WX | monsoon_overlap = yes | normal | 0 | Assumption | R08, M01 | Moderate |
| RL-HGT | R-SAFE | work_at_height = yes AND scaffolding_ready = no | elevated | 0 | Assumption | M01 | Low |
| RL-PAY | R-PAY | payment_delay_expected = yes | elevated | 0 | Assumption | M01 | Low |
| RL-DES | R-DES | design_incomplete = yes | elevated | 0 | Assumption | M06, M13 | Low |
| RL-RWK | R-RWK | prior_rework_history = yes | elevated | 0 | Assumption | M03, M15 | Low |
| RL-PLAN | R-PLAN | schedule_compressed = yes | elevated | 0 | Assumption | M01 | Low |
| RL-SKILL | R-SKILL | skilled_masons_short = yes | elevated | 0 | Assumption | M15 | Low |
| RL-WX2 | R-WX | monsoon_overlap = yes AND external_walls_in_scope = yes | elevated | 1 | Assumption | A09, P1-05 | Low |
| RL-PACE | R-PLAN | planned_daily_output > achieved_daily_output_last_week | elevated | 0 | Assumption | M01 | Low |
| RL-FRONT | R-FRONT | work_front_ready = no | elevated | 0 | Assumption | D01, P1-05 | Low |
| RL-VT | R-VT | masonry_floor_level >= 1 AND hoist_available = no | elevated | 0 | Assumption | P1-02, P3-02 | Low |
| RL-SCAF | R-SCAF | scaffolding_ready = no | elevated | 0 | Assumption | P1-05, P3-01 | Low |
| RL-MORT | R-MORT | sand_cement_stock_days <= sand_cement_lead_time_days | elevated | 0 | Assumption | A02, D01 | Low |
| RL-GPAY | R-GPAY | gang_payment_overdue = yes | elevated | 0 | Assumption | A08, D21 | Low |
| RL-OPEN | R-OPEN | any of: frames_on_site = no OR mep_sleeve_layout_marked = no OR lintel_level_plan_issued = no | elevated | 0 | Assumption | M10, M06 | Low |
| RL-FEST | R-FEST | festival_or_harvest_in_window = yes | normal | 0 | Assumption | A21, A03, A08 | Low |
| RL-FEST2 | R-FEST | festival_or_harvest_in_window = yes AND gang_mostly_migrant = yes | elevated | 1 | Assumption | A21, A03, A08 | Low |
| RL-HEAT | R-HEAT | summer_overlap = yes | normal | 0 | Assumption | P2-08, M15 | Low |

**Table C.2.** Description and rationale text of each rule as stored in the file. Source: `data/rules_masonry.json`.

| Rule | Description | Rationale (as stored) |
|---|---|---|
| RL-LAB | Required workers exceed workers available | Logical shortfall condition; carries no numeric threshold. Risk existence: M01, M07. |
| RL-MAT | Stock on site runs out before a new delivery can arrive (for the material with the longest lead time) | Logical stock-out condition: stock days at or below the lead time leave no margin (a tie is a stock-out risk). Carries no numeric threshold. Risk existence: M01, M06. |
| RL-MAT2 | Stock on site covers fewer days than the planned duration | Restocking is required during the activity, so the risk is relevant; it is not raised to elevated by this fact alone. Whether it fails depends on lead time (see RL-MAT, which wins when both fire). |
| RL-TOOL | Tools or equipment shortage expected | User-declared condition. |
| RL-WX | Activity period overlaps the monsoon / rainy season | Calendar overlap declared by the user. Internal walls can continue in rain, so monsoon alone marks the risk as relevant only (see RL-WX2 for external walls). |
| RL-HGT | Masonry is done at height and scaffolding is not ready | Work at height alone applies to almost every superstructure wall, so it is raised only when scaffolding is not ready. M01 ranks working at heights among the listed factors. |
| RL-PAY | Payment delays occurred previously or are expected | User-declared condition. |
| RL-DES | Drawings or details are incomplete | User-declared condition. |
| RL-RWK | Rework was frequent in earlier work on this site or crew | User-declared condition. |
| RL-PLAN | Planner or site engineer judges the programme faster than the gang can achieve | User-declared (subjective) condition. See RL-PACE for the checkable form. |
| RL-SKILL | Skilled masons are fewer than needed | User-declared condition. |
| RL-WX2 | Monsoon overlaps the activity and external walls are in scope | Logical condition declared by the user; external walls are the work that rain stops. Risk existence: A09 (Kolkata monsoon), P1-05. |
| RL-PACE | Planned daily output is higher than the output achieved last week | Checkable form of RL-PLAN: both facts are User Input in the same unit (the user chooses it once); no norm is used. |
| RL-FRONT | Floors or walls planned for the next 7 days are not de-propped, cleared and handed over | User-declared condition. Risk existence: D01, P1-05. Masonry-specific form: Expert Judgment, to be confirmed by the expert survey. |
| RL-VT | Masonry is above the ground floor and no hoist or material lift is available | Floor 0 is the ground floor, so the only number is the floor index 1. Risk existence (related): P1-02, P3-02. Expert Judgment, to be confirmed by the expert survey. |
| RL-SCAF | Scaffolding is not ready | User-declared condition. Risk existence: P1-05, P3-01. Expert Judgment, to be confirmed by the expert survey. |
| RL-MORT | Sand or cement stock runs out before a new delivery can arrive | Same logical stock-out condition as RL-MAT, for mortar materials. Risk existence: A02, D01. |
| RL-GPAY | The gang's weekly payment or the labour contractor's bill is overdue | User-declared condition. Risk existence: A08 (abstract only), D21. |
| RL-OPEN | Door/window frames, MEP sleeve layout or lintel-level plan is not ready | Any one of the three being 'No' fires the rule. If one is left blank and the others are 'Yes', the rule is reported as not evaluable. Risk existence (related): M10, M06. |
| RL-FEST | A major festival, harvest or election falls inside the activity window | Calendar fact declared by the user: the risk is relevant only. Expert Judgment (to be confirmed by the expert survey) for the Indian form. |
| RL-FEST2 | A festival, harvest or election falls inside the window and the gang is mostly migrant | Raised above RL-FEST (priority 1) when the gang is mostly migrant. Expert Judgment, to be confirmed by the expert survey. |
| RL-HEAT | The activity overlaps peak summer | Calendar fact declared by the user: the risk is relevant only. Heat figures from brick-making (P2-06) are not used. |
