# Topic Group D - Mitigation effectiveness (brick masonry, India, FYP decision-support system)

Status: v2 (final for this pass). 37 numbered papers D01-D37 (of which 15 carry a numeric effect: D01, D02, D03, D04, D05, D06, D09, D12, D14, D17, D20, D26, D27, D30, D32; the rest are qualitative/method papers, flagged), plus 7 bibliographic-only items. Sections: 0 conventions, 1 papers, 2 bibliographic-only, 3 context, 4 representation of response effect, 5 search log, 6 mitigation table, 7 model implications, 8 not located, 9 housekeeping.
Compiled: 2026-09-26.

## 0. Integrity conventions used in this file

- A number is recorded ONLY if I saw it in text I fetched. Everything else is `NR` (not reported in the text I saw) or `not located`.
- "FULL" = I read the full text (PDF/HTML converted to text). "ABSTRACT" = I saw only the publisher/indexer abstract (via OpenAlex/Crossref metadata or a repository landing page). I did not read the body of ABSTRACT papers, so their limitations are inferred from the abstract only and flagged.
- "Open access" is only stated as VERIFIED when a licence statement was visible in the text I fetched. Where the licence comes only from OpenAlex/DOAJ metadata (licence text itself not seen) it is written "OA per metadata (licence text not seen)".
- "Effect type": E = empirical (measured/observed on real projects), S = survey/perception (opinion of respondents), X = expert-elicited, M = model/simulation-assumed.
- Quotes are verbatim from the text I saw (typos of the source preserved).
- Access problems: MDPI, ScienceDirect, ResearchGate, TandF returned 403; ASCE and Springer paywalled; WebSearch quota (200/session) was exhausted mid-task, so from that point only API/direct-fetch routes (OpenAlex, Crossref, Semantic Scholar, repository PDFs) were used.
- Already in the evidence base (NOT re-reported): Lendra 2026, AlJassmi 2023, Merisalu 2021, Senic 2025, Safaeian 2022, Ghaeb & Mahjoob 2023, Koulinas 2021.

---

## 1. Verified papers (D01-D31)

### A. Lean / Last Planner / logistics (topic 1, 6)

**D01 - Vignesh (2017)** [FULL]
- Ref: Vignesh C. "A case study of implementing Last Planner System in Tiruchirappalli District of Tamil Nadu - India." Int. J. Civil Eng. & Technology (IJCIET) 8(4), 1918-1927.
- DOI: none printed on the paper (IAEME article ID IJCIET_08_04_218). Not verified via Crossref.
- Access: free PDF from publisher site; licence statement not seen -> not marked open access.
- Context: India (Tamil Nadu). Multipurpose college building, contract value "approximately 8 cores in INR" [sic], planned 22 months. LPS introduced when 45% of time had elapsed and project was "2 months behind schedule". Action research; author was a participant/team coordinator.
- Mitigation: Last Planner System (look-ahead, weekly work plan, PPC tracking) + bonus payment + free closed-user-group phones.
- Measured effect (verbatim): "The average PPC during the observation of 8 weeks of traditional management of the contractor was 37.5%." / "PPC rose from 53% in the first week to a level of 96% and peaked at 121% (were 104 assignments completed against 86 planned assignments) when bonus payment was introduced." / "The average PPC after implementation was 85%."
- Delay effect: NR in days. Only "The majority of site team believed that LPS was the reason that the project was able to be delivered on time." (perception).
- Causes of incomplete assignments (verbatim): "Material unavailability was the primary reason for incomplete assignment" (local ban on fine aggregate, lorry strike, trade ban); pre-requisite work second; "unavailability skilled labour was the third reason". "This shortage of labour was however overcome by proper planning and motivating labour by providing bonus payment".
- Type: E (single case, before/after) + S.
- Transferability to India masonry: high on context (India, building), but the activity is structure/finishing generally, not masonry-specific.
- Limitations: n=1 project; PPC>100% shows measurement artefact; no days-saved or cost; author involved in implementation; PPC is a reliability metric, not delay.

**D02 - Patel, Solanki, Shah, Bharania (2026)** [FULL]
- Ref: "Lean Tools Application to Minimize Construction Waste and Improve Site Productivity: A Case Study on 5S System and Last Planner System." Int. J. Science, Strategic Management and Technology 2(5).
- DOI: 10.55041/ijsmt.v2i5.090 (resolves per OpenAlex; DOI string printed in the PDF).
- Access: open access VERIFIED - PDF states "published under the Creative Commons Attribution 4.0 International License (CC BY 4.0)".
- Context: India (Ahmedabad, Gujarat), residential-commercial building ("Orchid Gold Project" in Table VI). 15-day field study + questionnaires to 82 professionals; RII analysis.
- Mitigation: Last Planner System; 5S.
- Measured effect (verbatim, abstract): "The Last Planner System was more efficient with an overall RII of 0.890, leading to a reduction of between 12-20% in project delay and between 15-22% increase in productivity. The percent plan complete increased from 60% to 85% after the use of LPS." "The 5S System ... resulting in an approximate reduction of between 8-12% in material waste and between 10-18% increase in labour efficiency."
- Table VI (verbatim rows): "Percent Plan Complete (PPC) 60% 85% 25%"; "Labour Productivity Baseline Improved 20-25% gain"; "Workflow Delays Frequent Reduced 12-20% reduction".
- Note the internal inconsistency: productivity gain is 15-22% in abstract and 20-25% in Table VI.
- Type: mostly S (RII = perception) with a short field observation; the ranges are described as "estimated"/"approximate".
- Transferability: India, building - good geographically; evidence quality weak.
- Limitations: only 15 days of field data, so a before/after PPC change over that horizon is questionable; ranges look like respondent estimates; new low-tier journal; no per-activity (masonry) breakdown. Use only as an order-of-magnitude "claim", not as calibrated input.

**D03 - Alsharqawi, Mohammadpour, Salama (2026)** [FULL]
- Ref: "Evaluating lean construction impacts on waste, lead time, rework, and cost: a case study of a commercial building project." Proc. IGLC34, pp. 1642-1653.
- DOI: 10.24928/2026/0219.
- Access: free PDF (IGLC storage); licence statement not seen -> not marked open access.
- Context: Canada (Eastern Ontario), 4-storey office ~9,000 m2, CAD 34M, ~18 months planned; lean started at Month 6. Prior state: "recurring material shortages, excessive on-site inventory, and unsynchronized scheduling".
- Mitigation bundle: Value Stream Mapping resequencing + Just-in-Time material handling + pull planning with LPS + daily stand-ups + selective preassembly + site-layout optimisation (bundle - effects not separable).
- Measured effect (Table 2, verbatim): material waste "~50 (projected total)" -> "~37 (actual total)" "= 25%"; avg. task duration "Baseline (planned)" -> "Actual (after pull)" "= 30% reduction (on avg)"; PPC "~55% (initial phases)" -> "~80% (later phases)" "+ 25 percentage points"; rework incidents "15 (estimated)" -> "12 (recorded)" "20% reduction"; labour productivity "1.0 (baseline index)" -> "1.1-1.2 (index)" "= 10-20% increase"; cost "~5% under budget" "= 15% cost savings" (footnote: relative to business-as-usual expectation).
- Type: E (single case, before/after) but several "before" values are projected/estimated (M).
- Transferability: low-medium (Canadian concrete-frame office, not masonry); useful only as an indication that JIT+LPS bundles shorten task durations.
- Limitations: one case; bundle; "before" baselines partly estimated; percentages are approximate ("about", "roughly").

**D30 - Kovvuri (Ramachandra Reddy), Sawhney, Ahuja, Sreekumar (2016)** [FULL - author manuscript draft from LJMU repository]
- Ref: "Efficient Project Delivery Using Lean Principles - An Indian Case Study." J. Institution of Engineers (India) Series A. DOI: 10.1007/s40030-016-0142-6 (per OpenAlex; DOI not printed in the manuscript draft). The text I read is the "Manuscript Draft" (may differ from the printed version).
- Access: green repository copy of the manuscript draft (LJMU); licence not seen -> not marked open access.
- Context: India, large construction project with two buildings; 15 weeks pre-LPS data, LPS for 8 weeks; action research (researcher embedded).
- Pre-LPS baseline (verbatim, Table 1): "Average PPC ... Building-1 52.9% ... Building-2 52.7% ... Overall site 52.8%" (min 15.8%, max 72.1%).
- During LPS (verbatim, Table 2): weekly PPC "54.16 70.83 57.89 71.43 72.73 84.21 86.36 95.24 72.25" (last value = cumulative; 151 of 209 tasks completed).
- Failure analysis (verbatim): "plan failures contribute 65 % of total failures"; "62 % causes of the failures were found to be due to internal reasons such as machinery, materials, submittals etc., which can be avoided, and 38 % of the failures are due to external reasons such as weather, design changes, hold by client etc."
- Constraints in the last two weeks (verbatim): "constraints that occurred were observed to be limited to only labour shortage , a problem owing to the unorganized nature of labour forces and material unavailability."
- Delay in days / cost: NR. Type: E (single case, pre/post, PPC only). Limitations: 8 weeks; PPC is reliability, not schedule delay; the draft's conclusion says LPS "would stand to benefit not only in terms of duration but also cost" (claim, not measured). Transferability: India building project - good; activity not masonry-specific.

**D28 - Gonzalez, Alarcon, Mundaca (2008)** [ABSTRACT]
- Ref: "Investigating the relationship between planning reliability and project performance." Production Planning & Control. DOI: 10.1080/09537280802059023. Access: closed.
- Context: a home-building project (country not stated in the abstract I saw).
- Effect (verbatim): "Statistical analyses ... showing positive and strong relationships between planning reliability and performance at activity and project levels." Numbers: NR in abstract.
- Type: E (correlational). Limitation: correlation, one project; no delay-days.

**D29 - Lagos & Alarcon (2021)** [ABSTRACT]
- Ref: "Assessing the Relationship between Constraint Management and Schedule Performance in Chilean and Colombian Construction Projects." J. Management in Engineering. DOI: 10.1061/(asce)me.1943-5479.0000942. Access: closed.
- Effect (verbatim): "Statistically significant correlations were found among constraint management, short-term compliance, and schedule accomplishment" in "69 construction projects". Effect sizes NR in abstract.
- Type: E (cross-project correlation). Use: supports the direction "constraint removal (e.g. material/labour readiness) improves schedule performance"; no probability/impact reduction factor.

### B. Crashing, overtime, shift work, congestion (topics 1, 4)

**D07 - Sonmez (2007)** [ABSTRACT; OpenMETU repository copy flagged cc-by-nc-nd in metadata, full text not fetched (server error)]
- Ref: Sonmez R. "Impact of occasional overtime on construction labor productivity: quantitative analysis." Canadian J. Civil Engineering 34(7), 803-808 (Crossref-verified). DOI: 10.1139/l07-004.
- Effect (verbatim): "Productivity data for 234 weeks were collected for quantitative analysis." / "The results of quantitative analysis indicate that moderate levels of occasional overtime did not have a significant impact on productivity." No % NR.
- Type: E. Limitation: "moderate" not quantified in abstract; trade/country not in abstract.

**D08 - Hanna, Taylor, Sullivan (2005)** [ABSTRACT]
- Ref: "Impact of Extended Overtime on Construction Labor Productivity." J. Constr. Eng. Manage. 131(6), 734. DOI: 10.1061/(asce)0733-9364(2005)131:6(734). Closed.
- Effect (verbatim): "The results show a decrease in productivity as the number of hours worked per week increase and/or as project duration increases." Data "from 88 projects located across the United States"; "labor intensive trades such as the electrical and mechanical trades". Percentages NR in abstract.
- Type: S/E (questionnaire of projects). Transferability: low (US electrical/mechanical trades).

**D09 - Hanna, Chang, Sullivan (2008)** [ABSTRACT]
- Ref: "Impact of Shift Work on Labor Productivity for Labor Intensive Contractor." J. Constr. Eng. Manage. 134(3), 197. DOI: 10.1061/(asce)0733-9364(2008)134:3(197). Closed.
- Effect (verbatim): "Small amounts of well-organized shift work can serve as a very effective response to schedule compression. The productivity loss, obtained from the quantification model developed through this study, ranges from -11 to 17% depending on the amount of shift work used." (sign convention "-11" as printed.)
- Type: E/model (regression "quantification model"). Transferability: low-medium (US labour-intensive contractors; not masonry). Limitation: sign convention ambiguous in abstract.

**D10 - Li, Love, Drew (2000)** [ABSTRACT]
- Ref: Li H., Love P.E.D., Drew D.S. "Effects of overtime work and additional resources on project cost and quality." Engineering, Construction & Architectural Management 7(3), 211-220 (Crossref-verified). DOI: 10.1108/eb021146. Closed.
- Mitigation and side effect (verbatim): "excessively prolonged overtime work can generate quality problems, such as rework, and additional resources." System-dynamics model of overtime vs added resources; "Utility theory is then applied to determine the most appropriate solution for mitigating project delays." Numbers: NR.
- Type: M (system dynamics). Use: conceptual support for modelling overtime -> rework (secondary risk).

**D12 - Lindhard, Salhab, Hamzeh (2025)** [ABSTRACT; full text under embargo per Aalborg portal - not OA]
- Ref: "Illustrating the impact of implementing work zones, adjusting work patterns and optimizing crew starting positions to minimize spatial conflicts." Engineering, Construction & Architectural Management. DOI: 10.1108/ecam-03-2025-0385.
- Context: simulation of interior finishing (flooring), two teams; task durations beta-distributed. Secondary risk of crashing by adding manpower: spatial conflicts/congestion.
- Effect (verbatim): "defining clear work zones reduced spatial conflicts by 68.3% and cut delays from 12.97% over the ideal two-team time in the unplanned case to 3.47%." / "combining work zones with optimized starting positions achieved near-ideal performance, with only 1.01% delay over the ideal and 94.7% fewer conflicts than the unplanned scenario".
- Type: M (simulation, assumptions inside paper not seen). Transferability: medium for the mechanism (adding crews -> congestion -> productivity loss), not for the numbers (flooring, not masonry).

**D25 - Senses & Kumral (2023)** [ABSTRACT; Crossref lists CC BY 4.0 licence URL; paper body not seen]
- Ref: "Trade-off between time and cost in project planning: a simulation-based optimization approach." SIMULATION 100(2), 127-143 (Crossref-verified). DOI: 10.1177/00375497231196889.
- Verbatim: "the time-cost trade-off is achieved under the project deadline and budget constraints by implementing 20,736 different crashing scenarios." Underground mine development example.
- Type: M. Use: methodological precedent for post-mitigation (crashing) simulation with cost; no effect size.

**D26 - Al-Alawi (2025)** [ABSTRACT; Crossref lists CC BY-ND 4.0 licence URL; paper body not seen]
- Ref: "Modeling, Investigating, and Quantification of the Hot Weather Effects on Construction Projects in Oman." The Journal of Engineering Research (TJER) 17(2), 89-99 (Crossref-verified). DOI: 10.53540/1726-6742.1129.
- Verbatim: "Results indicate that implementing the influence of hot and humid weather can lead to an extension of 3-38% longer project duration compared to the planned duration." Model uses NIOSH work/rest schedule; 3 completed projects, Muscat.
- Type: M. This is the hazard impact (not mitigation effectiveness); heat not monsoon. Limited transferability to monsoon.

### C. Substitution, prefabrication, mechanisation (topic 1)

**D04 - Anand & Ramamurthy (2003)** [ABSTRACT]
- Ref: "Laboratory-Based Productivity Study on Alternative Masonry Systems." J. Constr. Eng. Manage. 129(3), 237. DOI: 10.1061/(asce)0733-9364(2003)129:3(237). Closed.
- Verbatim: "work sampling (adopting the 5 min rating technique) was used" ... "Productivity enhancement of 80-120% was observed for dry-stacked masonry and 60-90% more for thin-jointed and mortar-bedded interlocking-block masonry than that of conventional masonry."
- Type: E (laboratory, controlled). Country not stated in the abstract (I did not verify authors' affiliation from the text I saw).
- Relevance: the only masonry-specific measured productivity effect of switching masonry system I located. Transferability to AAC or ordinary block substitution: NOT direct - it is interlocking/dry-stacked/thin-joint systems in a lab.
- Limitations: lab setting; interlocking blocks are not AAC or standard clay brick; sample size NR in abstract.

**D05 - Abdul Kadir, Lee, Jaafar et al. (2006)** [ABSTRACT]
- Ref: Abdul Kadir M.R., Lee W.P., Jaafar M.S., Sapuan S.M., Ali A.A.A. (2006) "Construction performance comparison between conventional and industrialised building systems in Malaysia." Structural Survey 24(5), 412-424 (Crossref-verified). DOI: 10.1108/02630800610712004. Closed.
- Verbatim: "Data were obtained from 100 residential projects through a questionnaire survey in 2005." / "the conventional building system of 22 workers was significantly different from the IBS of 18 workers. Similarly, the cycle time of 17 days per house for conventional building system was found to be significantly different from the IBS of four days."
- Type: S (questionnaire). Transferability: low-medium (Malaysia, structural system, not masonry). Limitation: respondent-reported; cost was "insignificantly different".

**D06 - Shahzad, Mbachu, Domingo (2015)** [ABSTRACT; OA: CC BY 4.0 per Crossref publisher-deposited licence URL; paper body not seen - MDPI returned 403]
- Ref: "Marginal Productivity Gained Through Prefabrication: Case Studies of Building Projects in Auckland." Buildings 5(1), 196-208 (Crossref-verified). DOI: 10.3390/buildings5010196.
- Verbatim: "Records of completion times and final contract values of 66 building projects implemented using prefab in Auckland were collected." / "the equivalent completion times and the final cost estimates for similar buildings implemented using the TBS were obtained from the Rawlinsons construction data handbook and feedback from some designers and contractors." / "Results showed that the use of prefab in place of TBS resulted in 34% and 19% average reductions in the completion times and costs, respectively. This also translated to overall 7% average improvement in the productivity outcomes".
- Type: E for prefab side, M/X for the counterfactual (handbook + practitioner feedback).
- Transferability: low-medium (NZ, whole buildings).

### D. Incentives, training, workforce (topic 1, 6)

**D27 - Fagbenle, Adeyemi, Adesanya (2004)** [ABSTRACT]
- Ref: "The impact of non-financial incentives on bricklayers' productivity in Nigeria." Construction Management and Economics. DOI: 10.1080/0144619042000241262. Closed.
- Verbatim: "on-site observation and measurement of bricklayers' output on 40 construction projects" / "non-financial incentive schemes significantly improved bricklayers' productive time and these schemes accounted for 6% to 26% of the variations in output between the two sets of sites on block laying and concreting activities measured."
- Type: E (with vs without incentive sites). IMPORTANT nuance: "accounted for 6% to 26% of the variations in output" is a variance-explained figure, NOT a % productivity gain. Do not use it as a productivity multiplier.
- Transferability: medium (bricklayers, developing-country labour-intensive context, Nigeria).

**D31 - Johari & Jha (2021)** [ABSTRACT]
- Ref: "Exploring the Relationship between Construction Workers' Communication Skills and Their Productivity." J. Management in Engineering. DOI: 10.1061/(asce)me.1943-5479.0000904. Closed.
- Context: India, six sites with a training yard; 114 workers; productivity measured directly on site.
- Verbatim: "an increase in listening and writing skills impact the productivity of workers positively, while an increase in speaking and reading skills affect it negatively."
- Effect sizes NR in abstract. Type: E (regression). Use: training design direction only; no effect size for a training mitigation.

**D23 - Karthik & Rao (2019)** [ABSTRACT]
- Ref: "Identifying the significant factors affecting the masonry labour productivity in building construction projects in India." Int. J. Construction Management. DOI: 10.1080/15623599.2019.1631978. Closed.
- Verbatim: "38 factors" ranked by RII from "120 construction site personnel working in various organisations in Telangana state"; "Work force-related factors were found to be the majority affecting factors with average RII of 78.4%."
- Type: S. Use: tells where the mitigation levers matter (workforce, working conditions); no effect size.

### E. Buffers (topic 1)

**D11 - Horman & Thomas (2005)** [ABSTRACT]
- Ref: "Role of Inventory Buffers in Construction Labor Performance." J. Constr. Eng. Manage. 131(7), 834. DOI: 10.1061/(asce)0733-9364(2005)131:7(834). Closed.
- Verbatim: "data collected from three commercial projects in Brazil" (rebar fabrication vs installation buffer) / "The results show that some buffer helps achieve the best labor performance in the construction operations studied." Also: "when oversized, buffers are wasteful, impede workflow, and hinder performance."
- Effect sizes NR in abstract. Type: E (exploratory, 3 projects). Use: indicates a non-monotonic (optimal-size) buffer effect - a buffer-stock alternative should not be modelled as "more is always better".

### F. Risk-response representation, taxonomy, secondary risk (topics 2, 3, 4)

**D13 - Ben-David & Raz (2001)** [ABSTRACT]
- Ref: "An integrated approach for risk response development in project planning." J. Operational Research Society 52(1), 14-25. DOI: 10.1057/palgrave.jors.2601029 (verified via Crossref: authors, journal, year, volume, pages match). Closed.
- Verbatim (abstract): "The model allows the representation of the overlapping effects of multiple risk reduction actions and of the impacts of secondary risk events, and supports the evaluation of the total risk exposure of the project under various combinations of risk reduction actions. The model can be treated with optimisation techniques in order to generate the most cost-effective combination of risk reduction actions." Example from the software industry.
- Numeric parameters/elicitation: NR (body not read). Type: M. Relevance: direct conceptual precedent for (i) overlapping effects of several actions and (ii) secondary risk events.

**D14 - Dey (2011)** [FULL - Aston repository accepted manuscript; licence not seen]
- Ref: Dey P.K. "Project risk management using multiple criteria decision-making technique and decision tree analysis: a case study of Indian oil refinery." Production Planning & Control 23(12), 903-921 (Crossref-verified). DOI: 10.1080/09537287.2011.586379.
- Context: India (refinery construction, central India), action research, 4 work packages; AHP for probability, risk map for impact, decision tree/EMV for choosing responses.
- Taxonomy (verbatim): "Risk analysis results derived a few risk responses in line with the principles to avoid, to reduce, to transfer and to absorb." Responses included "Scheduling the project by accommodating seasonal calamities" and "Selecting superior contractors, consultants and vendors on the basis past performance."
- Baseline (verbatim): "the project was expected to have experienced 4.81 months delay and US$ 30.28 million cost overrun."
- HOW EFFECTIVENESS WAS SET (verbatim): "it was assumed that if all the responses were under taken the probability of residual risk would be 5%), and the effects of risk factors on time and cost after risk response have been estimated from cumulative experience of the risk management group through focus group."
- Outcome (verbatim): "Total cost for risk responses was US$ 56 million which was much lower than US$140 million (if every response ... is implemented)." / "The project was completed in early 2004 with no time and cost overrun."
- Type: X + M (assumed residual 5% and focus-group post-response impacts); the outcome is one project observation.
- Transferability: high in method (EMV of response alternatives, India, residual risk); the numbers are refinery-specific.
- Limitations: residual probability was an assumption, not a measurement; single project; no counterfactual.

**D15 - Hallowell & Gambatese (2009)** [ABSTRACT]
- Ref: Hallowell M.R., Gambatese J.A. "Construction Safety Risk Mitigation." J. Constr. Eng. Manage. 135(12), 1316-1323 (Crossref-verified). DOI: 10.1061/(asce)co.1943-7862.0000107. Closed.
- Verbatim: "the ability of each safety program element to mitigate a portion of each of the safety risk classes was quantified using the Delphi method." Most effective elements: "upper management support and commitment and strategic subcontractor selection and management".
- Numeric values NR in abstract. Type: X (Delphi). Relevance: the closest published template for eliciting "% of a risk class mitigated by a measure" from an expert panel (safety domain, not schedule).

**D16 - Baker, Ponniah, Smith (1999)** [ABSTRACT]
- Ref: "Risk response techniques employed currently for major projects." Construction Management and Economics. DOI: 10.1080/014461999371709. Closed.
- Verbatim: "risk reduction as a response to assessed risks is most commonly used by both sectors; and that the construction industry concentrates almost exclusively on reduction of financial risk." Survey of "over one hundred companies" (oil & gas vs construction).
- Type: S. Relevance: taxonomy/usage; no effectiveness values.

**D17 - Naji & Ali (2018)** [FULL read of abstract/intro; body only partially read]
- Ref: Naji H.I., Ali R.H. "Risk Response Selection in Construction Projects." Civil Engineering Journal 3(12), 1208-1221 (Crossref-verified; PDF header Dec 2017, Crossref date Jan 2018). DOI: 10.28991/cej-030950. Open access VERIFIED in text: "This is an open access article under the CC-BY license".
- Verbatim: "The investment (contractor, bank) strategy ... saves the cost about 30%, while the Mitigate (pay for advances with interest 0. 1) Strategy show saving the cost 40% and giving land to contractors show saving the cost 40% finally the BIM strategy show saving the cost 25%."
- Type: M (Gravitational Search Algorithm / PSO optimisation, Iraq). Relevance: response = advance payment to contractors, a cost effect not a delay effect. Treat as low-confidence: cost-saving figures come from an optimisation model, inputs not verified.

**D18 - Jaskowski, Biruk, Krzeminski (2023)** [FULL]
- Ref: "Proactive-reactive repetitive project scheduling method - the concept of risk consideration at the project planning and execution stage." Archives of Civil Engineering 69(4), 89-104. DOI: 10.24425/ace.2023.147649.
- Access: open access VERIFIED in text (CC BY-NC-ND 4.0 statement on first page).
- Mitigation: time buffers (proactive) + reactive measures "changing construction methods, employing extra resources, or working overtime", evaluated by simulation for a repetitive project of several buildings.
- Result (verbatim): "the lowest average cost of delays and delay mitigating measures was found for the total delay of 12 days and using the option to use accelerated modes of processes." and (verbatim) "This observation is of course case-specific".
- Type: M. Relevance: shows a pre/post (with/without reactive acceleration) simulation design for repetitive work where crews move through units (like masonry floors). No empirical effect size.

**D19 - Kammouh, Kok, Nogal, Binnekamp, Wolfert (2022)** [ABSTRACT; TU/e portal states CC BY (seen); full-text PDF returned 403]
- Ref: "MitC: Open-source software for construction project control and delay mitigation." SoftwareX 18, 101023. DOI: 10.1016/j.softx.2022.101023.
- Verbatim: "The MitC searches for the most cost-effective set of mitigation measures considering risk events and durations uncertainties of activities. Moreover, the MitC captures activity correlations and enables contractual penalty/reward schemes in the simulation."
- Numeric mitigation parameters NR (body not read). Type: M. Relevance: software precedent for simulating "risk events + corrective measures + cost".

**D24 - Zhang, Bai, Kang (2022)** [ABSTRACT; OA: CC BY 4.0 per Crossref publisher-deposited licence URL; body not seen - MDPI 403]
- Ref: "Risk Response Strategies Selection over the Life Cycle of Project Portfolio." Buildings 12(12), 2191 (Crossref-verified). DOI: 10.3390/buildings12122191.
- Verbatim: "The findings reveal that the risk response effects are maximized if the risks are responded to in earlier stages." / "As the effect of the strategy depends on the actual situation of the PP, the factors affecting the response effect of the strategies are recommended for further study."
- Type: M (dynamic Bayesian network + reward-risk optimisation, portfolio level). Relevance: supports time-dependence of response effect; no numbers seen.

### G. Delay causes/mitigation in India (topic 6) - qualitative only

**D21 - Prasad, Vasugi, Renganaidu (2019)** [ABSTRACT] "Analysis of causes of delay in Indian construction projects and mitigation measures." J. Financial Management of Property and Construction. DOI: 10.1108/jfmpc-04-2018-0020. Closed.
- Verbatim: "Semi-structured in-depth interviews were conducted with senior industry professionals to develop exhaustive mitigation measures." Top causes are finance-related (e.g. "Delay in settlement of claims, contractor's financial difficulties, delay in payment for extra work/variations by owner, late payment from contractor to subcontractor or suppliers"). Type: S/X, no effect sizes.

**D22 - Prasad, Vasugi, Venkatesan (2018)** [ABSTRACT] "Critical causes of time overrun in Indian construction projects and mitigation measures." Int. J. Construction Education and Research. DOI: 10.1080/15578771.2018.1499569. Closed. Same first author as D21 (the two are probably related outputs; not verified). Verbatim: "exhaustive mitigation measures for top causes of delay were also developed" as "a checklist of best practices"; effect sizes NR.

**D20 - Guha & Biswas (2008)** [ABSTRACT]
- Ref: "Monsoon risks for construction sites in India." 2008 IEEE Int. Conf. on Industrial Engineering and Engineering Management, pp. 1724-1727. DOI: 10.1109/ieem.2008.4738167 (Crossref verified). Closed.
- Verbatim: "A study has been made for a housing project ... Monte Carlos simulations were conducted to assess the impacts of time and cost that could be attributed to monsoon. It has been found that the monsoon has increased the project duration by about 5% and the cost by 12%. The study indicates that specific planning for monsoon impact for each project is a worthwhile proposition in cities like Kolkata, India."
- Type: E + M (one housing project, MC). This is the size of the hazard, NOT the effectiveness of a mitigation. Mitigation effect (monsoon scheduling/protection): not located.

---

### H. Added after checkpoint (D32-D37)

**D32 - Abbasian-Hosseini, Nikakhtar, Ghoddousi (2014)** [ABSTRACT] - the only bricklaying-specific lean/simulation result located
- Ref: "Verification of lean construction benefits through simulation modeling: A case study of bricklaying process." KSCE J. Civil Engineering 18(5), 1248-1260 (Crossref-verified). DOI: 10.1007/s12205-014-0305-9.
- Access: NOT open access - the Springer page I fetched states "This is a preview of subscription content" (OpenAlex's "hybrid/cc-by-nc-nd" flag is not supported by what I saw). Abstract only.
- Context: bricklaying process at one site; "Data required for constructing the simulation model were gathered from the construction site through work and time study techniques." Country not stated in the abstract.
- Mitigation: applying lean principles (removal of non-value-adding work) to the bricklaying cycle, evaluated by simulation before real-world application.
- Effect (verbatim): "Preliminary results show improvement opportunities exist in the bricklaying process due to a high share of non value-adding work. The results of lean principles implementation also reveal that lean principles can enhance the performance of the bricklaying process through more than 40% productivity improvement."
- Type: M (simulation model calibrated with site time-study data; the 40% is a predicted, not observed, improvement).
- Transferability: high in activity (bricklaying); country and crew size unknown from abstract. Limitations: not implemented on site; model assumptions not seen.

**D33 - Tokdemir, Erol, Dikmen (2019; online 2018)** [ABSTRACT; OpenMETU copy flagged cc-by-nc-nd in metadata, full text not fetched - server error]
- Ref: "Delay Risk Assessment of Repetitive Construction Projects Using Line-of-Balance Scheduling and Monte Carlo Simulation." J. Constr. Eng. Manage. 145(2), 04018132 (Crossref-verified). DOI: 10.1061/(asce)co.1943-7862.0001595.
- Verbatim: "risk scenarios are defined considering the sources of uncertainty and vulnerability of activities. Next, probability distributions are determined for the required number of labor-hours for each activity and for learning rates, and finally, the delay risk of the project is quantified using Monte Carlo simulation." "The findings reveal that the outputs of the proposed method may enable decision makers to estimate delay risk under various scenarios, formulate effective risk response strategies, and prepare contingency plans for resource utilization in repetitive tasks."
- Numbers: NR in abstract. Type: M. Relevance: repetitive-activity (floor-by-floor) MC framework with labour-hour and learning-rate distributions - a natural place to attach response-driven changes in labour-hour distributions.

**D34 - Said & El-Rayes (2011; online 2010)** [ABSTRACT]
- Ref: "Optimizing Material Procurement and Storage on Construction Sites." J. Constr. Eng. Manage. 137(6), 421-431 (Crossref-verified). DOI: 10.1061/(asce)co.1943-7862.0000307. Closed.
- Verbatim: "The model incorporates newly developed algorithms to estimate the impact of potential material shortages on-site because of late delivery on project delays and stock-out costs." Genetic-algorithm minimisation of "material ordering, financing, stock-out, and layout costs".
- Numbers: NR in abstract. Type: M. Relevance: an explicit model of buffer/ordering policy -> shortage -> delay -> cost trade-off.

**D35 - Koushki & Kartam (2004)** [ABSTRACT]
- Ref: "Impact of construction materials on project time and cost in Kuwait." Engineering, Construction & Architectural Management 11(2), 126-132 (Crossref-verified). DOI: 10.1108/09699980410527867. Closed.
- Verbatim: "The owners of 450 residential projects ... were personally interviewed." "The material selection-time, type of materials, their availability in the local market and the presence of a supervising engineer, all demonstrated a statistically significant impact on the on-time delivery of materials to construction sites."
- Effect sizes NR in abstract. Type: S/E (owner interviews). Relevance: the closest thing to evidence for "advance material selection/procurement" as a lever; direction only, no delay-days or probability.

**D36 - Lagos, Herrera, Alarcon (2019)** [ABSTRACT]
- Ref: "Assessing the Impacts of an IT LPS Support System on Schedule Accomplishment in Construction Projects." J. Constr. Eng. Manage. 145(10), 04019055 (Crossref-verified). DOI: 10.1061/(asce)co.1943-7862.0001691. Closed.
- Verbatim: "A sample of 50 projects was used to corroborate that projects that have higher PPC and PCR also have better performance, measured by the schedule accomplishment and number of noncompliances." Effect sizes NR. Type: E (cross-project correlation). Supports D29's direction.

**D37 - Ajayi, Bamisaye, Chinda et al. (2026)** [ABSTRACT; Crossref lists CC BY-NC-ND 4.0 licence URL]
- Ref: "The nexus between fatigue, schedule pressure, and their interconnected impacts on performance and sustainability." Results in Engineering 30, 110516 (Crossref-verified). DOI: 10.1016/j.rineng.2026.110516.
- Verbatim: "The results reveal strong interdependencies among fatigue, overtime, and schedule pressure, factors that collectively impact productivity." "improving task accuracy while carefully managing fatigue, overtime, and schedule pressure can substantially increase productivity and reduce rework". System-dynamics model (validation "R-score of 0.991, an R2 of 0.911").
- Effect sizes for a mitigation: NR. Type: M. Relevance: supports modelling overtime -> fatigue -> rework as a coupled secondary risk (with D10).

---

## 2. Bibliographic-only items (existence verified, content NOT seen - do not cite for effect sizes)

Existence and bibliographic data verified via Crossref/OpenAlex; publisher abstract elided/inaccessible; I did not read them.
- Zuo & Zhang (2018), "Selection of risk response actions with consideration of secondary risks", Int. J. Project Management 36(2), 241-254. DOI 10.1016/j.ijproman.2017.11.002. (Semantic Scholar machine-generated TLDR, NOT the authors' abstract: "secondary risk plays an important role in the process of RRA selection".)
- Fan, Lin, Sheu (2008), "Choosing a project risk-handling strategy: An analytical model", Int. J. Production Economics 112(2), 700-713. DOI 10.1016/j.ijpe.2007.06.006. (Machine TLDR only: "A conceptual framework was constructed that defines the relationship between risk-handling strategy and relevant project characteristics".) A green repository copy exists at NTU (ntur.lib.ntu.edu.tw) but it returned 403.
- Zhang & Fan (2014), "An optimization method for selecting project risk response strategies", Int. J. Project Management 32(3), 412-422. DOI 10.1016/j.ijproman.2013.06.006.
- Seyedhoseini, Noori, Hatefi (2009), "An Integrated Methodology for Assessment and Selection of the Project Risk Response Actions", Risk Analysis 29(5), 752-763. DOI 10.1111/j.1539-6924.2008.01187.x. (Machine TLDR only: "selecting a set of RA that minimizes the undesirable deviation from achieving the project scope".)
- Parsaei Motamed & Bamdad (2021), "A multi-objective optimization approach for selecting risk response actions: considering environmental and secondary risks", OPSEARCH. DOI 10.1007/s12597-021-00541-5.
- Bai, Xie, Lin (2024), "Dynamic selection of risk response strategies with resource allocation for construction project portfolios", Computers & Industrial Engineering. DOI 10.1016/j.cie.2024.110116.
- Chen, Lu, Han (2022), "A Bayesian-driven Monte Carlo approach for managing construction schedule risks of infrastructures under uncertainty", Expert Systems with Applications. DOI 10.1016/j.eswa.2022.118810.

(Zhang, Bai and Fan et al. named in the brief: only D24 above and the bibliographic items were reachable; their internal "effectiveness scales" are therefore NOT reported.)

---

## 3. Other papers seen (context only, not counted among D01-D37)

- Enshassi, Mohamed, Mayer, Abed (2007), "Benchmarking masonry labor productivity", Int. J. Productivity & Performance Management 56(4), 358-368, DOI 10.1108/17410400710745342 [ABSTRACT]: verbatim "the baseline productivity of masonry works in Gaza seems to range from 0.29 to 0.80 work-hours per square meter" (9 projects). Baseline, not mitigation.
- Hassoon et al. (2025), J. Infrastructure Preservation and Resilience 6, art. 3, DOI 10.1186/s43065-025-00116-4 [ABSTRACT; Crossref lists CC BY 4.0]: brickwork/housing skeleton tasks, Iraq; RII: "planning (RII = 0.874), team size (RII = 0.856)". Ranking only.
- Thamboo, Zahra, Navaratnam, Asad, Poologanathan (2021), "Prospects of Developing Prefabricated Masonry Walling Systems in Australia", Buildings 11(7), 294, DOI 10.3390/buildings11070294 [ABSTRACT; Crossref lists CC BY 4.0]: verbatim "Conventional masonry construction is labour-intensive and time-consuming; therefore, prefabrication can be an effective solution to accelerate the masonry construction"; measured effect given is environmental only ("nearly 30% and 15% savings, respectively, in terms of energy saving and CO2 emissions"). Time saving from prefabricated masonry: NR in abstract.
- Love & Edwards (2004), "Forensic project management: The underlying causes of rework in construction projects", Civil Eng. & Environmental Systems 21(3), 207-228, DOI 10.1080/10286600412331295955 [ABSTRACT]: two longitudinal case studies; "strategies for reducing the incidence of rework are identified"; numbers NR.
- Abhirami (2026), "Integration of LPS and Primavera ... Residential Building Projects", IJSREM, DOI 10.55041/ijsrem63203 [FULL]: claims "improvements in planning reliability, coordination, productivity, and schedule performance" but I found NO numbers in the text; not usable as evidence. (Low-tier journal.)
- Itendrakumar (2026) prefabrication profitability dissertation (Haryana): abstract contains implausible/unsourced figures; NOT used.

---

## 4. What the papers say about HOW a response's effect is represented / elicited (topics 2-3)

Only what I could verify in text I saw (abstract or full text):
- Probability-and-impact, with overlap and secondary risk: D13 (Ben-David & Raz 2001) - "representation of the overlapping effects of multiple risk reduction actions and of the impacts of secondary risk events" (abstract). Parameter values and elicitation: not seen.
- Residual risk by assumption + focus group: D14 (Dey 2011) - residual probability "would be 5%" if all responses are undertaken (assumed), post-response time/cost effects "estimated from cumulative experience of the risk management group through focus group"; alternatives compared by EMV in a decision tree. This is the closest match to the project's pre/post + EMV design, and is in an Indian setting.
- Expert-panel quantification of "the ability of each ... element to mitigate a portion of each of the ... risk classes" (Delphi): D15 (safety domain; the values themselves not seen).
- Simulation search over corrective measures with cost and penalty/reward: D19 (MitC), D18 (buffers + accelerated modes), D25 (20,736 crashing scenarios).
- Time-dependence of response effect: D24 - "risk response effects are maximized if the risks are responded to in earlier stages".
- Response taxonomy: D14 lists "avoid, ... reduce, ... transfer and ... absorb"; D16 finds "risk reduction ... is most commonly used" in construction and oil & gas. PMBOK "opportunity" responses: not located in any paper I could read.
- Terms "risk reduction factor" and "response effectiveness scale": not located in any accessible text. The papers that most likely define such parameters (Zuo & Zhang 2018; Fan et al. 2008; Zhang & Fan 2014; Seyedhoseini et al. 2009) were paywalled/403 - their content is NOT reported.
- Matching response type to risk type (topic 3): only D14 (responses derived per work-package risk) and D16 (usage survey) - no quantitative matching rule located.

## 5. Search log (queries and counts)

Tools: (a) WebSearch - 11 successful queries in this run, then the session quota (200) was exhausted; results were snippet-level and were used only to find candidate titles, never as evidence. (b) OpenAlex API `title_and_abstract.search` (counts below are OpenAlex hit counts; the top 8-15 by relevance were screened). (c) Crossref API (DOI/bibliographic verification of every DOI cited). (d) Semantic Scholar API (abstract/TLDR). (e) Direct PDF/HTML fetch with text extraction (pypdf) for OA/repository copies. Blocked: MDPI, ScienceDirect, TandF, ResearchGate, ASCE, several university repositories (403/500).

WebSearch queries (11): "risk response effectiveness schedule risk Monte Carlo residual risk secondary risk construction project"; "Ben-David Raz 2001 integration of project risk management response actions schedule Monte Carlo"; "last planner system effect on plan percent complete productivity improvement building construction case study"; "brick masonry productivity improvement India construction delay mitigation labour shortage monsoon"; "prefabrication versus conventional construction time saving percent case study buildings open access"; "AAC blocks versus clay brick masonry construction time productivity comparison India study"; "overtime effect on labor productivity construction masonry percent loss study"; "risk response effectiveness expert elicitation risk response probability reduction impact reduction construction schedule model"; "productivity study AAC block masonry versus brick masonry mason output m2 per day time study construction site"; "monsoon rainfall impact on construction schedule India delay days quantified study building projects mitigation"; "Monte Carlo simulation construction schedule risk mitigation measures reduced delay probability before and after mitigation case study". (Numbers in commercial-blog snippets about AAC productivity were seen only as snippets and are deliberately NOT recorded.)

OpenAlex title_and_abstract queries with hit counts:
- risk response construction project schedule simulation: 56
- risk response effectiveness construction: 1,393
- secondary risk response project: 3,175
- risk response strategy selection project risk: 1,373
- risk response actions secondary risk selection: 576
- risk response techniques employed construction: 392
- choosing a project risk-handling strategy: 231
- project risk management survey risk response reduction transfer avoidance retention construction: 3
- delay mitigation strategies scenario simulation construction schedule: 15
- mitigation Monte Carlo simulation project duration before and after mitigation residual risk: 0
- system dynamics schedule pressure overtime rework construction: 2
- last planner system construction: 1,237; last planner productivity delay reduction building: 9; planning reliability productivity last planner: 45; constraint management last planner schedule performance: 15
- masonry productivity: 387; brickwork productivity improvement: 1; bricklaying productivity: 90; thin-joint masonry productivity: 5; crew composition masonry productivity: 2; brickwork defects quality control: 5; brick masonry labour productivity India: 0
- AAC block masonry: 257; autoclaved aerated concrete masonry productivity: 1; autoclaved aerated concrete blocks construction time labour productivity masonry: 0; AAC blocks brick masonry cost time comparison building India: 1; aerated concrete blocks construction speed: 10; alternative masonry construction speed productivity blocks interlocking: 0; masonry construction time saving: 64
- just-in-time material delivery construction delay: 72; material management construction delay reduction buffer: 18; inventory buffers construction labor performance: 5; material shortage productivity loss construction: 42; material procurement delay construction: 580; supplier selection construction delay risk mitigation: 5; supplier diversification construction: 249
- overtime productivity construction: 185; shift work labor productivity construction: 163; crew size productivity construction: 87; schedule crashing time-cost trade-off construction: 43; congestion crowded work space productivity loss construction: 0
- prefabrication construction time reduction case study: 45; off-site construction time savings: query hit the rate limit (no result)
- workflow variability labor productivity construction reducing variability: 3; rework reduction quality management construction: 89
- incentive productivity construction: 988; financial incentives construction workers: 273; construction workers training productivity: 761; training skill upgrading construction workers productivity: 12; construction skill training India workers: 87; skilled labour shortage construction India: 18; labour shortage India construction strategies mitigation: 4; delay Indian construction projects mitigation measures: 18
- rainfall weather delay construction productivity: 12; rainfall construction productivity: 390; weather delay construction schedule risk: 133; monsoon construction delay India: 12; monsoon construction: 1,936; monsoon risks construction sites: 92; site layout planning productivity improvement construction: 29
- Rate-limited (429, no result): "risk response actions effectiveness project schedule optimization"; "incentive scheme construction labour productivity" (replaced by the incentive queries above); "ready-mix mortar construction productivity"; "off-site construction time savings".

Note: OpenAlex `title_and_abstract.search` returns full-text-like noise for generic words; hit counts above are therefore not a measure of literature size, only of screening effort.

## 6. Table: mitigation measure -> quantified evidence found (Y/N) -> paper IDs -> what still requires expert/user input

Legend: Y = a numeric effect from a real project/simulation was seen in text; P = partial (bundle, or number is variance-explained, or hazard size only, or direction only); N = not located.

| Mitigation measure | Quantified evidence? | Paper IDs | What still requires expert / user input |
|---|---|---|---|
| Buffer stock / just-in-time material management | P - only inside a bundle (D03: task duration "= 30% reduction", PPC ~55%->~80%); D11 shows an optimum buffer size (no numbers); D34/D18 are models. Stand-alone masonry effect: not located | D03, D11, D18, D34 | Reduction in probability of "material shortage" event; reduction in shortage duration; carrying cost; storage/weather-damage secondary risk. Should be modelled as non-monotonic (D11). |
| Supplier diversification | N - not located | (D35 gives direction for material availability/selection time only) | Entirely expert-elicited: p and delay-impact reduction; price premium; quality-variation secondary risk |
| Advance material procurement | N for delay effect (D35: direction only, statistically significant; D17: cost-saving figures from an optimisation model in Iraq, for advance-payment strategy) | D35, D17, D01 (material unavailability was the top cause of failed assignments) | p' and F' for material-delay risk; capital/financing cost; risk of storage damage/theft |
| Crew-size increase / crashing | P - AlJassmi 2023 already held; here only the congestion side effect is quantified in simulation (D12) | D12, D10, D25, D18 | Productivity loss per added mason (congestion), cost premium, availability of extra masons |
| Overtime / shift work | Y (P) - D09: "productivity loss ... ranges from -11 to 17%" for shift work; D07: moderate occasional overtime "did not have a significant impact"; D08 direction only. (Lendra 2026 already held) | D07, D08, D09, D10, D37 | Local overtime multipliers for masonry in India; fatigue -> rework and safety probabilities (secondary risks) |
| Mechanisation / prefabrication / block substitution | Y (P for masonry) - D04 lab: productivity +60-120% for interlocking/dry-stack masonry; D05: crew 22 -> 18, cycle 17 -> 4 days/house (survey, IBS); D06: -34% time, -19% cost, +7% productivity (prefab, NZ). AAC-specific peer-reviewed productivity: not located | D04, D05, D06 (context: Thamboo 2021 in Sect. 3) | AAC vs clay-brick productivity in local conditions; block-supply reliability; cracking/rework and mortar-type changes; cost delta |
| Training / skill upgrading | N - direction only | D31, D23 | Effect on productivity and rework probability; training cost/time; attrition of trained workers |
| Incentive schemes | P - D27: incentives "accounted for 6% to 26% of the variations in output" (variance explained, NOT a productivity gain); D01: bonus period PPC peaked at 121% (single case) | D27, D01 | Productivity multiplier under incentive; cost of incentive per m3/m2; quality trade-off (rush -> rework) |
| Better site layout / logistics | P - D03 (bundle, ~10-20% productivity index rise incl. layout); D12 (work zones cut simulated spatial conflicts 68.3%) | D03, D12 | Local layout gains for masonry (vertical transport, mortar/brick staging) |
| Weather protection / monsoon scheduling | N for mitigation effect. Hazard size only: D20 (monsoon +~5% duration, +12% cost, one Kolkata housing project); D26 (heat +3-38% duration, Oman) | D20, D26, D14 (lists "Scheduling the project by accommodating seasonal calamities" as a response, effect not separable) | Residual delay days after covering/rescheduling; cost of covers/dewatering; secondary risk of schedule compression after the monsoon |
| Rework reduction / quality control | N for masonry. Bundle only: D03 rework incidents 15 -> 12 (20%) | D03 (context: Love & Edwards 2004 in Sect. 3) | Rework probability and rework days per defect type for masonry/plaster; inspection cost |
| Lean / Last Planner | Y - D01: PPC 37.5% -> 85% (India); D02: 60% -> 85%, "12-20%" less delay (India, survey-type); D03: 55% -> 80% (Canada); D30: 52.8% -> 72.25% over 8 weeks (India); D28/D29/D36: PPC/constraint removal correlate with productivity/schedule | D01, D02, D03, D30, D28, D29, D36 | PPC is reliability, not delay: conversion of PPC change into delay-days/probability reduction is NOT provided by any paper seen except D02's "12-20%" (weak). Needs expert judgement. |
| Bricklaying-specific lean improvement | Y (simulation) - D32: "more than 40% productivity improvement" | D32 | Whether the 40% holds outside that site; implementation cost |
| Response effectiveness representation, residual risk | Y (method) - D13, D14 (5% residual assumed; focus-group post-response impacts), D15 (Delphi), D19, D24 | D13, D14, D15, D19, D24 | Every effectiveness parameter must be elicited from the user/experts; no literature value is transferable as-is |
| Secondary risks / side effects | P - direction (overtime -> rework/fatigue D10, D37; crashing -> congestion D12) with only D12 numeric | D10, D12, D37 | Probability and impact of each secondary risk per alternative |
| Before/after (pre/post) simulation designs | Y (method) - D14 (expected 4.81 months delay pre-response; project later "completed ... with no time and cost overrun"), D18, D19, D25, D32 | D14, D18, D19, D25, D32 | Choice of distributions for F'; correlation between responses (overlap, D13) |
| Response taxonomy / matching to risk type | P - avoid/reduce/transfer/absorb (D14), reduction most used (D16); PMBOK opportunity responses not located | D14, D16 | Mapping of each of the project's risks to a response class |

## 7. Implications for the decision-support model (design guidance, not data)

1. No paper I could read supplies a transferable "risk reduction factor" for a masonry-specific mitigation. Treat p -> p' and F -> F' for every alternative as expert-elicited inputs (e.g. min / most likely / max of the reduction), and use the literature numbers above only as plausibility bounds or sanity checks with their context stated.
2. Keep the design close to D14 (India): probability and impact after response per alternative, cost per alternative, EMV comparison; and state explicitly, as D14 did, when a residual value is an assumption.
3. Model side effects explicitly: overtime -> rework/fatigue (D10, D37), crashing -> congestion (D12), buffers -> non-monotonic benefit (D11).
4. Do not read PPC gains as delay reductions (D01, D02, D03, D30 all report PPC or bundled outcomes).
5. D27's "6% to 26%" is variance explained; D09's "-11 to 17%" has an ambiguous sign convention in the abstract; D02's productivity range differs between abstract and table; D04 is laboratory and for interlocking blocks. Flag all four when used.
6. India-specific quantified mitigation evidence is thin: D01, D02, D30 (LPS), D14 (risk-response EMV), D20 (monsoon hazard size), D21/D22 (qualitative mitigation checklists), D23/D31 (labour factors). No Indian study located that quantifies monsoon protection, supplier diversification, advance procurement, AAC productivity or masonry rework reduction.

## 8. Not located (stated explicitly)

- Supplier diversification effect on delay probability: not located.
- Advance procurement effect on delay probability/duration: not located (only direction, D35).
- Monsoon-protection/scheduling effect size: not located (hazard size only, D20).
- Peer-reviewed measured AAC-vs-clay-brick masonry productivity/time saving: not located (only non-peer-reviewed web claims were seen as snippets; not recorded).
- Site-layout effect on masonry productivity alone: not located.
- Rework-reduction/QC effect for masonry: not located.
- Training effect size on masonry productivity: not located.
- "Risk reduction factor" / "response effectiveness" scales as defined in Zuo & Zhang, Fan et al., Zhang & Fan, Bai et al.: content not accessible.
- Conversion factor from PPC improvement to delay reduction: not located.

## 9. Housekeeping

- All DOIs cited were resolved via Crossref (bibliographic data matched title, journal and year), except D01 (no DOI printed) and the bibliographic-only items where noted.
- Open-access statements: VERIFIED in text for D02, D17, D18; Crossref-deposited licence URL only (paper body not seen) for D06, D24, D25, D26, D19, D37, Hassoon 2025, Thamboo 2021; repository "OA per metadata" without licence text for D07, D33; NOT open access: D32 (Springer preview), D12 (embargoed). Everything else is closed or free-to-read without a verified licence.
- Intermediate files (PDF text extractions) are in the session scratchpad only; no other project files were modified.
