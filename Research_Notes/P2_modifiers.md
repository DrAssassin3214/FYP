# P2 - Productivity modifier models (masonry / manual building trades)

Prepared for the FYP decision-support tool (brick masonry, Indian building construction). Integrity rules: every number below was copied from text I actually opened (full text unless stated); otherwise NR (not reported) or NC (not checked), with "abstract only" / "snippet only" stated. "Open access" is claimed only where a licence statement was seen. Derived numbers are labelled "my arithmetic".

Run status: work resumed after a usage-limit interruption; nothing from the first attempt survived, so all records here were re-derived in this run. Records are re-saved after every 3-4 entries; the file is therefore a running log and later sections (table, gaps) are rewritten at each save.


## 1. Search log (strings and counts)
Tools: Crossref REST (verification + bibliographic search), OpenAlex (open-access location; hit rate limits repeatedly), WebSearch (US-only), built-in browser pane for MDPI/paywall-adjacent pages that block curl/Invoke-WebRequest (extracted MathJax equation source + table DOM directly), direct downloads of open-access HTML/PDF to the scratchpad with pypdf/HTML-strip text extraction. Publisher pages returning 403 or bot-blocked (ASCE, Elsevier, Emerald, ProQuest, UT Austin repository, CORE, ConcreteConstruction, LSU viewcontent, curt.org unreachable, METU repository 500) were NOT bypassed.
- Crossref bibliographic + single-DOI lookups (about 30 DOIs total across two sessions): Thomas & Sakarcan 1994; Grimm & Wagner 1974; Koehn & Brown 1985/1986; Srinavin & Mohamed 2003; Mohamed & Srinavin 2002/2005; Sanders & Thomas 1991/1993; Sweis et al. 2008; Thomas & Raynar 1997; Thomas 1992; Sonmez 2007; Hanna et al. 2005/2008; El-Rayes & Moselhi 2001; Jarkas 2016 (blockwork learning curve); Li et al. 2016 (Beijing rebar); Gerek et al. 2015. Result: all of these classic/masonry-specific quantitative models remain PAYWALLED; only abstracts available (Mohamed & Srinavin 2002; Jarkas 2016; Sonmez 2007).
- OpenAlex open-access checks and searches (rate-limited, HTTP 429, at several points): located green-OA copies for Sweis 2009 (iiste.org), Sonmez 2007 (METU handle, server error), and confirmed all ASCE/Elsevier/Emerald items closed.
- WebSearch (10 queries this session, 9-10 results each): Mohamed-Srinavin PMV equation; CRREL cold-weather masonry; bricklayers heat WBGT regression; India heat/masonry/monsoon; Thomas-Sakarcan factor model; "Formula ... environmental factors" (Malara et al.); heat meta-analysis BMC; overtime BRT/Thomas-Raynar; masonry regression crew/wall-height; Ovararin thesis; Jordan plastering variability; Loganathan-Kalidindi; Al-Zwainy brickwork regression; Ekyalimpa human-robot brickwork; floor-level learning curve; piece-rate incentives; monsoon India; rainfall quantitative models; Koehn-Brown / Grimm-Wagner / Hancher numeric details; Frontiers temperature-productivity.
- Browser-pane full reads (bypassing curl 403s) of three MDPI open-access papers with equations recovered directly from MathJax source + DOM tables: Malara, Plebankiewicz & Juszczyk 2019 (Buildings 9(12):240, fuzzy factor model incl. weather); Ekyalimpa et al. 2023 (Buildings 13(12):3087, brickwork PCA factor ranking, no printable equation); Shan & Goodrum 2014 (Buildings 4(3):295, tabulated Koehn & Brown temperature x humidity productivity-factor table); Sopic, Vrankovic & Marovic 2025 (Appl Sci 15(19):10759, adverse-weather day-count model, explicitly NOT a magnitude model).
- Local held papers (user's Research_Papers/5_Masonry_Productivity_Delay, 16 PDFs) text-extracted with pypdf: Lendra 2026 (P2-02) and Mahamid 2020 (P2-03) read in full; remaining 14 held PDFs text-extracted but not yet screened line-by-line for modifier equations (flagged as a gap).
- Other open PDFs fully read: Yi & Chan 2017 (PMC, heat/rebar HK); Sett & Sahu 2014 (PMC, brick workers India); Han et al. 2024 (BMC meta-analysis); Venugopal et al. 2026 (Sci Rep, Tamil Nadu); Agbo, Izam & Ayegba 2021 (JCDC, plastering Nigeria, low reliability); Sweis, Sweis, Abu Hammad & Abu Rumman 2009 (iiste.org, Jordan masonry baseline/variation); Gerek et al. 2015 (masonry crew ANN, ranking only, no usable coefficients); Rasool & Al-Zwainy 2016 (Iraq brickwork regression); Revay Report (Brunies & Emir 2001, secondary review of overtime charts); Long International web article (Carter, MCAA overtime PI table, secondary).
- Records: 22 items across 18 distinct papers (P2-11 to P2-15 are five sub-records of one paper, Malara et al. 2019). Usable ABSOLUTE-output equations with real coefficients: P2-01 (heat, rebar, unit-ambiguous), P2-03 (rework, brick works), P2-16 (brickwork regression, Iraq, unit not stated). Usable MULTIPLIER/table structures: P2-11 to P2-15 (fuzzy model incl. temperature/rain/wind/shift/learning-in), P2-17 (temperature x humidity table). Day-count (no magnitude): P2-18. Descriptive bands only: P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10.


## 2. Records (each verified from text actually read; see per-record 'Read' line)


### P2-01  Yi & Chan 2017 - heat stress (WBGT) -> rebar-fixing direct work time (Hong Kong)
- Authors/year: Wen Yi; Albert P. C. Chan, 2017. "Effects of Heat Stress on Construction Labor Productivity in Hong Kong: A Case Study of Rebar Workers". Int J Environ Res Public Health 14(9):1055. DOI 10.3390/ijerph14091055 (Crossref-verified, see verification list).
- Access: open access, CC BY (licence text seen on PMC5615592). Read: FULL TEXT (PMC HTML).
- Context: Hong Kong training grounds, Aug-Sep 2016; rebar fixing (manual building trade; NOT masonry).
- Sample/method: 14 male steel-bar fixers, 378 synchronised 15-min data sets (340 to fit, 38 to validate); WBGT (QuesTemp 36), heart rate belt, AACE work sampling (direct / indirect / non-productive); stepwise multiple linear regression.
- Input variable(s): WBGT deg C (observed 22.28-35.46); %HRmax (34.3-80.5); work duration h (0-4); age y (21-39); alcohol habit code 0/1/2.
- EXACT equation (Eq. 2): `CLP = 1.602 - 0.028 WBGT + 0.231 %HRmax - 0.035 WD - 0.005 Age - 0.085 ADH`
- Output: CLP = direct-work-time proportion. ABSOLUTE output, not a multiplier. Unit of CLP inside Eq. 2 not stated in the text read; abstract says DWT falls 0.33% per +1 deg C WBGT, which does not obviously match -0.028 (flag; do not use either number without checking the PDF figure/units).
- Fit: adj R2 = 0.68 (p<0.05); validation RMSE 0.857, MAPE 0.092, Theil U 0.009; max VIF 5.68.
- Also printed (Table 4): mean DWT by time of day (8-9h 57.82%; 9-10h 70.53%; 10:15-11h 72.79%; 11-12h 67.41%; 13-14h 55.96%; 14-15h 59.35%; 15:30-16:30 62.63%). Useful for start-up/afternoon dip, not a modifier equation.
- Limitations: rebar not masonry; HK not India; 14 young acclimatised workers; needs %HRmax input; unit ambiguity above.
- Usable for tool? Partly: supports a direction and order of magnitude of heat effect for manual trades in hot-humid climate; Eq. 2 is NOT directly usable as a multiplier without expert/unit check.


### P2-02  Lendra et al. 2026 - overtime vs regular hours, plastering & skim coating (Indonesia) [held paper]
- Authors/year: Lendra; M. I. R. Resnawan; W. Nuswantoro; Andi, 2026. J Eng Manag Syst Eng 5(2):156-177. DOI 10.56578/jemse050203. Access: open access, CC BY 4.0 (seen on PDF page 1). Read: FULL TEXT (user's local PDF).
- Context: Palangka Raya, Indonesia; two-storey residential; plastering and skim coating (finishing, NOT masonry); 9 regular h + 2-3 overtime h.
- Method: Five-Minute Rating work sampling, 1,296 observations (864 regular / 432 overtime), 6 workers, 3 days per trade; Anderson-Darling normality; Wilcoxon (plastering) / paired t (skim).
- Numbers printed (Table 1): plastering LUR 56.94% regular -> 56.02% overtime (-0.92 pts, text rounds to -1.0%); skim coating 66.67% -> 60.19% (-6.48 pts, text -6.5%). Effective activities per session 133.5 -> 125.5 (-5.99%, Table 4). Volume per hour: plastering 21.28 -> 27.22 m2/man-day (+28%); skim coating 47.99 -> 71.63 (+49%) (Tables 7, 8, abstract). p = 0.109 plastering, 0.031 skim coating; df = 2.
- Form: TABLE only (no equation). Definitions: LUR = t_eff/t x 100% (Eq. 1); relative decrease = (initial - final)/initial x 100% (Eq. 2).
- Decision rule printed (Table 17): if LUR decline > 5% and statistically significant, reconsider overtime.
- Secondary citation (NOT read): Putra et al. [24] cited for lightweight brick-wall installation overtime productivity +185% / +32% / +22% (foreman / labourer / assistant labourer) - Indonesian, snippet-level via this paper only.
- Limitations: not masonry; tiny sample; payment scheme tied to output; authors call results preliminary; conflicts with classical overtime-loss curves.
- Usable for tool? Only as a cautionary, low-weight data point; NOT a modifier equation.


### P2-03  Mahamid 2020 - rework cost -> brick-works productivity (Palestine) [held paper]
- Authors/year: Ibrahim Mahamid, 2020. "Study of relationship between rework and labor productivity in Building Construction Projects". Revista de la Construccion 19(1):30-41. DOI 10.7764/RDLC.19.1.30-41. Access: free PDF held locally; licence text not found in the PDF (open access NOT confirmed). Read: FULL TEXT.
- Context: West Bank, Palestine; 40 building projects 2015-2018 from contracting firms; brick works (Model 2), plus plastering and ceramic.
- EXACT equation (Eq. 5): `Y = 34.36 - 1.71 X`, Y = labour productivity in brick works (m2/day, 2-labour crew), X = rework cost in brick works (% of item contract price). R2 = 0.78 (chart 0.7823), F(1,39) = 62.71, p = 0.00, n = 40; t = 7.11 / 6.44. Mean rework 4.51%, mean productivity 26.2 m2/day.
- Other trades printed: plastering Y = 40.9 - 2.02X (R2 0.82; means 5.11%, 30.59 m2/day); ceramic Y = 44.60 - 2.58X (R2 0.79; means 5.43%, 30.55 m2/day).
- Form: ABSOLUTE output (m2/day for a 2-labour crew), not a multiplier. Derived relative form 1 - 0.0498 X (my arithmetic, not printed).
- Validity range: X not stated numerically; chart axis 0-10 %.
- Also (Table 2, Likert ranking, no quantification): top LP factors lack of labour experience 3.95, payments delay 3.92, rework due to labour mistakes 3.83, lack of supervisor's experience 3.54, materials shortage 3.49; low wages 3.34; absenteeism 2.67; overmanning 2.63; confined space 2.66.
- Flags: paper text defines Y/X inversely in the generic Eq. 3 (Y = rework, X = productivity) but Eqs. 4-6 use Y = productivity; line at mean rework gives 26.65 vs printed mean 26.2 (my arithmetic).
- Usable for tool? YES as an absolute-output relation for brick works (the only brick-specific rework quantification found so far), with the caveats above (Palestine, project-level data, unspecified brick type).


### P2-04  Sweis, Sweis, Abu Hammad & Abu Rumman 2009 - baseline productivity and normal variation band, masonry (Jordan)
- Citation: Jordan Journal of Civil Engineering 3(3):197-212, 2009. DOI: NR (none printed). Access: free PDF on iiste.org; licence not seen (OA not confirmed). Read: FULL TEXT.
- Context: 14 concrete-masonry projects, Amman; crew-shift-level daily data; all rated work content 1 (Table 1 scale 1-5, modified from Thomas & Zavrski 1998).
- Numbers printed (Table 2, averages of 14 projects, work-hours per m2): baseline 0.946; average daily productivity 1.104; range of normal variation above and below average 0.227; above baseline 0.454; UCL 1.314; LCL 0.876. Per-project rows are in the JSON.
- Method: UCL/LCL = mean +/- 3.14 x median of consecutive ranges (Nelson 1984); baseline = mean of days below LCL.
- Modifier content: NONE quantified per factor. The paper lists cited work-environment factors (adverse weather, unavailable material, lack of equipment/tools, out-of-sequence work, congestion, dilution of supervision, rework, scheduled-overtime fatigue) and only PROPOSES a binary-variable regression on (actual - baseline) as future work.
- My arithmetic (labelled): average daily / average baseline = 1.104 / 0.946 = 1.17; UCL / baseline = 1.39. Use only as an order-of-magnitude "normal variation" band.
- Flags: text says baseline = LCL average (0.876) but Table 2 baseline average = 0.946; unit text "20 mm x 20 mm x 40 mm" looks like a typo.
- Usable for tool? As a published range of day-to-day variability around baseline for masonry (useful to bound Monte-Carlo / uncertainty of a productivity model), NOT as a factor modifier.


### P2-05  Agbo, Izam & Ayegba 2021 - work-environment factor regression, wall plastering (Nigeria)  [LOW RELIABILITY]
- Citation: J Constr Dev Ctries (Early View, provisional PDF, accepted 02-Aug-2021). DOI 10.21315/jcdc-01-21-0009. Access: CC BY 4.0 (printed on PDF p.1). Read: FULL TEXT (provisional version).
- Context: 25 public building projects in Abuja, 30-day observation (Jan-Feb 2020), 2-person gangs plastering sandcrete-block walls; plastering, NOT bricklaying.
- Model (as printed): `Pav - PbL = Var - PbL + PL1 X1 + ... + PL15 X15` (X = factor cited that day). R2 = 0.636, F(15,137) = 6.201, DW = 1.346.
- Table 5 (unstandardised B / standardised Beta / p): waiting for materials 2.399 / .624 / .006; on job but not working 3.591 / .526 / .010; congestion .756 / .525 / .011; work redone 1.726 / .517 / .013; waiting for tools 2.498 / .511 / .015; waiting for information 3.593 / .472 / .031; weather 1.170 / .421 / .034; interference .483 / .372 / .046; gang size/composition 1.649 / .310 / .041; unexplained movement -.264 / .320 / .050; not significant: supervision, waiting for other crew, accident, equipment breakdown, waiting for instruction.
- Baseline etc.: avg daily productivity 1.268 whr/m2; baseline 0.993 (abstract; Table 2 prints 0.963); mean coefficient of productivity variation 22.08% (range 8.76-63.3%).
- Flags: units of B not stated (implausibly large vs baseline if whr/m2); Beta values reported in the text as "% of variability"; text p-values differ from table.
- Usable for tool? NO as coefficients. Useful only as (a) ranking evidence that materials waiting, congestion, rework and weather matter for masonry-type trades; (b) the CPV range 8.76-63.3% as a published day-to-day variability figure.


### P2-06  Sett & Sahu 2014 - temperature -> weekly output of brickfield workers (India)
- Citation: Glob Health Action 7:21923 (2014). DOI 10.3402/gha.v7.21923. Access: open access CC BY (licence text on PMC3914028). Read: FULL TEXT.
- Context: West Bengal manual brick-MAKING units (moulders and carriers), NOT bricklaying. 120 questionnaires, weekly output records (88 moulder-weeks, 32 carrier-weeks), cardiac subset n=40; 8-month period.
- Printed: "linear decline in productivity with increased maximum air temperature above 34.9 C"; "lost productivity for every degree rise in temperature is about 2%" (abstract/conclusion); Discussion prints "about a 1.81% loss".
- Form: relative slope (percent output loss per +1 C above ~34.9 C max air temp); NO equation, intercept or R2 printed (Fig. 2 only).
- Secondary values cited inside the paper (not read at source): rice harvesters India ~5% per +1 C WBGT (Sahu et al.); Thailand construction and pottery hourly productivity down 10-60% (Langkulsen et al.).
- Limitations: brick manufacturing, piece-rate self-paced female workers; weekly not hourly output; single unit.
- Usable for tool? Only as an India-specific order-of-magnitude slope (about 1.8-2% per degree above ~35 C) with heavy caveats; not masonry.


### P2-07  Han, Dong, Weng & Xiang 2024 - heat and productivity loss, meta-analysis (construction workers)
- Citation: BMC Public Health 24:3252 (2024). DOI 10.1186/s12889-024-20744-x. Access: open access CC BY-NC-ND 4.0 (seen on PMC11583663). Read: FULL TEXT.
- Content: 14 studies, 2387 workers; random-effects pooled proportion with productivity loss 0.60 (95% CI 0.48-0.72), I2 = 90%. Subgroups (Table 3): WBGT/ambient <= 28 C / 35 C 0.59 (0.44-0.73); above 0.62 (0.37-0.84); self-report 0.67 (0.58-0.75); actual measurement 0.13 (0.03-0.29, 2 studies); age >= 38 0.61; male-only 0.45 vs mixed/female 0.74.
- Secondary (cited, not read at source): Li Beijing rebar 0.57% per +1 C WBGT; Sett India brick workers ~2% per degree above 34.98 C; Zhang "ideal temperature" 24.90 C.
- Form: TABLE of prevalences; not a dose-response equation and not an output multiplier.
- Usable for tool? Supporting evidence only (existence and rough size of heat effect, self-report vs measured gap); no coefficient for a modifier.


### P2-08  Venugopal, Latha & Shanmugam 2026 - heat stress and perceived productivity loss, outdoor workers in Tamil Nadu (India)
- Citation: Sci Rep 16:14228 (2026). DOI 10.1038/s41598-026-41807-6. Access: open access CC BY-NC-ND 4.0 (seen on PMC13139379). Read: FULL TEXT (main article; supplement not read).
- Context: 1560 informal outdoor workers, five sectors incl. construction, 11 districts, 2021-2023; HOTHAPS questionnaire plus WBGT measurements.
- Printed: WBGT above 30 C threshold; 1.4-fold risk of PL with elevated WBGT (95% CI 1.1-1.8); high workload AOR 1.5 (1.2-2.1). Table 3 (n=310 repeat): summer WBGT 21.7-32.7 C, 75% exceed TLV, hours lost 5.8 (0.5-100), PL 32; winter WBGT 20.4-32.5 C, 62%, 3.8 (0.5-60), PL 17; AOR PL summer 2.3 (1.2-4.2).
- Secondary (cited, not read at source): rice harvesters ~5% per +1 C WBGT above 26 C; Muthers et al. 20-50% loss in peak heat.
- Form: TABLE / odds ratios; perception-based, no output multiplier.
- Usable for tool? Context only (Indian seasonal WBGT and perceived loss); no modifier coefficient, no construction-specific number extracted.


### P2-09  Brunies & Emir 2001 (Revay Report 20(3)) - review of published overtime productivity charts  [SECONDARY]
- Citation: The Revay Report, Vol. 20 No. 3, Nov 2001 (consultancy newsletter). DOI: NR. Access: freely downloadable PDF; only a reproduction statement seen, no open licence. Read: FULL TEXT (text layer of the regulations.gov copy); figures not readable.
- Numbers printed: BLS 50/60/70-h weeks 92/82/78%; Foster Wheeler 5x10 h 87%, 6x10 h 73%; CII SD-98 (Thomas & Raynar) loss 10-15% for 5- and 6-day weeks, average about 15%, range none to 25%; NECA 1962 survey (5d x 8h scheduled) 9/10/11/12 h days 100/98/95/92%, 6d x 8h 98%, 7d x 8h 95%, 6d x 10h 84%, 7d x 10h 78% (row-to-category mapping inferred from layout); Haneiko & Henry concrete 60 vs 40 h/wk: 6.78 vs 5.01 hrs/cy.
- Form: TABLE of relative productivity (multiplier on straight-time baseline) by weekly hours.
- Authors' warnings: charts to be used with greatest caution; BRT curves come from one project; CII 1988 found overtime losses inconsistent ("Productivity does not necessarily decrease").
- Limitations: no masonry; US industrial context; no per-day (1-3 h) overtime data.
- Usable for tool? As a published range for weekly-hours overtime (about 5-30% loss depending on weeks and hours) if the team wants a conservative overtime penalty; needs expert choice of curve; primary sources still to be read.


### P2-10  Carter (Long International) - MCAA Bulletin OT1 Revised (2011) overtime Productivity Index values  [SECONDARY]
- Source: Long International web article "Labor Productivity Loss Calculation for Overtime" by Rod C. Carter; undated in the text read. DOI NR. Read: web text (Table 1 image not readable).
- Numbers printed in prose: 50 h/wk PI 0.95 (week 1) to 0.72 (week 10); 60 h/wk PI 0.91 (week 1) to 0.61 (week 10); 54-60 h/wk 2nd consecutive week 0.90; 63 h 0.84; 70-72 h 0.80. Richardson add-ons to standard man-hours: 5-10% (41-48 h/wk), 11-15% (49-50), 16-20% (51-54), 21-25% (55-59).
- Formulae quoted: PI = planned productivity / actual productivity; loss = 1 - PI; inefficient MHs = actual MHs - actual MHs / (1 + inefficiency factor).
- MCAA rule quoted: a return to 40-h weeks "resets" the consecutive-week count.
- Limitations: secondary; industrial trades; weekly hours only.
- Usable for tool? Yes as a published overtime lookup structure (hours-per-week x consecutive weeks) IF the team accepts the MCAA averages; needs the primary bulletin for the full table.


### P2-11 to P2-15  Malara, Plebankiewicz & Juszczyk 2019 - fuzzy factor model for worker productivity incl. weather (Poland)
(One paper, split into five JSON items: P2-11 composite model; P2-12 air temperature; P2-13 precipitation and wind; P2-14 shift duration; P2-15 adaptation/learning-in and absence.)
- Citation: Buildings 9(12):240 (2019). DOI 10.3390/buildings9120240. Access: open access CC BY 4.0 (seen on MDPI page). Read: FULL TEXT via browser pane; equations recovered from the page's MathJax source; Tables 1-5 read.
- Context: Poland; literature + expert membership functions; weights from a 2014 survey (142 respondents: 66 supervisors, 76 workers); validation 236 field measurements over about a dozen works including bricklaying; example is ceiling formwork.
- Composite formula (Eq. 12): `Wp = [ SUM(mu_i * w_i) / SUM(w_i) + 0.5 ]^y`, y from Eq. 13-14 (sigma_w = sigma_t^y). Wp is RELATIVE productivity (1 = standard) so it is MULTIPLICATIVE on a standard rate (example: 0.769 m2/w-h x 1.04 = 0.800).
- Weights (Table 3): 0.25 shift duration, recovery, family time, absence; 0.5 noise, stress, age, precipitation, air temperature, wind, day of week, adaptation; 0.75 ergonomics, workstation organisation, fatigue, health; 1.0 salary.
- Membership functions printed: air temperature (Eq. 7) 0 at <=4 C, rises linearly to 1 at 16 C, falls linearly to 0 at 28 C; precipitation (Eq. 5) 1 at 0 mm falling linearly to 0 at 10 mm; wind (Eq. 6) 1 at 0 m/s to 0 at 10 m/s; shift duration (Eq. 3) 0 at <=6 h, 1 for 7.5-9 h, falling linearly to 0 at 12 h; adaptation (Eq. 9) 0 at day 1 to 1 at day 16; day-of-week (Eq. 11) Mon 0.38, Tue 0.87, Wed 1, Thu 0.88, Fri 0.84, Sat 0. Full list in JSON.
- Table 4: theoretical Wp interval [z1, z2] by exponent y: y=1 0.5-1.5; y=2 0.25-2.25; y=3 0.13-3.38; y=5 0.03-7.59.
- My arithmetic (labelled): with all other factors neutral (mu = 0.5), y = 1 and SUM(w) = 9 (all 17 factors), one factor at mu = 0 vs mu = 1 changes Wp only from about 0.97 to 1.03 for a weight-0.5 factor (Wp = 1 + w(mu-0.5)/9). Using only some factors changes SUM(w); the sensitivity is governed by y.
- Flags: Eq. 1 age function has overlapping printed cases; Eq. 8 absence function looks inverted; example recovery mu printed 0.28 vs 0.25 from Eq. 4; y for the example not printed; no validation correlations printed in text read.
- Limitations: expert/Polish; not fitted; temperate optimum (16 C) and 28 C cut-off are not valid for Indian summer heat.
- Usable for tool? A ready-made structure (weights + membership functions + multiplicative Wp) that could be re-parameterised for India by an expert; coefficients NOT transferable as printed.


### P2-16  Rasool & Al-Zwainy 2016 - brickwork productivity regression (Iraq)  [LOW-MEDIUM RELIABILITY]
- Citation: Sch J Eng Tech 4(5):234-243 (2016). DOI: NR. Access: free PDF, licence not seen. Read: FULL TEXT.
- Data: n = 50 brickwork observations from a Baghdad University thesis (2011/2012); variables age (22-55 y), experience (4-32 y), number of workers (4-8), level of execution (1-3, labelled "Meter").
- EXACT MLR equation (Eq. 3): `y = 4.010 + 0.025 X1 - 0.013 X2 - 0.038 X3 - 0.417 X4` (X1 age, X2 experience, X3 no. of workers, X4 level). p-values: age 0.013, experience 0.234, workers 0.554, level 0.003. R = 0.682, R2 = 0.466, adj 0.418 (Table 5); validation on 5 new cases R 87.28%, MAPE 7.5%.
- Logistic (Eq. 6): `3.257 + 0.166 X1 - 0.193 X2 - 0.095 X3 - 3.204 X4` (probability of "good" productivity), Nagelkerke R2 0.583.
- Form: ABSOLUTE productivity (unit not stated; mean 3.95), not a multiplier.
- Flags: unit and definition of "level" missing; age/experience signs conflict (r = 0.76 between them); very small validation set.
- Usable for tool? Only as directional evidence that higher building level lowers brickwork productivity (about -0.417 per level unit, about 10.6% of the 3.95 mean, my arithmetic) and that crew size effect is not significant; not usable numerically without the original definitions.


### P2-17  Shan & Goodrum 2014 - temperature x humidity productivity-factor table (tabulated Koehn & Brown model)  [SECONDARY REPRODUCTION]
- Citation: Buildings 4(3):295-319 (2014). DOI 10.3390/buildings4030295. Access: open access CC BY 3.0 (seen on MDPI page). Read: FULL TEXT via browser pane; Table 2 extracted cell by cell.
- What it is: the authors adopt the Koehn & Brown (1985) temperature-humidity model and print it as Table 2, a productivity factor (<= 1, percent of standard efficient operation) by temperature (-20 to 120 F = -28.9 to 48.9 C, 15 rows) and relative humidity (5 to 95%, 10 columns). Full table in the JSON.
- Key cells (factor at RH 35% / 75%): 26.7 C (80 F) 1.00 / 0.96; 32.2 C (90 F) 0.93 / 0.85; 37.8 C (100 F) 0.79 / 0.67; 43.3 C (110 F) 0.57 / 0.41; cold side 4.4 C (40 F) 0.96 / 0.96; -1.1 C (30 F) 0.90 / 0.89; -12.2 C (10 F) 0.70 / 0.62. Optimal 10-21 C (50-70 F) = 1.00 at all humidities.
- Form: TABLE, multiplier on baseline output (man-hours = baseline man-hours / factor). Daily factor = average of time-point factors over the 10-h day (Eq. 1 variable definitions only).
- Authors' description of source data (not read at source): Koehn & Brown 172 points across steel, MASONRY, electrical, carpentry, labour; Grimm & Wagner 51 workers erecting standard masonry wall panels at 40-100 F, RH 20-100%; Thomas & Yiakoumis 12-82 F.
- Limitations: secondary; US data; no acclimatisation/clothing/work-rate terms; table ends at 48.9 C; original K&B equations and fit not read.
- Usable for tool? YES as the best available published temperature-humidity multiplier table that includes masonry-related data, provided the team labels it "as tabulated by Shan & Goodrum after Koehn & Brown" and an expert confirms suitability for Indian acclimatised workers.


### P2-18  Sopic, Vrankovic & Marovic 2025 - adverse-weather DAY-COUNT model (Croatia)  [no magnitude; secondary citations noted]
- Citation: Appl Sci 15(19):10759 (2025). DOI 10.3390/app151910759. Access: open access CC BY 4.0 (seen on MDPI page). Read: FULL TEXT via browser pane (tables + MathJax formulas + conclusion).
- Own model: inclusion-exclusion estimate of the expected number of days per month with at least one adverse-weather event (precipitation >=10 mm, stormy wind >=17.2 m/s gust, cold Tmin<0C or hot Tmax>=30C), with 95% CIs (Shapiro-Wilk then t- or Z-interval). Applied to Rijeka, Krk, Pazin, 1999-2022. Example: Rijeka July 17-21 of 31 days; Pazin January about 22 of 31 days.
- Formulas extracted (Eq. 4-6): pairwise/triple joint-day corrections built from marginal day counts treated as roughly independent, e.g. Eq.4 = a+b+c - (a/d)b + (a/d)c + (b/d)c + (a/d)(b/d)c.
- CRITICAL: the authors state explicitly in the Conclusions that this model gives only the expected COUNT of affected days, NOT the magnitude of productivity loss (not 25%, 50%, 75%, etc.) - magnitude is left to the schedule planner.
- Secondary citations inside this paper (NOT verified at source in this run): light rain <4 mm/12h up to 40% loss; productivity drops above 10 mm precipitation; unaffected 10-20 C, drops above 25 C or below 0 C; up to 57% loss per +1 C above 28 C; wind >=8.94 m/s: 30-40% loss; heavy snow 35% loss; hard stops below -23.3 C or above 43.3 C.
- Usable for tool? The day-count/frequency method (Eq. 4-6) is a genuinely usable structure for estimating exposure days if India monsoon/heat threshold day-counts are available, but it produces NO productivity multiplier by itself - magnitude must come from elsewhere (e.g. P2-17's Koehn & Brown table). The secondary citations are leads only, not verified figures.




## 3. Modifier -> usable equation? -> paper IDs -> validity range -> what still needs user/expert input

| Modifier | Usable equation? | Paper IDs | Validity range (as printed) | Still needs user/expert input |
|---|---|---|---|---|
| Temperature x humidity (multiplicative table) | YES - table, multiplier on baseline man-hours | P2-17 (tabulated Koehn & Brown, secondary) | -28.9 to 48.9 C, RH 5-95% | Confirm suitability for acclimatised Indian workers; original K&B equation still unread (paywalled) |
| Heat stress (WBGT) -> absolute output | PARTIAL - absolute regression, unit ambiguous, rebar not masonry | P2-01 (Hong Kong) | WBGT 22.3-35.5 C | Unit check of Eq.2; a masonry-specific curve (Sanders & Thomas, Srinavin & Mohamed) still unread |
| Max air temperature -> brick-making output slope | PARTIAL - relative slope only (~1.8-2%/deg C above ~35C), no equation | P2-06 (India, brick manufacture not laying) | Tmax > 34.9 C | Confirm transferability to bricklaying (not brick-making) |
| Heat prevalence (any trade) | NOT a magnitude - prevalence/odds only | P2-07 (meta-analysis), P2-08 (Tamil Nadu) | WBGT >28C/ >30C thresholds | Use for context/validation only |
| Fuzzy composite factor model incl. weather, rain, wind, shift length, learning-in, absence | YES - explicit multiplicative Wp formula + membership functions | P2-11 to P2-15 (Poland) | Temperate optimum 16C, 0-28C band; rain 0-10mm; wind 0-10 m/s; shift 6-12h; learning-in 1-16 days | Re-parameterise membership functions and weights for Indian climate/labour before use; not fitted, expert/survey-based |
| Adverse-weather day frequency (rain>=10mm, wind, cold/hot days) | Day-COUNT only, no magnitude | P2-18 (Croatia) | Monthly counts, temperate thresholds | Combine with a magnitude table (e.g. P2-17) and India-specific thresholds (monsoon mm, WBGT) |
| Overtime / extended hours | Lookup tables only (secondary, industrial trades, weekly-hours basis); one tiny finishing-trade study (India-adjacent, Indonesia) inconclusive | P2-09, P2-10 (secondary reviews), P2-02 (Indonesia, unreliable) | 50-70 h/week (P2-09/10); 2-3 h/day (P2-02) | Primary Thomas & Raynar 1997 and CII SD-98 still paywalled/unread; no data for typical 1-3 h/day Indian overtime |
| Rework / defects -> absolute brick-works productivity | YES - linear equation with R2, brick works | P2-03 (Palestine) | rework roughly 0-10% of item price (chart axis) | Confirm brick type/thickness; consider deriving a relative multiplier from the printed slope/intercept |
| Crew size, worker age/experience, building level, wall length/height, mortar type | NOT usable numerically - factor rankings only (ANN weight order, PCA loadings, Likert means), one weak Iraqi regression | P2-16 (Iraq, weak/unit-unstated), plus ranking-only: Gerek 2015, Lawaju 2021, Ekyalimpa 2023 | - | Sanders & Thomas 1991/1993 masonry equations and Ovararin 2001 thesis (crew/disruption coefficients) remain paywalled/repository-blocked - highest-priority follow-up |
| Day-to-day variability / baseline productivity band (uncertainty) | YES as a descriptive band, not a factor modifier | P2-04 (14 Jordan masonry projects), P2-05 (CPV 8.76-63.3%, Nigeria plastering) | - | Use only to bound uncertainty/Monte-Carlo range, not as a directional modifier |

## 4. Gaps
- No published, fully-read India-specific masonry/bricklaying temperature or monsoon-rain productivity EQUATION was found. The closest is a brick-MANUFACTURING (not bricklaying) slope (P2-06) and a Tamil Nadu perception study with no output-per-hour number (P2-08).
- Classic foundational weather-productivity equations (Thomas & Sakarcan 1994 factor model; Grimm & Wagner 1974; Koehn & Brown 1985 original equations; Srinavin & Mohamed 2003; Mohamed & Srinavin 2005 PMV equations; Hancher & Abd-Elkhalek 1998) are all paywalled - only their tabulated/cited reproductions (P2-17) or abstracts were accessible.
- Masonry-specific factor/disruption equations (Sanders & Thomas 1991 "Factors Affecting Masonry-Labor Productivity"; Sanders & Thomas 1993 "Masonry Productivity Forecasting Model"; Sweis et al. 2008 US/UK/Jordan comparative baseline; Ovararin 2001 PhD thesis on field-disruption productivity loss in masonry) are paywalled or the repository blocked the download (UT Austin 403) - these are the highest-value unread sources for a masonry-specific factor model and should be the first follow-up (e.g. via institutional access or interlibrary loan).
- No primary overtime study calibrated to short (1-3 h/day) daily overtime, typical of Indian sites, was found; all located quantifications use US/Canadian weekly-hours industrial data (P2-09, P2-10) or one small, methodologically weak Indonesian finishing-trade study (P2-02).
- 14 of the 16 user-held PDFs in Research_Papers/5_Masonry_Productivity_Delay were text-extracted but not yet screened line-by-line for modifier equations (time-boxed out of this run).
- Monsoon/rain-day quantification specific to Indian masonry productivity was not located; P2-18 gives a day-count method (transferable) but no magnitude, and El-Rayes & Moselhi 2001 (highway rainfall model) remains paywalled.


