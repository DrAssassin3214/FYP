| Rule | Condition (in words) | Formal condition | Risk flagged | Level | Pri. | Source | Conf. |
|---|---|---|---|---|---|---|---|
| RL-LAB | Required workers exceed workers available | `required_workers` > `available_workers` | R-LAB | elevated | 0 | Assumption | Moderate |
| RL-MAT | Stock on site runs out before a new delivery can arrive (for the material with the longest lead time) | `material_stock_days` <= `material_lead_time_days` | R-MAT | elevated | 1 | Assumption | Moderate |
| RL-MAT2 | Stock on site covers fewer days than the planned duration | `material_stock_days` < `planned_duration_days` | R-MAT | normal | 0 | Assumption | Low |
| RL-TOOL | Tools or equipment shortage expected | `tools_shortage` = true | R-TOOL | elevated | 0 | Assumption | Low |
| RL-WX | Activity period overlaps the monsoon / rainy season | `monsoon_overlap` = true | R-WX | normal | 0 | Assumption | Moderate |
| RL-HGT | Masonry is done at height and scaffolding is not ready | `work_at_height` = true AND `scaffolding_ready` = false | R-SAFE | elevated | 0 | Assumption | Low |
| RL-PAY | Payment delays occurred previously or are expected | `payment_delay_expected` = true | R-PAY | elevated | 0 | Assumption | Low |
| RL-DES | Drawings or details are incomplete | `design_incomplete` = true | R-DES | elevated | 0 | Assumption | Low |
| RL-RWK | Rework was frequent in earlier work on this site or crew | `prior_rework_history` = true | R-RWK | elevated | 0 | Assumption | Low |
| RL-PLAN | Planner or site engineer judges the programme faster than the gang can achieve | `schedule_compressed` = true | R-PLAN | elevated | 0 | Assumption | Low |
| RL-SKILL | Skilled masons are fewer than needed | `skilled_masons_short` = true | R-SKILL | elevated | 0 | Assumption | Low |
| RL-WX2 | Monsoon overlaps the activity and external walls are in scope | `monsoon_overlap` = true AND `external_walls_in_scope` = true | R-WX | elevated | 1 | Assumption | Low |
| RL-PACE | Planned daily output is higher than the output achieved last week | `planned_daily_output` > `achieved_daily_output_last_week` | R-PLAN | elevated | 0 | Assumption | Low |
| RL-FRONT | Floors or walls planned for the next 7 days are not de-propped, cleared and handed over | `work_front_ready` = false | R-FRONT | elevated | 0 | Assumption | Low |
| RL-VT | Masonry is above the ground floor and no hoist or material lift is available | `masonry_floor_level` >= 1 AND `hoist_available` = false | R-VT | elevated | 0 | Assumption | Low |
| RL-SCAF | Scaffolding is not ready | `scaffolding_ready` = false | R-SCAF | elevated | 0 | Assumption | Low |
| RL-MORT | Sand or cement stock runs out before a new delivery can arrive | `sand_cement_stock_days` <= `sand_cement_lead_time_days` | R-MORT | elevated | 0 | Assumption | Low |
| RL-GPAY | The gang's weekly payment or the labour contractor's bill is overdue | `gang_payment_overdue` = true | R-GPAY | elevated | 0 | Assumption | Low |
| RL-OPEN | Door/window frames, MEP sleeve layout or lintel-level plan is not ready | `frames_on_site` = false OR `mep_sleeve_layout_marked` = false OR `lintel_level_plan_issued` = false | R-OPEN | elevated | 0 | Assumption | Low |
| RL-FEST | A major festival, harvest or election falls inside the activity window | `festival_or_harvest_in_window` = true | R-FEST | normal | 0 | Assumption | Low |
| RL-FEST2 | A festival, harvest or election falls inside the window and the gang is mostly migrant | `festival_or_harvest_in_window` = true AND `gang_mostly_migrant` = true | R-FEST | elevated | 1 | Assumption | Low |
| RL-HEAT | The activity overlaps peak summer | `summer_overlap` = true | R-HEAT | normal | 0 | Assumption | Low |
