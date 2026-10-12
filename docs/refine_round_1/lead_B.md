# Lead B findings, round 1 (GUI and usability, audit only)

Method: I drove the app in the browser (masonry-gui, port 8766) myself: added all library risks, entered p and delay, set duration and impact edges, switched the ranking basis, searched evidence, opened Export and POSTed the live case to /api/report, /api/register-csv and /api/report-html. Workers B2 and B3 did code-reading audits (their rows are marked "code-read" = line numbers checked by the worker, not re-run by me unless marked VERIFIED). B1 and B4 were done by me. Console: no errors. Network: all 200, no failures. Server stopped.

Notes on the brief: the library has 46 risks (not 38); 38 is the count the "all studies" basis can seed (37 + 1 entered in my run, 8 unseeded). Doc counts should say which.

## Verified in the running app

| ID | Sev | Where | What is wrong | Evidence | Proposed fix | Conf | User decision |
|---|---|---|---|---|---|---|---|
| B-01 | high | app.css:130 `body{min-width:380px}`, topbar nowrap (app.css:158-188), no breakpoint below 760px | Page does not fit a phone: at 375 px emulation the layout width was 496 px (scrollWidth 496 vs 375) on case, risks and matrix. VERIFIED | resize_window 375x812, read scrollWidth/innerWidth | Remove min-width; wrap or collapse the topbar below 760px | high | no |
| B-02 | high | app.css:667 `.nav-label{display:none}`; app.js:69,72 | At 1180 px and below the rail links have no accessible name (label display:none, icon aria-hidden, no aria-label). VERIFIED at 496 px layout: display none, aria-label none | JS query of #rail a | Add aria-label "N. Title" to each link and Settings button | high | no |
| B-03 | high | js/screens/risks.js:159 (lede) vs matrix behaviour | Register lede says a risk "is placed on the matrix once both [p and delay] are entered", but 29-37 library risks with no numbers are placed on the matrix as literature tiers (toast app.js:414 says so). Contradictory first-read text | Risks screen after Add all: KPI "Literature tier 30", matrix shows chips | Reword: "assessed level once both are entered; library risks without numbers show a literature tier (ordinal, Assumption)" | high | no |
| B-04 | high | Tags default off (app.js:39-43, README_GUI.md:71) | Source pickers and per-field ILLUSTRATIVE notes are hidden by default, so on a fresh start a number's Source is not visible while entering it (Source still stored: selects held "User Input"). Conflicts with QUALITY_BAR item 5 "Source labels present" at the point of entry. VERIFIED | Fresh load: toolbar shows "Tags: off"; p/delay Source selects exist but are hidden | Default Tags to on, or always show Source next to any entered number | high | yes (design choice made earlier by user per README) |
| B-05 | high | js/screens/analysis.js (nav item 5 "Cost, options & decision", app.js:22) | Step 5 "Decide / Cost, options & decision" is in the live nav although the lean-refactor memory says cost/decision screens were dropped, and Handoff 8.14 says they are "not in the navigation". Open scope question, not decided by agents. Also analysis.js:118 labels it "Step 7" while Export is also Step 7 (nav says 5) | Rail lists 7 items; B3 read analysis.js:118 and report.js:14 | Supervisor to decide keep/hide; fix step number to 5 either way | high | yes |
| B-06 | med | matrix screen, impact-axis caption | Garbled text before edges are entered: "Impact edges not entered of planned duration · Source: not given". VERIFIED | Matrix screen text (ref_3895) | "Impact edges not entered yet (Source: not given)" | high | no |
| B-07 | med | Matrix empty prerequisite | With 1 risk entered and duration blank the Notes list says "risk matrix not computed: the planned activity duration is not entered" but KPI/summary gives no pointer to where; edges live behind an unlabeled "Impact class thresholds" icon button (ref_3354) in the page header. User must find a hidden popover to place any entered-number risk | Matrix screen at start | Show an inline "Enter duration (step 1) and impact edges" prompt with a link/button | med | no |
| B-08 | med | library data (R-WX description, data/risk_library_masonry.json; shown on Risks screen) | Text "Building studies in the notes rank weather below labour and material." is the withdrawn weather claim (Handoff 8.6/8.11 F09). VERIFIED in rendered library | Risks > Library > R-WX | Data owner (Lead C) to delete the sentence | high | no (file is Lead C's) |
| B-09 | med | Library cards | "NO SURVEY VALUE" tag shown on risks whose text cites an RII (e.g. R-PRD "RII 0.73", R-TRN "RII 0.459", R-GOV "RII 0.698", R-FIN "RII 0.777"). Reads as contradictory | Library listing | Rename to "not in the ranking" or explain (outcome/not comparable) | med | no |
| B-10 | med | Export CSV (register.csv) | Literature-tier rows carry p_class, impact_class and score (e.g. 3,3,9) with blank level and no tier column marker except `tier`/note text; a spreadsheet reader can read score 9 as assessed. Also floats unrounded (5.666666666666667) while screen/md show 5.67. VERIFIED via /api/register-csv | R-TOOL row vs R-MAT row | Blank p_class/impact_class/score for tier rows or add explicit `basis` column filter note; round to 2 dp | med | no (engine file, Lead A) |
| B-11 | med | Export report.html | report.html text contains "ordinal" once and no ILLUSTRATIVE (correct for a non-illustrative case); register.md and screen preview carry the ordinal-only and tier notes. Screen, md and CSV numbers agreed (R-MAT p 0.4, 2/5/12, e-delay 5.67, p3 x i3 = 9 Moderate; 38 placed, 37 tier, 1 entered). No mismatch found in numbers. VERIFIED | POST /api/report, /api/register-csv, /api/report-html | none (record as pass) | med | no |
| B-12 | low | Evidence screen | Evidence count 4,447 records in the corpus vs 3,975 in memory notes and "three versions" of corpus size in Handoff 8.9; also "NC" and "depth" shown without explanation. VERIFIED count | Evidence screen header | Lead D to reconcile; show "not coded" for NC | med | yes (8.9 open) |
| B-13 | low | Evidence search | Empty state works ("0 best matches ... No record matches"). Search "scaffolding" returned 43 matches. Search failure would read the same as no match (code-read, B-27) | VERIFIED empty state | see B-27 | high | no |
| B-14 | low | Risks screen toast | Success toast appears bottom-left over the rail/Settings button and the last card text; auto-hides | Screenshot after Add all | Position away from rail | low | no |
| B-15 | low | README_GUI.md | Stale: says library of 46 risks "16 without survey value" and 30 seeded (matches), but step table lists 6 steps (no Cost/Options step, Export is "6"), refers to Settings in rail, "Find options online" and charts sections for the Cost screen. Matrix colour contrast claim "5.6:1 or better" confirmed by worker (Extreme 5.60) | README_GUI.md:27-34,52-75 | Update step table to match nav (7 steps) or remove legacy sections once B-05 decided | high | depends on B-05 |
| B-16 | low | Toolbar AI badge | Badge shows "AI: guarded LLM (gemini-3.8-flash)": a model name the user cannot verify; shown while no key is expected offline per README ("offline mode" without key) | Toolbar text | Confirm the name is read from settings, not hard-coded | low | no |

## Code-read findings (worker B2, accessibility and responsive)

| ID | Sev | file:line | Issue | Proposed fix | Conf |
|---|---|---|---|---|---|
| B-17 | high | app.js:165,182 renderScreen | Focus restore works only for elements with an id; Edit/Done, remove, Yes/No/Unknown, tabs, Add buttons lose focus to body after every action | stable data-focus-key restore | med-high |
| B-18 | high | ui.js:264-283, app.js:615-616 | "Clear saved key" confirm reuses the single #modal and destroys the Settings dialog; Cancel closes it all and loses typed key | second dialog or reopen Settings | med-high |
| B-19 | high | index.html:52, app.css:145 | Skip link is .sr-only and never visible on focus | add :focus style | high |
| B-20 | high | matrix.js:45-46,39,44 | role=table with role=cell but no rows/headers: invalid ARIA, matrix not navigable by screen reader | grid/row/gridcell or real table | med-high |
| B-21 | high | theme-designshop.css:272 vs app.css:692 | form-grid auto-fill minmax(260px) overrides the 760px single-column rule; fields overflow at 375px | minmax(min(260px,100%),1fr) | med-high |
| B-22 | high | matrix.js:79 inline style repeat(4,..); app.css:552-553 | Impact-edge form and 5x5 matrix have no narrow-screen layout (cells about 17px wide at 375px) | overflow-x:auto with min-width, or stacked list | med-high |
| B-23 | med | app.css:681 .btn .lbl{display:none}; risks.js:160 | "Custom risk" and toolbar buttons lose their only text at 1040px and below | aria-label | high |
| B-24 | med | theme-designshop.css:159, app.css:336,374,420 | outline:none on inputs, 1px border is the only focus cue; global ring 1px and clipped in scroll containers (theme:44) | 2px ring | med |
| B-25 | med | matrix.js:40, ui.js:70-76 | Risk chips and .term are tabindex spans with only data-tip text: no role/name, tooltips do not work on touch | aria-label with tip text | med |
| B-26 | med | app.js live regions | KPI strip, matrix and evidence count update silently; only #dirty has role=status | aria-live summary line | med |
| B-27 | med | app.js:203-219, 533-536, 646-654 | Evidence fetch failure reads as "No record matches"; New/Load example/health failures give no message; settings failure shows fake "not configured" | alert/toast on !r.ok | high (by code) |
| B-28 | med | app.js:808-827 | boot() and renderScreen have no try/catch: a screen bug blanks the app | wrap and show alertBox | med |
| B-29 | low | risks.js:118 | library filter #lib-q has no label | aria-label | high |
| B-30 | low | app.css:416 | evidence remove (x) chip is 14px, below 24px target | enlarge hit area | high |
| B-31 | low | risks.js:167-170 | tab roles without tabpanel/arrow keys | complete pattern or use buttons | med |
| B-32 | low | `<th>` without scope, no captions (matrix.js:54,59 etc.) | table semantics | scope=col, caption | med |
| B-33 | low | index.html:6 | title never changes per screen | set document.title | med |
| B-34 | low | cursor.js, theme:237 | custom cursor hides native cursor, no forced-colors handling, rAF loop never stops | restore native cursor for inputs; stop loop when idle | med-low |
| B-35 | low | theme-designshop.css:255 | .matrix-graphic hard white background in dark theme | token | low |

Contrast (computed by B2 from CSS hex): matrix cell ink on Low 9.23, Moderate 13.41, High 8.48, Extreme 5.60 (all pass AA); the 10 px level word at opacity .85 gives 4.74 on Extreme (close to limit); adjacent cell colours differ only 1.45-1.58:1 so level relies on the printed word; `--text-3` on `--surface-3` 4.44 (fails 4.5). Not re-run by me.

## Code-read findings (worker B3, wording)

Withdrawn wording ('validated', 'predicts', 'optimal', 'weather is rated lower') does not occur in any reachable UI file (grep by worker). Dead legacy screens (cost, decision, mitigation, productivity, simulation, explain .js) are not imported; productivity.js:66,68 contain "prediction(s)" in the model sense. Deleting them is a user decision.

| ID | Sev | file:line | String / problem | Proposed fix | Conf | User decision |
|---|---|---|---|---|---|---|
| B-36 | med | analysis.js:62-70 | Command banner (e.g. "AUTHORIZE MITIGATION", "Preferred option") reads as an order; strongest decision wording in the UI | "Result under the chosen criterion, inputs illustrative unless sourced" | med | yes (tied to B-05) |
| B-37 | med | analysis.js:79-92 | P50/P90/P(T>deadline), EMV, value at stake, p column shown without Source label; jargon unexplained | add Derived Calculation / Source and plain-language headings | med | no |
| B-38 | med | analysis.js:106,46 | "10,000 iterations" hard-coded in text (QUALITY_BAR 4) | read from result | med | no |
| B-39 | med | analysis.js:67 | "changes with the seed" collides with "literature seed" | "changes with the random draw" | med | no |
| B-40 | med | risks.js:26 | Tier sentence very long and jargon-heavy (p class, RII, tier); lacks short "ordinal only" | "Starting position only: ranked N of M by survey importance (not a probability or days)" | med | no |
| B-41 | med | matrix.js:89-94 | Ranking-basis control uses seed/held-out/pooled/equal-count bands jargon; matrix.js:47 impact axis caption wrongly implies division for tier risks | plain labels ("5 main surveys (default)" / "all 11 surveys"); caveat the axis caption | med | no |
| B-42 | med | rules.js:84-89,95,111 | "Fired", "Not evaluable", "Confidence" (could be read as statistical confidence), "elevated" | "Triggered", "Cannot check: facts missing", "Strength of basis", "of higher concern" | med | no |
| B-43 | med | app.js:241 vs app.js:414 | Toast says flagged risks need p and delay "to place them on the matrix" but seeded ones are already placed | align wording | med | no |
| B-44 | med | risks.js:66 | Hard-coded citations "Dey, 2011; Baker et al., 1999" in a UI hint: confirm they are in the evidence corpus (QUALITY_BAR 6) | verify or remove | med | no |
| B-45 | low | index.html:7,98; app.js:73 | Meta description lacks "ordinal"; noscript/"offline" text says nothing leaves the machine though optional AI/online search do | adjust wording | med | no |
| B-46 | low | cross-cutting | Three names for one thing: literature tier / seed / starting place; Case vs Project; "score" and "p/impact class" unexplained; "NC", "bin edges", "EMV", "PERT/lambda", "Bernoulli" jargon | glossary pass | med | no |
| B-47 | low | ui.js:214-223 | ILLUSTRATIVE banner only triggers on the word "illustrative" in case text; a literature-tier-only matrix shows no equivalent banner (matrix has its own ordinal badge) | also banner for tier-only | med | no |
| B-48 | low | rules.js:131,59,62 | internal field names (`planned_duration_days`, rule ids) shown to users | hide behind details | low | no |

## Not reproduced / not done

- B-17 to B-35 and B-36 to B-48 line numbers were checked by the workers; I confirmed B-01, B-02 and B-06 and the report numbers myself. UNVERIFIED by me in the browser: B-17, B-18, B-19 to B-22 (except overflow in B-01), B-24, B-25, B-27 to B-28, B-30 to B-35.
- Keyboard-only walkthrough, 800 px and 1280 px screenshots, PNG/SVG downloads and the Open/Save file round trip were not exercised. Matrix PNG/SVG exports not compared to screen; the SVG preview on the Export screen matched the md table.
- Evidence browser "Only IDs cited in this case" toggle and Settings dialog were not opened.
