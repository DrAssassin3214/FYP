# Topic Group C - Economics and decision analysis (research notes)

Project context: AI-assisted, literature-grounded Monte Carlo + risk-matrix + EMV decision-support system for ONE activity (brick masonry, India). Decision rule under test: TEC_m = C_mitigation + E[C_residual] subject to a deadline-probability constraint.

Status of this file: CHECKPOINT 3 (rewritten after a tool rate-limit interruption; entries C22-C27 added after tools resumed). Nothing below was invented. Where I could not see a number or equation in text I fetched, I write NR (not reported / not retrieved) or NC (not checked).

## 0. Integrity notes and limits of this pass (read first)

- Access levels used in every entry:
  - FULL = I read the paper text (PDF extracted locally) and quote equations/numbers from it.
  - PAGE = I read only the publisher/PMC/SciELO landing page as summarised by the fetch tool (numbers below are from that page summary, not from the PDF).
  - ABSTRACT = I saw only an abstract or metadata. No equations or numbers beyond the abstract are given.
  - LOCAL = read from the copy already held in C:\Users\Omkar\Desktop\FYP\Research_Papers (not modified). These four (C18-C21) may overlap with other topic groups.
- DOI verification method is stated per entry: CROSSREF (resolved through the Crossref API), IN-PDF (DOI printed in the PDF I read), PAGE (printed on the landing page), OPENALEX (metadata only), URL-DERIVED (taken from a publisher URL, not resolved).
- Open access is claimed only where I saw a licence statement in the PDF/page or in Crossref. Where sources conflict, the conflict is reported.
- Tool limits hit: (a) the WebSearch quota for the session reached 200/200 (shared, not only my calls) so the last three planned searches were refused; (b) WebFetch returned a session-limit error for a while (reset time given as 8:20pm IST) and later worked again; (c) OpenAlex and Semantic Scholar APIs then returned HTTP 429 (OpenAlex Retry-After about 9 hours), HAL returned an "Access Denied" bot-protection page, and a few publisher hosts refused connections. I did NOT try to route around any of these limits. Total: 27 numbered papers (C01-C27) + 1 grey-literature item (G01), of which 9 are ABSTRACT/PAGE only (C04, C05, C07, C10, C13, C14, C15, C16, C17).
- DOI verification status (Crossref API = title, authors, journal, year matched): CONFIRMED for C01, C02, C03, C04, C05, C06 (the Crossref record for C06 is the online-first record dated 14 March 2018 with no volume/issue; the printed citation is vol. 26(3), 2019), C08, C09, C10, C11, C12, C13 (Crossref also gives licence CC BY-NC 4.0 for C13), C14, C17. NOT FOUND in Crossref (HTTP 404): C15 - the DOI printed on the journal page (10.22059/ijms.2020.272892.673461) did not resolve there. NOT CHECKED against Crossref (rate limit / not attempted): C07 (DOI identical on the Springer page and in a search result), C16 (DOI from OpenAlex only), C18-C27 (DOI printed in the PDF or on the page that I read).
- mdpi.com returned 403 to WebFetch. mdpi-res.com PDF URLs worked; Crossref API worked for metadata and licences; OpenAlex worked until it was rate-limited; DOAJ API worked for counts.
- Statements I could only see in a search-engine summary (not in fetched text) are listed in section 7 as UNVERIFIED and are not used as evidence.

## 1. Search strings used and counts

### 1a. WebSearch (27 successful queries by me; 4 further calls failed on a JSON error and were not counted; 3 were refused at quota)
Counts of hits are not exposed by WebSearch (it returns about 9-10 links per query); the per-query link count was 9-10 each.

1. Project risk costs: estimation overruns caused when using only expected value ASCE 2022
2. Ben-David Raz 2001 "An integrated approach for risk response development in project planning" Journal of the Operational Research Society
3. daily delay cost construction components site overhead idle labour equipment financing liquidated damages calculation open access
4. contingency estimation Monte Carlo P80 P90 percentile construction project cost open access
5. delay cost per day construction projects India liquidated damages overhead idle equipment case study delay cost quantification journal
6. "expected monetary value" risk limitations variance risk neutrality project risk management construction paper
7. Monte Carlo simulation schedule delay converted to cost daily indirect cost liquidated damages probability distribution total cost building construction
8. risk response selection cost-benefit expected utility risk aversion project risk decision tree construction risk response optimization
9. "Understanding project cost contingency estimation: A holistic risk perspective" systematic literature review six-element framework
10. Vegas-Fernandez "expected value" risk cost "three times" underestimates contingency Monte Carlo enlargement factor abstract
11. Paquin 2022 coherent risk measure project cost probability distributions cost overrun contingency reserve
12. Conditional Value-at-Risk project scheduling cost overrun construction contingency schedule risk arxiv OR mdpi OR pmc
13. chance-constrained programming risk response selection project deadline probability constraint stochastic project scheduling open access
14. fuzzy TOPSIS risk response strategy selection construction projects mdpi
15. AHP TOPSIS criticism rank reversal multi-criteria decision making construction risk when cost minimisation sufficient
16. Monte Carlo simulation risk register expected value versus simulated cost contingency construction project probabilistic cost estimate (domains: mdpi, ncbi, arxiv)
17. liquidated damages delay cost daily rate Monte Carlo simulation construction schedule risk cost of delay (same domains)
18. risk response strategy selection budget constraint optimization construction residual risk mitigation cost (same domains)
19. delay costs Indian construction projects time overrun cost overrun quantification per day (same domains)
20. Marc Bara "Enhanced Monte Carlo simulation for project risk analysis" time-shifted risks dependency modeling arxiv OR ssrn OR pdf
21. Rockafellar Uryasev "Optimization of conditional value-at-risk" pdf Journal of Risk 2000
22. Velasquez Hester "An analysis of multi-criteria decision making methods" International Journal of Operations Research 2013 pdf
23. CPWD general conditions of contract clause 2 compensation for delay 1.5% per month of delay maximum 10% tendered value
24. Fang Marle "integrated framework for risk response planning under resource constraints" large engineering projects HAL pdf
25. cpwd.gov.in General Conditions of Contract 2023 Clause 2 "compensation for delay" "per month of delay" "computed on per day basis" tendered value
26. Baccarini Love statistical characteristics of cost contingency in water infrastructure projects JCEM 2014 Wakeby P50 P80
27. risk-neutral expected value criterion inadequate project risk decisions utility function risk-averse decision maker construction contractor expected utility theory paper

Refused at quota (never executed): "expected monetary value" underestimates tail risk ...; Touran probabilistic model for cost contingency; schedule contingency P80 Monte Carlo ... time contingency delay penalty.

### 1b. OpenAlex API discovery queries (filter is_oa:true; the meta.count is the number of matching works in OpenAlex; first 15 examined)
| Query text | Year filter | meta.count |
|---|---|---|
| "risk response" selection construction projects optimization | 2012-2026 | 2,102 |
| "conditional value at risk" construction project schedule cost | 2010-2026 | 1,120 |
| "liquidated damages" delay cost simulation construction | 2008-2026 | 306 |
| "expected monetary value" risk construction contingency | 2008-2026 | 156 |
Three more OpenAlex queries (delay cost overhead financing per day; contingency Monte Carlo P80; expected utility risk aversion construction) failed on the session limit and a repeat of the chance-constrained query was later refused with HTTP 429 (Retry-After about 9 hours); counts NC.

### 1c. Other index queries (after tools resumed)
| Source | Query | Result count | Notes |
|---|---|---|---|
| Crossref search API | chance constrained project scheduling deadline probability construction (has-license, from 2010) | 580,507 (unfiltered bibliographic match, not meaningful) | top 10 were paywalled or not on topic; none used |
| arXiv API | "project scheduling" AND (chance constraint OR chance-constrained OR CVaR) | 0 | nothing usable |
| DOAJ API | "liquidated damages" AND "Monte Carlo" AND construction | 0 | |
| DOAJ API | "risk response" AND construction | 82 | first 14 shown were mostly risk-identification papers; none read |
| DOAJ API | "expected monetary value" AND construction | 5 | led to C27 (Hong et al. 2023); the Facta Universitatis payoff-matrix paper (Mirkovic et al. 2020, DOI 10.2298/FUACE201117020M) also appeared but its host refused the connection, so it was not read |
| Semantic Scholar API | risk response expected utility construction | refused (HTTP 429) | NC |

## 2. Index of entries

| ID | Citation (short) | Access | Topics |
|---|---|---|---|
| C01 | Hadad & Keren 2025, JRFM | FULL, CC BY 4.0 | 4, 5, 6, 3 |
| C02 | Azimi Vaziri, Oztemir, Pehlivan 2026, Buildings | FULL, CC BY 4.0 | 1, 6, 7 |
| C03 | Ding et al. 2024, Buildings | FULL, CC BY 4.0 | 6, 3 |
| C04 | Vegas-Fernandez 2022, J. Manage. Eng. | ABSTRACT, closed | 2, 3 |
| C05 | Paquin et al. 2022, JCEM | ABSTRACT, closed | 3, 6, 7 |
| C06 | Shoar & Nazari 2019, Scientia Iranica | FULL, diamond OA | 4, 5 |
| C07 | Ben-David & Raz 2001, JORS | ABSTRACT (+ two secondary descriptions), paywalled | 4 |
| C08 | Zhang, Li, Sun, Ning 2025, IJMPB | FULL (accepted manuscript) | 2, 3 |
| C09 | Rockafellar & Uryasev 2000, J. Risk | FULL (author preprint), non-construction | 6 |
| C10 | Aires & Ferreira 2018, Pesquisa Operacional | PAGE, CC BY 4.0 | 5 |
| C11 | Anil, Kassim, Varghese 2021, AIJR Proc. | FULL, CC BY-NC 4.0 | 1 (India) |
| C12 | Alshboul et al. 2022, Sustainability | FULL, CC BY 4.0 | 1 |
| C13 | Bara Iniesta 2025, Appl. Oper. Anal. | ABSTRACT, OA per OpenAlex | 3, 7 |
| C14 | Aljorany & Mahjoob 2024, ETASR | PAGE, CC BY 4.0 | 4 |
| C15 | Mokhtari & Aghagoli 2020, IJMS | ABSTRACT | 4 |
| C16 | Tripathi, Hasan, Jha, Jain 2022, JLADREC | ABSTRACT, OA unverified | 1 (India) |
| C17 | Namazian et al. 2019, IJERPH | PAGE, CC BY 4.0 | 7 (negative) |
| C18 | AlJassmi, Abduljalil, Philip 2023, JAABE | LOCAL, CC BY 4.0 | 1, 4, 7 (brickwork) |
| C19 | Van Basten, Firstyanandara, Crevits 2026, Int. J. Technol. | LOCAL | 1, 4 |
| C20 | Starczyk-Kolbyk & Jedras 2025, Appl. Sci. | LOCAL | 2 |
| C21 | Zavala et al. 2025, Future Transp. | LOCAL | 3, 6 |
| C22 | Chatterjee, Zavadskas, Tamosaitiene, Adhikary, Kar 2018, Symmetry | FULL, CC BY | 5 |
| C23 | Zhang, Bai, Kang 2022, Buildings | FULL, CC BY 4.0 | 2, 4 |
| C24 | Choi & Lee 2024, ISARC proceedings | FULL, freely downloadable, no open licence seen | 1, 4, 7 |
| C25 | Ahmadi, Behzadian, Ardeshir, Kapelan 2017, JCEM | FULL, CC BY 4.0 | 5, 4 |
| C26 | Buertey, Abeere-Inga, Kumi 2012, JCPMI | FULL, CC BY-NC 4.0 (page) | 3 |
| C27 | Hong, Eum, Song 2023, Appl. Sci. | FULL, CC BY | 2, 1, 4 (EMV incl. delay LD) |
| G01 | Zack & Badala (Navigant), Pricing Contractor Delay Costs | FULL, grey literature, year NR | 1 |

## 3. Entries

### C01 - Hadad, Y. and Keren, B. (2025). Risk-Response Budgeting: A Financial Optimization Approach to Project Risk Management. Journal of Risk and Financial Management, 18(3), 160.
- DOI: 10.3390/jrfm18030160 (IN-PDF citation line). Access: FULL; licence CC BY 4.0 printed in the PDF (open access verified).
- Context: risk-response budget allocation for an office building (about 1,500 m2, budget USD 3.8 million, planned 18 months, 13 responsible risks); Monte Carlo simulation feeding integer linear programming; several alternative objective functions then combined by counting.
- Key equations (transcribed from the PDF; n risks, j = 1..n; K simulations; i = 1,2,3 = cost, time, quality):
  - (1) E_ij = (a_ij + 4 m_ij + b_ij)/6 ; Var_ij = ((b_ij - a_ij)/6)^2  (a, m, b = optimistic, most likely, pessimistic impact of factor i of risk R_j).
  - (2) z_ijk = NORM.INV(x, E_ij, Var_ij), x ~ U(0,1) (as printed).
  - (3) P_jk = x (P_max,j - P_min,j) + P_min,j  (occurrence probability drawn between expert bounds).
  - (4) L_j,0 = (1/K) sum_k P_jk sum_i z_ijk = (1/K) sum_k L_j,0,k  (average weighted impact = simulated EMV of risk j).
  - (5) Var_j,0 = sum_k (L_j,0,k - L_j,0)^2 / K.
  - (6) S_jk = x (S_max,j - S_min,j) + S_min,j  (random mitigation rate); L_j,1,k = L_j,0,k (1 - S_jk); (7), (8) give L_j,1 and Var_j,1 (residual expected impact and variance).
  - (9) Max sum_j Y_j u_j - sum_j Y_j C_j  s.t. sum_j Y_j C_j <= B, Y_j in {0,1}, with u_j = L_j,0 - L_j,1 (net expected saving; equivalent to minimising TEC given the budget).
  - (10) same without the -C term (maximise expected saving under budget).
  - (11) Min sum_j (X_j Var_j,0 + Y_j Var_j,1), X_j + Y_j = 1, budget constraint (variance).
  - (12) minimise P(L > a) with P(L>a) = 1 - P(z <= (a - sum(X_j L_j,0 + Y_j L_j,1)) / sqrt(sum(X_j Var_j,0 + Y_j Var_j,1))), normal approximation, risks uncorrelated (non-linear, solved by Excel Solver).
  - (13) minimise maximum regret; (14) minimax; (15) Max sum_j Y_j S_j s.t. budget, where S_j = number of criteria that select R_j.
  - Stated assumptions: risk impacts uncorrelated in 4.3/4.4 (variances add).
- Key numbers: 13 risks, total unmitigated impact 2,365 (thousand USD, Table 2) and total response cost 625 against an available response budget of 300 (thousand USD); 500 Monte Carlo runs per risk; Table 3 sums: E_j,0 = 1,354.92, E_j,1 = 627.73, expected saving 727.19. Criterion 1 optimum: net expected saving 117.86 thousand USD selecting R1, R3, R7, R8, R9, R12. All six criteria select R1, R7, R8; none select R4 or R13. Final weighted plan (15): R1, R3, R6, R7, R8, R9.
- Arithmetic check (mine): the six risks selected under criterion 1 cost 50+30+50+70+40+50 = 290, not the 300 the text says was "entirely used"; savings sum to 407.86 so 407.86 - 290 = 117.86 is consistent with the reported optimum. Minor text inconsistency in the paper.
- Limitations stated: quality of subjective expert estimates; identifying statistical dependencies between random variables. Also: normal approximation and independence in (12); ILP is NP-hard for large n (paper's own statement); single case; data not public.
- Also gives a secondary description of Ben-David and Raz (2001) and Kuo et al. (2019) as approaches that minimise total risk cost, and lists response optimisation objectives in the literature (maximise response effect, minimise response cost, maximise expected utility).
- Design decision supported: (i) TEC-type objective with a budget cap is a published, working formulation (eq. 9-10); (ii) residual risk modelled as multiplicative mitigation rate S drawn from an expert range (eq. 6); (iii) P(L>a) is a legitimate alternative objective, showing the selected set changes with the criterion; (iv) run-count of 500 is per-risk in their case (not a convergence proof).

### C02 - Azimi Vaziri, M., Oztemir, A.E. and Pehlivan, S. (2026). Stochastic Risk-Aware Time-Cost Optimization of Construction Schedules Using a Hybrid GA-GWO Algorithm with Integer Crash-Day Decisions. Buildings, 16(15), 3091.
- DOI: 10.3390/buildings16153091 (IN-PDF). Access: FULL; CC BY licence statement in the PDF. Published 4 August 2026 (per the PDF).
- Context: 30-activity construction project reconstructed from Microsoft Project data; triangular activity durations; Monte Carlo; CVaR-oriented risk-adjusted duration and cost.
- Key equations (transcribed):
  - (13) C_I(x) = h T(x)  (indirect cost; h = indirect cost per project day; T = project duration).
  - (14) C_L(x) = l max(0, T(x) - T_c)  (liquidated damages; l = LD per delayed day; T_c = contractual duration threshold).
  - (12) C_D(x) = sum_i (C_i^0 + c_i x_i)  (direct cost with crash cost c_i per crash day x_i).
  - (15)/(16) C_T(x) = C_D(x) + C_I(x) + C_L(x).
  - (26) CVaR_alpha^T(x) = E[ T~(x) | T~(x) >= VaR_alpha^T(x) ]; (27) same for cost; VaR_alpha is the alpha-quantile of the simulated distribution.
  - (28) T_R(x) = (1 - lambda_T) E[T(x)] + lambda_T CVaR_alpha^T(x); (29) C_R(x) = (1 - lambda_C) E[C_T(x)] + lambda_C CVaR_alpha^C(x)  (lambda = risk-aversion coefficients).
  - (30)-(32) normalised objective F(x) = w_T (T_R/T_R(x0))^beta_T + w_C (C_R/C_R(x0))^beta_C + gamma (T_R/T_R(x0)) (C_R/C_R(x0)).
- Key numbers: h = USD 2,500 per day; l = USD 3,500 per delayed day; T_c = 895 days; baseline total cost USD 13,982,500 = USD 11,745,000 direct + USD 2,237,500 indirect (my check: 2,500 x 895 = 2,237,500). CVaR confidence 0.90; lambda_T = lambda_C = 0.50; 150 replications per fitness evaluation, 1,000 for final reporting, convergence check with 150/500/1,000/5,000; hybrid GA-GWO cut deterministic duration from 895 to 699 working days; differences from GA and MPGWO-DLL not significant after Bonferroni correction.
- Limitations stated: parameters (h, l, T_c) are case-specific "not universal"; one 30-activity project; broader validation needed.
- Design decision supported: an explicit, simple delay-to-money conversion inside the simulation: per-iteration cost = direct + h*T + l*max(0, T - T_c), then report E[C], P90 and CVaR90. Confirms that the LD term is a hinge (non-linear) function of simulated duration.

### C03 - Ding, F., Liu, M., Hsiang, S.M., Hu, P., Zhang, Y. and Jiang, K. (2024). Duration and Labor Resource Optimization for Construction Projects - A Conditional-Value-at-Risk-Based Analysis. Buildings, 14(2), 553.
- DOI: 10.3390/buildings14020553 (CROSSREF; licence CC BY 4.0 per Crossref; OpenAlex also gold OA). Access: FULL (PDF from mdpi-res).
- Context: Takt-time planning of a high-rise residential floor, Arena simulation, 1,672 productivity samples, 90 labour combinations, VaR/CVaR at 75% and 90%.
- Key equations (transcribed): (2) integral from -inf to psi of f(x) dx = alpha (VaR at confidence alpha; interpreted as the latest finish time at confidence alpha); (3) CVaR_alpha(x) = 1/(1 - alpha) * integral from alpha to 1 of VaR_t(x) dt (expected value of the tail beyond alpha); (4) x% = (x - x_min)/(x_max - x_min) x 100% (normalisation of duration to a percentile scale).
- Key numbers: 4,500 simulated permutations (50 simulations x 90 combinations); floor duration VaR(0.9) = 69.69 h, expected duration beyond that limit (CVaR) = 74.56 h; tying beam bars VaR(0.9) = 42.54 h, CVaR(0.9) = 45.27 h; VaR(0.75) = 40.01 h, CVaR(0.75) = 45.39 h. Takt-time planning cut duration by 20.2% and labour cost by 2.1%.
- The paper states that a VaR of 20 days at alpha = 90% means the probability of not finishing in 20 days is limited to 10% - i.e., VaR_alpha(T) <= D is the same statement as P(T > D) <= 1 - alpha (this is the deadline-probability constraint in quantile form).
- Limitations stated: VaR and CVaR applied only to schedule; cost and quality left for future work; one building type; VaR is non-convex, not sub-additive and blind to the size of loss beyond alpha (their words, citing others); found that CVaR does not necessarily rise with alpha and that changes in VaR and CVaR are uncorrelated.
- Design decision supported: report both P(T > D) (or the quantile) and the tail mean; do not treat the two as interchangeable.

### C04 - Vegas-Fernandez, F. (2022). Project Risk Costs: Estimation Overruns Caused When Using Only Expected Value for Contingency Calculations. Journal of Management in Engineering, 38(5), 04022037.
- DOI: 10.1061/(ASCE)ME.1943-5479.0001064 (CROSSREF: title, single author, September 2022, volume 38 issue 5 article 04022037). Access: ABSTRACT only; ASCE page returned 403; OpenAlex/Semantic Scholar list it as closed. No licence.
- Abstract content (reconstructed by OpenAlex from its abstract index; I did not see the full text): expected-value method = overall expected risk cost as the sum of probability x impact products over risk events; compared against Monte Carlo simulation on thousands of random analytical models and on 271 real projects; effect of number of events, correlation and statistical distribution examined; common risk models do not meet the premises needed for stand-alone use of the EV method; EV can underestimate risk cost by up to three times; proposes an enlargement factor applied to the deterministic expected risk cost, with a multivariate-regression formula for the factor.
- Key equations: sum_i (P_i x C_i) is the object criticised (the abstract does not print an equation). Regression formula for the enlargement factor: NR (not seen).
- Which "premises" of EV are violated and the definition of "underestimation" (relative to which percentile?): NR - not in the abstract.
- Limitations: NR beyond abstract. Design decision supported: do not present sum(P_i C_i) as a contingency; present simulated distribution percentiles alongside it. The full text is needed before quoting the enlargement factor.

### C05 - Paquin, J.-P., Morin, P.-P., Lambert, A. and Koplyay, T. (2022). Assessing Project Contingency Reserves with the Expected Cost Overrun Risk Measure. Journal of Construction Engineering and Management, 148(10).
- DOI: 10.1061/(asce)co.1943-7862.0002361 (CROSSREF: authors, journal, 2022, volume 148, issue 10). Access: ABSTRACT only (OpenAlex-reconstructed); closed.
- Abstract content: proposes the expected cost overrun (ECO) as a coherent risk measure for contingency reserves; states that the project cost-percentile metric is not a coherent risk measure; ECO is the tail expectation of the cost distribution, i.e., the average of costs exceeding the baseline cost at a given significance level; closed-form solution under (among others) the normal distribution; reserve interpretable as an insurance contract; extends to a project time-overrun penalty measure (ETO) and a contingent-risk version (ETOP).
- Equations and numbers: NR (not in abstract).
- Design decision supported: theoretical argument (for a tail-expectation contingency rather than a bare percentile) and a direct link between time overrun and penalty. Same family as CVaR (see C09). Full text needed before use.

### C06 - Shoar, Sh. and Nazari, A. (2019). An optimization framework for risk response actions selection using hybrid ACO and FTOPSIS. Scientia Iranica (Transactions E: Industrial Engineering), 26(3), 1763-1777.
- DOI: 10.24200/sci.2018.20225 (IN-PDF, decoded from the PDF text layer; OpenAlex: diamond OA, licence field none). Access: FULL. Licence: not stated in the text I read - open access status per OpenAlex/journal only.
- Context: real 12-storey plus 7 underground commercial building; project cost USD 5.6 million; allocated budget for risk response USD 225,000; 34 risks identified, top 10 analysed with a design structure matrix (0-4 scale) and fuzzy membership functions; ant colony optimisation (ACO) chooses response sets; fuzzy TOPSIS then ranks the ACO solutions on further criteria.
- Key equations (transcribed, symbols simplified): (17)-(19) expected time / cost / quality loss after response, e.g. ECL_AR = sum_i sum_j sum_k w_i^cost x_ij (P_k^AR I_k^AR,cost D_jk), where x_ij = 1 if response j is applied to risk i, P_k^AR and I_k^AR = probability and impact of risk k after response, D_jk = influence of risk j on risk k from the DSM; (20) OF = W_t (ETL - ETL_AR)/ETL + W_c (ECL - ECL_AR)/ECL + W_q (EQL - EQL_AR)/EQL with W_t, W_c, W_q from AHP (the extracted text prints "min OF" but the text later says the fitness is maximised - direction ambiguous in my extraction); (21) sum_j C_j <= B; (22) Fitness = OF - Violation, Violation = alpha max(R.C/B - 1, 0), alpha > 1000 (penalty for exceeding budget).
- Evidence on MCDA vs optimisation: the paper states that optimisation models generally minimise implementation cost, that only some criteria can be quantified in the optimiser, and that criteria such as executive support and stakeholder satisfaction "cannot be quantified using ACO", so a TOPSIS step is recommended after optimisation; the case study reports that this second step may change the chosen solution. Also lists five families of response-generation approaches (zonal, trade-off, WBS-based, optimisation, case-based) and describes Ben-David and Raz (2001) as an optimisation model over work content, risk events, reduction actions and effects (secondary description, see C07).
- Limitations stated by the authors: optimal set varies with uncertainty level (needs sensitivity analysis); DSM interaction quantification is uncertain; secondary risks not modelled; sensitivity to interactions untested.
- Design decision supported: use constrained cost minimisation as the core and apply MCDA (or a manual review) only to non-monetary criteria; a budget cap can be implemented as a penalty term.

### C07 - Ben-David, I. and Raz, T. (2001). An integrated approach for risk response development in project planning. Journal of the Operational Research Society, 52(1), 14-25.
- DOI: 10.1057/palgrave.jors.2601029 (Springer page; consistent across two fetches and a search result). Access: ABSTRACT only; the Springer page is paywalled and showed no equations or variables. NOT read in full.
- What is known from what I saw: abstract says the model integrates project work content, risk events, and risk-reduction actions and their effects, represents overlapping effects of several reduction actions and secondary risk events, supports evaluation of total risk exposure under combinations of actions, and can be optimised to give the most cost-effective combination; illustrated with a software-industry example.
- Secondary descriptions (both read in full text): C01 groups it with approaches that minimise total risk cost; C06 describes it as an integrated model of work contents, risk events, reduction actions and effects solved by optimisation to give cost-effective combinations. Neither reproduces its equations. Objective function, constraints, variables: NR.
- Design decision supported: precedent for modelling overlapping response effects and secondary risks in the response-selection model (a feature the current TEC_m definition lacks). Original text needed before claiming details.

### C08 - Zhang, L., Li, Y., Sun, N. and Ning, Y. (2025). Understanding project cost contingency estimation: a holistic risk perspective. International Journal of Managing Projects in Business, 18(1), 139-164.
- DOI: 10.1108/ijmpb-07-2024-0162 (CROSSREF: authors Zhang, Li, Sun, Ning; IJMPB vol. 18, issue 1, pp. 139-164; issued 9 January 2025; the Crossref abstract matches the manuscript's). Access: FULL text of the UCL accepted manuscript (green route; no licence statement seen on the PDF; the published version is under Emerald site policies per Crossref, i.e., not an open licence).
- Content seen: systematic literature review (859 abstracts screened from Web of Science, ScienceDirect and Scopus, 2002-2024; 216 duplicates removed; 45 non-articles removed; 67 full articles analysed); six-element framework (event, consequence, uncertainty, probability, knowledge, mitigation) and twelve risk dimensions. Classifies contingency estimation into risk-source, individual-risk-event and overall-risk (outcome) approaches; lists expected value, AHP, probability trees, fuzzy methods and Monte Carlo among individual-risk methods; notes that studies disagree on including secondary and residual risks and fundamental uncertainties. It lists Vegas-Fernandez (2022) as the study of expected value plus Monte Carlo, and Paquin et al. (2022) as a coherent-risk-measure study (C04, C05).
- Equations: none used. Numbers above are the review counts.
- Limitations: review of contingency estimation, not a test of a decision rule; the accepted manuscript has no journal pagination.
- Design decision supported: contingency literature is split between per-event (EV/MC) and outcome-based (percentile of overrun) approaches; states explicit need to treat residual/secondary risk.

### C09 - Rockafellar, R.T. and Uryasev, S. (2000). Optimization of conditional value-at-risk. The Journal of Risk, 2(3), 21-41.
- DOI: 10.21314/jor.2000.038 (CROSSREF: authors, journal, volume 2, issue 3, pages 21-41, 2000). Access: FULL text of the author-hosted preprint dated 5 September 1999 (sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf); the journal version may differ. Not a construction paper. Licence NC.
- Key equations (transcribed; f(x, y) = loss for decision x and random vector y with density p(y); beta = probability level):
  - (1) Psi(x, alpha) = integral over f(x,y) <= alpha of p(y) dy  (loss CDF).
  - (2) alpha_beta(x) = min{alpha : Psi(x, alpha) >= beta}  (beta-VaR).
  - (3) phi_beta(x) = (1 - beta)^(-1) integral over f(x,y) >= alpha_beta(x) of f(x,y) p(y) dy  (beta-CVaR = conditional expectation of the loss at or above VaR).
  - (4) F_beta(x, alpha) = alpha + (1 - beta)^(-1) integral of [f(x,y) - alpha]^+ p(y) dy, with [t]^+ = max(t, 0); Theorem 1: phi_beta(x) = min over alpha of F_beta(x, alpha), F convex in alpha.
  - (9) sampled version: F~_beta(x, alpha) = alpha + (1/(q(1 - beta))) sum_k [f(x, y_k) - alpha]^+.
- Statements: VaR lacks sub-additivity and convexity; CVaR (mean excess loss, tail VaR) is a coherent risk measure (attributed to Pflug 2000); common levels 0.90, 0.95, 0.99; minimising CVaR reduces to linear programming when scenarios are used.
- Design decision supported: exact definitions and the sampled estimator to implement CVaR on the simulated cost distribution (e.g., mean of the worst (1 - beta) share of simulated total costs).

### C10 - Aires, R.F.F. and Ferreira, L. (2018). The rank reversal problem in multi-criteria decision making: a literature review. Pesquisa Operacional, 38(2), 331-362.
- DOI: 10.1590/0101-7438.2018.038.02.0331 (CROSSREF: volume 38, issue 2, pages 331-362, August 2018; Crossref lists no licence, the CC BY 4.0 statement is from the SciELO page). Access: PAGE (SciELO page as summarised by the fetch tool; PDF not read); licence CC BY 4.0 shown on the page.
- Content (as extracted from the page): systematic review of 130 articles (1980-2015) on rank reversal, i.e., a change in the ordering of alternatives after adding or removing alternatives; share of articles by method: AHP 76.2%, PROMETHEE 3.1%, TOPSIS 2.3%, ELECTRE 2.3%, hybrids/others 16.2%; five types of rank reversal; causes named for AHP (synthesis, normalisation, criteria weighting, misapplication, decision-maker uncertainty) and TOPSIS (vector normalisation, ideal-solution calculation); remedies (AHP ideal mode, multiplicative AHP, M-TOPSIS, modified normalisation, REMBRANDT). Authors say the debate is unresolved and that TOPSIS, ELECTRE and PROMETHEE are less studied than AHP.
- Not construction-specific. Design decision supported: if MCDA (AHP/TOPSIS) is used for response ranking, the ranking can change when an alternative is added or dropped; a cost-based rule with a probability constraint does not have this property (INFERENCE; the review does not test cost minimisation).

### C11 - Anil, N.E., Kassim, R. and Varghese, S.P. (2021). Analysis of Compensation for Delay and Settlement of Disputes Clauses in CPWD Contract Guidelines. AIJR Proceedings (International Web Conference in Civil Engineering for a Sustainable Planet, ICCESP 2021), pp. 69-75.
- DOI: 10.21467/proceedings.112.9 (IN-PDF and PAGE). Access: FULL; licence CC BY-NC 4.0 stated on the AIJR book page (PDF itself states copyright held by authors).
- Indian evidence on delay compensation. Context: questionnaire on clauses 2, 5 and 25 of CPWD GCC 2020; 55 professionals contacted, 22 responded.
- Key statements: the paper describes CPWD Clause 2 compensation as liquidated compensation, not a penalty, at a maximum rate of "1% per month of delay, computed on a per-day basis", with a ceiling of 10% of the accepted tendered value. DISCREPANCY: search-engine snippets about CPWD GCC (2019/2020/2023 versions) said 1.5% per month with the same 10% cap; I could not fetch the official GCC to resolve this. Use both figures as unverified until the current GCC text is checked (rate NC).
- Survey numbers: 72.7% of respondents use the clause in all contracts; methods used to compute compensation: fixed percentage with upper limit 44.4%, fixed amount with upper limit 38.9%, pre-defined formula 16.7%; 70% concerned that contracts do not specify a delay/disruption cost analysis method; 84.8% favour a specific clause on concurrent delay.
- Limitations: very small sample (22), perception survey, no cost data per day.
- Design decision supported: an Indian public-sector LD model is percent-of-contract-value per day with a cap, so the LD term in the simulation should be parameterised as rate x tendered value with a cap, not only a fixed rupee amount (INFERENCE from the clause description).

### C12 - Alshboul, O., Alzubaidi, M.A., Al Mamlook, R.E., Almasabha, G., Almuflih, A.S. and Shehadeh, A. (2022). Forecasting Liquidated Damages via Machine Learning-Based Modified Regression Models for Highway Construction Projects. Sustainability, 14(10), 5835.
- DOI: 10.3390/su14105835 (IN-PDF). Access: FULL; CC BY 4.0 printed in the PDF.
- Context: US highway projects; LD data for 2,486 road projects from state DOTs (collected 2012-2018); multiple linear regression and ML-modified regressions.
- Statements read: LDs are pre-estimated contractual amounts, typically levied as a percentage per day after the completion date, to compensate management, engineering and inspection costs beyond the contract completion date; Total Bid Amount had the largest influence on LD amount; LD correlated negatively with change-order variables and total adjustment days. The paper says it found no practical tool to predict LD in the literature.
- Equations: general MLR form Y = b0 + b1 X1 + ... + e (eq. 1); a fitted 4-variable equation appears in the PDF (coefficients not reproduced here).
- Limitations: US highway context; predicts the LD amount, not the delay cost to the contractor; relevance to Indian masonry is low.
- Design decision supported: LD is a contract-defined daily charge (owner's viewpoint), distinct from the contractor's own daily delay cost; the two should be separate parameters.

### C13 - Bara Iniesta, M. (2025). Enhanced Monte Carlo simulation for project risk analysis: integrating cost and schedule impacts with time-shifted risks and dependency modeling. Applied Operations and Analytics, 1(1), 1-15.
- DOI: 10.1080/29966892.2025.2552675 (CROSSREF: not run; OPENALEX: title, author, year, journal, volume/issue/pages). Access: ABSTRACT only (OpenAlex-reconstructed); publisher full text returned 403. OpenAlex reports diamond OA and licence CC-BY-NC (not verified on the publisher page).
- Abstract content: Monte Carlo with time-bound risk events and probabilistic dependencies; cascading impacts via time-shifted risks and dynamic probability adjustment; synthetic project; classical MC understates contingency relative to the enhanced method because of temporal cascade effects; produces time-phased contingency forecasts including daily P90 delay curves; bootstrap analysis used for statistical precision. A GitHub implementation exists (repository name seen in a search result; not opened).
- Equations, numbers, contingency size values: NR. Limitation visible: synthetic project only.
- Design decision supported: time-phased P90 delay curve idea; shows that adding dependencies raises contingency (direction only).

### C14 - Aljorany, H.O. and Mahjoob, A.M.R. (2024). Establishing a Budget for Optimal Response Strategies for Risks Categorized into Distinct Groups by using a Mathematical Model and Genetic Algorithm. Engineering, Technology & Applied Science Research, 14(3), 14747-14753.
- DOI: 10.48084/etasr.7526 (PAGE). Access: PAGE only; licence CC BY 4.0 printed on the page. PDF not read.
- Content: binary programming plus genetic algorithm for response strategy selection for primary and secondary risk events in different risk categories; tested on a geothermal construction project; budget limits and binary strategy variables. Equations, budget numbers, results: NR.
- Design decision supported: secondary-risk handling in binary response selection is a published extension (details NC).

### C15 - Mokhtari, G. and Aghagoli, F. (2020). Project Portfolio Risk Response Selection Using Bayesian Belief Networks. Interdisciplinary Journal of Management Studies, 13(2), 197-219.
- DOI: 10.22059/ijms.2020.272892.673461 (PAGE). Access: ABSTRACT only; licence not stated on the page.
- Content: Bayesian network with three node types (portfolio risks, impact effects, response actions) to model interactions among risks, impacts and responses; optimisation minimises combined residual-risk effect and implementation cost; solved by genetic algorithm. Numbers: NR. Portfolio level, not single activity.

### C16 - Tripathi, O.P., Hasan, A., Jha, K.N. and Jain, A.K. (2022). Evaluating Government Contracts for Delays, Delay Damages, and Levy of Compensation Provisions. Journal of Legal Affairs and Dispute Resolution in Engineering and Construction, 15(1).
- DOI: 10.1061/(ASCE)LA.1943-4170.0000584 (OPENALEX; article number NC). Access: ABSTRACT only.
- Indian evidence. Abstract (OpenAlex-reconstructed): examines delay provisions, damage assessment and compensation clauses of three Indian government organisations (CPWD, DMRC, NHAI) using organisational manuals plus interviews with senior professionals; finds existing compensation methods flawed and potentially biased; proposes a mathematical framework for fair delay compensation that considers the total delay period.
- OPEN-ACCESS CONFLICT: OpenAlex lists a Figshare copy (submitted version) as CC-BY, but the Figshare API record for the same item shows "All Rights Reserved" and the file under embargo (about 585 KB). Treated as NOT open access. The framework, rates, equations and numbers: NR.
- Priority for follow-up: this is the most Indian-specific peer-reviewed source for delay compensation found; obtain via institutional access.

### C17 - Namazian, A., Yakhchali, S.H., Yousefi, V. and Tamosaitiene, J. (2019). Combining Monte Carlo Simulation and Bayesian Networks Methods for Assessing Completion Time of Projects under Risk. International Journal of Environmental Research and Public Health, 16(24), 5024.
- DOI: 10.3390/ijerph16245024 (PAGE, PMC). Access: PAGE (summary of the PMC article); CC BY 4.0 per the page.
- Relevant as a negative finding for topic 7: the model expresses risk impact only as days of delay (expected project delay 19.93 days by simulation vs 19.68 theoretical in a gas refinery case with 1,000 iterations) and is not converted to money. Equations (Bayes' theorem; activity duration adjustment d_r = d_r0 (1 + max_k R_rk); expected delay as weighted sum over high/medium/low risk states) are as printed in the summary. Limitations stated: 5-point scale impacts, project-level only, expert-elicited priors. Design decision: the days-to-money step is not supplied by this paper; take it from C02, C11, C19.

### C18 - AlJassmi, H., Abduljalil, Y. and Philip, B. (2023). Towards self-recovering construction schedules: a new method for periodically updating project plans and optimizing recovery actions. Journal of Asian Architecture and Building Engineering, 22(4), 2335-2347.
- DOI: 10.1080/13467581.2022.2153055 (IN-PDF). Access: LOCAL (held as a Group 5 paper); CC BY 4.0 printed in the PDF. Not modified.
- Brickwork evidence: tested on brickwork activities in a residential complex in the UAE, using 1,487 working days of retrospective data for 132 masons; the neural-network productivity forecast reported as 98% accurate; recovery options: activity crashing (extra masons/overtime), fast tracking, "do nothing"; activity crashing found to be the lowest-cost option.
- Delay-cost definition (citing Lock 2017 in the paper): the "do nothing" option is chosen when the recovery cost exceeds the delay cost, and the delay cost is described as including delay penalty, salary and resource costs, loss caused by late start of the next activity, and administration cost. No numeric daily rate found (NR).
- Design decision supported: an accept/mitigate comparison inside the schedule (recovery cost vs delay cost) already exists for brickwork; useful as the "accept" arm of TEC.

### C19 - Van Basten, Firstyanandara, F.D. and Crevits, I. (2026). Transformation of Risk Mapping in Shopping Mall Construction Through Value Engineering and Risk Assessment (VERA) Approach. International Journal of Technology, 17(3), 1196-1215.
- DOI: 10.14716/ijtech.v17i3.8104 (as printed in the local PDF text; not resolved). Access: LOCAL (Group 5 paper); licence NC.
- Delay-cost example (Indonesia): the contractor's LD is stated as 1 per mille of the contract value per day; for a piling package of about USD 6.1 million (10% of total construction value) a 110-day delay gives a penalty of about USD 671 thousand (my check: 0.001 x 6.1 million x 110 = 671,000, consistent with the package value as the base). Switching to the alternative piling method (HSPD) was estimated to complete in 135 days instead of 240; equipment rental/operation cost about USD 636 thousand vs USD 509 thousand (25% higher, difference about USD 127 thousand). The paper's risk ranking is by FMEA RPN (RPN 210 for low labour performance), not by expected cost.
- Design decision supported: worked example of "avoid/mitigate cost (USD 127 thousand) vs LD exposure (USD 671 thousand)" - a deterministic TEC comparison; shows LD base can be a package value.
- Limitation: deterministic, single scenario; no probabilities.

### C20 - Starczyk-Kolbyk, A. and Jedras, I. (2025). Integrated Risk Assessment in Construction Contracts: Comparative Evaluation of Risk Matrix and Monte Carlo Simulation on a High-Rise Office Building Project. Applied Sciences, 15(17), 9371.
- DOI: 10.3390/app15179371 (as listed in the project's own README; not resolved by me). Access: LOCAL (Group 2 paper #13); CC BY per README.
- EMV vs simulation (topic 2): risk-matrix exposure for 10 threats and 2 opportunities = product of impact on cost and probability (medium probability), total exposure PLN -552,000 (a net saving, driven by a PLN -1,350,000 value-engineering opportunity). Monte Carlo (triangular impact, uniform probability range): reported mode PLN -524,444.84; minimum PLN -2,285,715.52; maximum PLN 4,119,905.54; 59.587% certainty that the total additional cost is <= 0.
- Caveat (mine): the authors compare the risk-matrix sum with the simulation MODE, not the mean, so this is not a like-for-like EV vs E[C] comparison; the wide simulated range (about -2.29 to +4.12 million PLN) shows the spread that the single EV figure hides.
- Design decision supported: show the EV number and the simulated distribution side by side.

### C21 - Zavala, G., Ariza Flores, V., Santos, R. and Blas Cano, J. (2025). Stochastic Cost Estimation in Transportation Infrastructure Projects Using Monte Carlo Simulation and Correlated Risk Variables. Future Transportation, 5(4), 176.
- DOI: 10.3390/futuretransp5040176 (IN-PDF). Access: LOCAL (Group 2 paper #20); CC BY 4.0 printed in the PDF.
- Contingency percentiles (topic 3, 6): correlated model total cost: mean USD 84.01 M, P50 83.98 M, P90 85.00 M, P95 86.26 M, s.d. 0.73 vs 0.61 for the independence model; independence P95 = 84.63 M vs correlated 86.26 M. Exceedance probabilities: budget 84.00 M -> 45.4%; 84.50 M -> 28.7%; P90 (85.00 M) -> 16.8%; P95 -> about 3.0% (from a fitted skew-normal reproducing the reported quantiles). Recommends calibrating a P90-P95 percentile to funding decisions in their Peruvian road context.
- Equation (their proxy): Expected overrun proxy = Pr(Cost > Threshold) x max(P95_with_rho - Threshold, 0); values 1.03 / 0.51 / 0.21 / 0 MUSD for the four thresholds. The authors state this proxy does not integrate the full tail (as CVaR / expected shortfall does) and therefore understates tail risk.
- Limitations stated: correlations from limited evidence and expert judgment; linear correlation misses tail dependence; marginals approximate.
- Design decision supported: ties percentile choice to residual exceedance probability and flags the tail-mean gap; supports reporting P(exceed budget) at each contingency level.

### C22 - Chatterjee, K., Zavadskas, E.K., Tamosaitiene, J., Adhikary, K. and Kar, S. (2018). A Hybrid MCDM Technique for Risk Management in Construction Projects. Symmetry, 10(2), 46.
- DOI: 10.3390/sym10020046 (IN-PDF). Access: FULL (mdpi-res PDF); the PDF prints a Creative Commons Attribution statement (version number not read). Published 13 February 2018 per the PDF.
- Context: MCDM selection of a risk-response strategy: D-number extension of ANP (criteria weights), consistent fuzzy preference relation for ratings, and D-MABAC for ranking; illustrative construction case with 10 experts (5 technical, 5 management), 9 risk criteria in 3 dimensions (external: political, economic, social; process: technological, work quality, time and cost; internal: resource, documents/information, stakeholder), 5 alternative responses (A1 proper scheduling for updated project information; A2 adjust plans for scope; A3 information on local partner credibility; A4 transfer risks to other parties; A5 merger/diversification of projects).
- Key numbers: D-MABAC, D-TOPSIS, D-COPRAS and D-ARAS all give the same ranking A1 > A3 > A4 > A2 > A5 (Spearman coefficient 1.000 between methods). Sensitivity: eight criteria-weight scenarios changed the ranks of some alternatives: A1 stayed best in five of eight scenarios (second in two, third in one); A5 stayed worst in six of eight. The authors state the weights come from expert perception and that the ranking is sensitive to them.
- No monetary or probabilistic evaluation of responses: cost and time enter only as one risk criterion (C6, "time and cost risk"). Equations (D-ANP, D-MABAC) are long and not transcribed here (NC).
- Limitations: 10-expert single illustrative example; rank stability across four MCDM methods does not test agreement with a cost-based rule (NR).
- Design decision supported: shows what an MCDM response ranking looks like for construction risk (no cost-of-delay, no residual-risk quantification) and that ranks depend on criteria weights; supports keeping MCDA to qualitative criteria.

### C23 - Zhang, B., Bai, L. and Kang, S. (2022). Risk Response Strategies Selection over the Life Cycle of Project Portfolio. Buildings, 12(12), 2191.
- DOI: 10.3390/buildings12122191 (IN-PDF). Access: FULL; CC BY 4.0 printed in the PDF. Published 11 December 2022.
- Context: project-portfolio (construction) risks; dynamic Bayesian network for causality and time dependency; 0-1 integer programme (CPLEX) selecting response strategies per life-cycle stage.
- Key equations (transcribed): expected loss EL defined as the product of likelihood and impact (their words: product of likelihood and impact, i.e., EMV at the risk level); (8) Max z = sum_i sum_k Prp_i^k x_i^k + sum_i sum_k sum_{m=k+1}^{K} Trp_i^m x_i^k + sum_i sum_k Cop_i^k x_i^k (direct effect on the risk, indirect effect on later stages, indirect effect on other risks in the same stage, of strategy A_i chosen in stage k); (9) sum_i C_i x_i^k <= B_k for each stage k (budget); (10) sum_i L_i^k - sum_i S_i^k x_i^k - sum_{m<k} sum_i Trp_i^m x_i^m <= phi_k (residual expected loss in stage k must not exceed the acceptable bound phi_k); (11) each strategy at most once; (12) mutually exclusive pairs; (13) prerequisite pairs; (14) binary. Variable definitions as printed: C_i cost of strategy A_i; B_k stage budget; L_i^k expected loss before response; S_i^k response effect; phi_k upper bound on acceptable expected loss in stage k.
- Key numbers: 19 candidate strategies; stage budget B_k = 25 (million yuan) for k = 1..4; acceptable expected loss phi = 5000, 5000, 5000, 1000 for stages 1-4 (units as printed in the paper's example, currency unit for phi not confirmed); finding: response effect is larger when risks are responded to in earlier stages; the authors state that accounting for risk correlations makes response more effective in reducing expected losses than assuming independence.
- Limitations stated: input data from expert judgment because of missing historical data; expert weighting scheme overlaps (age vs experience).
- Design decision supported: precedent for a "residual expected loss <= acceptable bound" constraint (eq. 10) alongside a budget cap - a threshold on expected residual loss, not on the probability of missing a deadline. Portfolio/stage-based, not single-activity.

### C24 - Choi, S.-W. and Lee, E.-B. (2024). A Delay Liquidated Damages (DLD) Mitigation Model based on Earned Schedule (ES) and Earned Value Management System (EVMS) Concepts. Proceedings of the 41st ISARC (International Symposium on Automation and Robotics in Construction), Lille, France, pp. 374-380.
- DOI: 10.22260/ISARC2024/0049 (PAGE, iaarc.org). Access: FULL (PDF from iaarc.org; the page lists a different PDF path that returned 404, the working path was http://www.iaarc.org/publications/fulltext/048_ISARC_2024_Paper_152.pdf). Licence: page shows only "(c) IAARC"; no open licence seen; conference paper, peer-review status NC.
- Context: EPC plant projects (Korean contractor, Hanoi project); earned schedule to forecast delay and compare acceleration cost with delay liquidated damages (DLD).
- Key equation (transcribed): (1) DLD = Contract Amount x Delay Schedule x DLD Rate, with DLD not to exceed Contract Amount x Cap (delay measured in schedule days; rate per day as a fraction of contract amount).
- Decision rule stated in the text: if DLD per day is less than the average daily shortening (acceleration) cost, paying DLD is supported; if DLD per day exceeds the acceleration cost, acceleration is supported. Equation (8): cost for 1-day reduction divided by the number of concurrent critical-path activities (priority for catch-up).
- Key numbers: KPMG statistic quoted in the paper: only 25% of EPC projects met deadlines and 31% met budgets over the past 36 months (as quoted, source not checked); single critical path case: 72 days delayed, late compensation set at USD 50,000 per day (total USD 3,600,000); shortening 12 days cost USD 149,863; result USD 3,149,863 total vs USD 3,600,000, saving USD 450,137 (my check: 60 x 50,000 + 149,863 = 3,149,863). Multiple critical paths: 10 days shortened at USD 2,853,602 and "USD 746,398 saved compared to the full DLD" - my check: 3,600,000 - 2,853,602 = 746,398, which omits any residual DLD for the unshortened days, so the second result is not reproducible from the text as written (derivation NC).
- Limitations: single company/project; deterministic (no probability distribution of delay); DLD rate treated as a given input.
- Design decision supported: (i) LD formula = contract (or package) value x daily rate x delay days with a cap - same structure as the CPWD clause described in C11; (ii) a per-day break-even rule (avoided delay cost per day vs mitigation cost per day) as a sanity check on the TEC ranking; (iii) shows deterministic what the current design does probabilistically.

### C25 - Ahmadi, M., Behzadian, K., Ardeshir, A. and Kapelan, Z. (2017). Comprehensive risk management using fuzzy FMEA and MCDA techniques in highway construction projects. Journal of Civil Engineering and Management, 23(2), 300-310.
- DOI: 10.3846/13923730.2015.1068847 (IN-PDF). Access: FULL (journal PDF); CC BY 4.0 stated on the journal page (Vilnius Tech OJS). Received 28 Aug 2014, accepted 13 May 2015 (per PDF); OpenAlex lists the year as 2016 (online-first), the print year is 2017.
- Context: Bijar-Zanjan highway project in Iran; 30 risk events ranked by risk critical number (RCN) using fuzzy FMEA and fuzzy AHP over cost, time and quality; response chosen with an expert system and the scope expected deviation (SED) index (a TOPSIS-derived deviation from target time, quality and cost).
- Equation: (5) SED combines weighted relative deviations of expected time T, quality Q and cost C from targets T0, Q0, C0 with weights W_t, W_q, W_c (the extracted equation text is garbled, so the exact form is not transcribed here; NC).
- Key numbers (Table 5, risk event "increase in tar price"; targets 240 days, EUR 1,025.9 thousand): business-as-usual 340 days, EUR 1,117 thousand, quality 0.96, SED 17.2%; response 1 (mitigation, save budget for tar price inflation) 300 days, EUR 1,055.6 thousand, SED 8.63%; response 2 (avoidance, RCC pavement instead of asphalt) 300 days, EUR 856.2 thousand, SED 1.05%. The paper says RCC takes about 15% longer to construct but costs about 25% less than asphalt (citing a typical design).
- Observation (mine): response 2 also has the lowest cost and equal-lowest time among the three states, so a plain cost or time comparison would give the same choice; this case does not demonstrate a need for MCDA. There is no delay-cost or LD term; time enters only as a normalised deviation. The paper also describes Fan et al. (2008) as selecting responses on minimum cost only.
- Limitations stated: useful if only one party is the risk owner; secondary risks and simultaneous multiple responses not modelled; complexity of expert systems and data collection burden; practitioners prefer own judgment.
- Design decision supported: MCDA is used here to combine three non-commensurable criteria; where all criteria can be monetised (delay cost, mitigation cost) this reduces to a cost comparison.

### C26 - Buertey, J.I.T., Abeere-Inga, E. and Kumi, T.A. (2012). Estimating Cost Contingency for Construction Projects: The Challenge of Systemic and Project Specific Risk. Journal of Construction Project Management and Innovation, 2(1), 166-189.
- DOI: 10.36615/jcpmi.v2i1.20 (PAGE; the DOI redirects to the journal article page). Access: FULL (PDF); licence CC BY-NC 4.0 shown on the journal page. Small regional journal; weak evidence grade.
- Context: Ghana; 204 questionnaires to built-environment professionals, 118 returned (57.8%); FMEA as a qualitative tool and univariate statistics as a quantitative tool.
- Key numbers: systemic risk accounts for about 64% of the cost drivers of cost uncertainty (paper text: 0.637) and project-specific risk for 36%; scope changes, incomplete scope definition, design status and changes in specification rated as high-impact systemic risks; natural/force majeure and economic indicators regarded as beyond the project team's prediction.
- Statement relevant to topic 2 (secondary citation; original not read): the paper says Hollmann (2007) postulates that empirically based parametric models suit systemic risk, while an expected monetary value can be deduced from Monte Carlo simulation for project-specific risk.
- Limitations: perception survey (57.8% response); no contingency equation or percentile results; no delay-cost content.
- Design decision supported: only that contingency literature separates systemic (scope/design-status-driven) uncertainty from event-type risk and that a Monte Carlo derived EMV is proposed for the latter.

### C27 - Hong, W., Eum, T. and Song, C.G. (2023). Design Optimization Methodology for Diversion Structure with Concrete Cofferdam Using Risk-Based Least-Cost Design Method. Applied Sciences, 13(5), 2903.
- DOI: 10.3390/app13052903 (IN-PDF). Access: FULL; CC BY licence statement printed in the PDF. Not a masonry paper (hydropower diversion structure, Gulpur project, Pakistan) - included as a worked example of expected-cost optimisation that contains an explicit delay-LD term.
- Key equation (transcribed, words as printed): EMV = Construction cost of diversion structure + Failure probability of upstream cofferdam x [ (Reconstruction cost of upstream and downstream cofferdams) + Delay LD ] + Overflow probability of upstream cofferdam x Recovery cost. The design option with the lowest EMV is chosen. Failure probability from a limit-state Monte Carlo (500,000 samples per stability analysis); overflow probability = inverse of the return period.
- Key numbers: delay for reconstruction set at 2 months; Delay LD set at 1.5% of total EPC cost; recovery cost cases USD 0.5, 1.0, 2.0, 3.0, 4.0 million; optimal design flood frequency 1 year for recovery cost USD 0.5 million, 1-2 years for USD 1.0-2.0 million (for 3, 4 and 5 year usage periods) and 2-10 years for USD 3.0-4.0 million; the authors note the optimum is driven by recovery cost and period of use because the overflow probability is much larger than the failure probability, so delay LD and reconstruction cost, although large, did not change the optimum.
- Limitations: EMV is a mean; no variance, percentile or deadline constraint; LD set as a lump percentage for a fixed 2-month delay; single project.
- Design decision supported: precedent for the structure TEC = deterministic cost + sum of (probability x consequence including LD) used to rank alternatives; also a caution that a dominant high-probability term can make the LD term irrelevant to the ranking (sensitivity analysis on LD is worthwhile).

### G01 (grey literature, not peer-reviewed) - Zack, J.G. Jr. and Badala, P.V. Pricing Contractor Delay Costs: A Research Perspective. Navigant Construction Forum (white paper). Year: NR (the PDF template shows "MONTH YEAR").
- Access: FULL text of the PDF via the CMAA site; grey literature; not peer reviewed; US and Canada/UK contract practice.
- Content on delay-cost components (topic 1): delay damages are those costs that increase solely because of a delaying event; direct = idled and extended labour and equipment, storage, bond, material inflation; indirect = loss of efficiency, extended or unabsorbed home-office overhead, extended field-office overhead. Field-office overhead items listed include site trailers, utilities, project management and supervision staff, vehicles, safety equipment. Time-related vs non-time-related costs must be separated (mobilisation is one-time). The paper says there are at least eight methods to compute extended field-office overhead and that they do not give the same daily cost. The simplest (actual-cost, project-average) method: divide time-related field-office overhead by project duration and multiply by the days of compensable delay. Named formulae for home office overhead: Eichleay (US), Emden/Hudson (UK, Canada). Note: field overhead is roughly bell-shaped over time, so an average daily rate can over- or under-compensate depending on when the delay occurs.
- No financing-cost formula found in this source (NR). Numbers for Indian conditions: NR.
- Design decision supported: separate parameters for (a) time-related site overhead per day, (b) idle labour/equipment per day, (c) home-office overhead, (d) contractual LD, (e) financing; treat mobilisation as fixed.

## 4. Evidence by topic (1-7), with what each paper supports

1. Delay cost per day: components - G01 (direct vs indirect list; field overhead average-rate method), C18 (delay cost list incl. penalty, salary/resources, next-activity loss, administration), C02 (indirect cost h per day + LD l per day, numeric example), C12 (LD as daily charge), C11 (CPWD LD as percent of tendered value per month, computed per day, capped at 10%), C19 (1 per mille per day of contract value), C24 (DLD = contract amount x delay days x DLD rate, capped; USD 50,000 per day in the example), C27 (delay LD = 1.5% of total EPC cost for a 2-month delay, inside an expected-cost objective). Indian examples: C11 (survey; rate discrepancy 1% vs 1.5%), C16 (CPWD, DMRC, NHAI; abstract only). Financing-cost per day from a peer-reviewed source: NR.
2. EMV definition and limits: C04 (sum of P x impact products; simulation on 271 projects and random models; EV may underestimate up to three times; enlargement factor), C20 (risk-matrix EV vs simulation range), C01 (E_j = mean of P x impact per risk; additivity of expectations and variances only for uncorrelated risks), C08 (review context), C23 (expected loss defined as likelihood x impact, used with a budget cap and a residual-expected-loss ceiling), C27 (EMV = construction cost + P(failure) x [reconstruction + delay LD] + P(overflow) x recovery cost; lowest EMV wins; no variance or percentile). Risk neutrality of EMV is discussed via C01 (net saving vs criteria that consider variance or regret); a peer-reviewed paper that formally derives EMV risk neutrality: NR.
3. Contingency by percentile / MC: C21 (P50/P90/P95 with exceedance probabilities), C05 (percentile not a coherent measure; expected overrun instead), C13 (time-phased P90), C08 (review), C26 (systemic vs project-specific split, about 64% / 36% in a Ghana survey; secondary mention of EMV from Monte Carlo for project-specific risk). P80 evidence specifically: NR from a paper I read (only search-engine summaries mention P80 practice).
4. Risk-response selection: C01 (ILP; several objectives; budget), C06 (ACO + budget penalty), C07 (Ben-David and Raz; abstract only), C14, C15 (abstract-level), C18 (recovery vs delay cost), C19 (avoid vs LD example), C23 (budget cap plus residual-loss ceiling, portfolio stages), C24 (per-day break-even between DLD and acceleration cost), C25 (mitigation vs avoidance compared on time/cost/quality deviation), C27 (least expected total cost including LD). Decision trees and expected utility in construction: NR from read papers (only search snippets from PMI library, unverified); Safaeian 2022 already held.
5. MCDA: C06 (FTOPSIS applied after cost/time/quality optimisation for non-quantifiable criteria), C01 (multiple criteria combined by counting), C10 (rank reversal in AHP, TOPSIS etc.), C22 (D-ANP/MABAC ranking of five response strategies; ranks identical across four MCDM methods but changed under eight weight scenarios; no monetary terms), C25 (fuzzy AHP + TOPSIS-derived SED index; chosen response also had lowest cost and equal-lowest time). Evidence that MCDA outperforms cost minimisation: NR.
6. Deadline and tail criteria: C03 (VaR as finish time at confidence, CVaR beyond), C02 (CVaR-adjusted duration and cost), C09 (formal definitions and estimator), C05 (ECO), C01 (P(L > a) objective), C21 (exceedance proxy and its limits). Chance-constrained project scheduling papers: search results seen (JORS 2018 uncertain chance-constrained model; IEEE 2004 chance constrained project scheduling under risk) but NOT read; treat as leads.
7. Delay-to-money in simulation: C02 (explicit equations, per-iteration cost with h*T + l*max(0, T - T_c)), C27 (probability x [reconstruction + delay LD] inside an expected-cost formula, with LD as a percentage of contract cost), C24 (deterministic: DLD = contract amount x days x rate, capped), C03 (schedule-only), C17 (days only, no money), C13 (time-phased P90 delay), C05 (time overrun penalty measures).

## 5. Which decision criterion is best supported, and what the evidence does NOT support

Labelling: [E] = directly evidenced in a paper I read (IDs given); [I] = my inference; [NR] = no evidence found.

A. Best-supported core criterion (cost-based, constrained):
- Total expected cost with a budget cap, TEC_m = C_mit + E[C_residual], is the objective used or described in [E] C01 eq. (9) (net expected saving = expected reduction minus response cost, subject to a budget), C06 (optimisation models "generally minimise cost of implementing actions", budget as constraint eq. 21), and, per two secondary descriptions, Ben-David and Raz (C07, via C01 and C06). Residual risk is represented as a mitigation rate applied to simulated impact [E] C01 eq. (6) or as after-response probability/impact [E] C06 eq. (17)-(19).
- The paper-level evidence for using simulated E[C] rather than the sum of P_i C_i: [E] C04 abstract (EV can underestimate risk cost by up to three times relative to Monte Carlo); [E] C20 (EV and simulation compared; large simulated spread). Whether E[C] from simulation differs from sum P_i C_i in the presence of independent risks with linear impacts: [I] by linearity of expectation the two coincide when each risk's cost is P x impact and there are no interactions; differences arise from correlation/dependence, conditional probabilities, non-linear cost functions (the LD term), and from comparing against high percentiles rather than means. This is textbook reasoning, not shown in the papers I read; the exact premises in C04 are NR.
- Further [E] support for a total-expected-cost ranking that contains an LD term: C27 (lowest EMV over design alternatives, with delay LD inside the bracketed consequence) and C24 (deterministic per-day rule: accept the LD if DLD per day is below the acceleration cost per day, otherwise accelerate). C23 uses a related but different form: maximise response effect subject to a budget cap and a ceiling on residual expected loss (eq. 9-10).
- [I] Because LD = l max(0, T - T_c) is convex in T, E[LD] is not equal to l max(0, E[T] - T_c) (Jensen); deterministic EV on mean duration understates expected LD. The functional form is [E] C02 eq. (14); the Jensen point is my inference.

B. Deadline-probability constraint:
- [E] C03 states VaR at confidence alpha is the latest finish time at that confidence (probability of not finishing by that time is limited to 1 - alpha); [E] C01 (4.4, eq. 12) uses P(L > a) as a selectable objective (normal approximation, uncorrelated risks). So "P(T > D) <= alpha" is a recognised criterion, equivalent to quantile_T(1 - alpha) <= D [I, direct rearrangement of C03's statement]. It is NOT shown in any read paper as a hard constraint jointly with TEC minimisation for a construction activity [NR]; C01 treats it as an alternative objective and then combines criteria by counting. The choice of alpha (5%, 10%, 20%) is not evidenced [NR].

C. Tail metrics:
- CVaR/expected shortfall is supported as a more informative tail measure than VaR/percentile [E] C09, C03, C02, C05 (ECO), C21 (says its exceedance proxy understates tail risk). Supported as an optional reporting metric and as a risk-adjusted objective term [E] C02 eq. (28)-(29). Not evidenced as required for a single-activity masonry model [NR].

D. Risk neutrality vs risk aversion:
- Risk aversion is handled in the read papers by variance minimisation, exceedance probability, regret/minimax [E] C01, or by a risk-aversion weight lambda on CVaR [E] C02. Utility functions/expected utility in construction: Safaeian 2022 (already held) and Zhang and Zuo 2016 (named in C01, not read). The evidence I read does not show that risk-neutral EMV gives worse decisions than a utility criterion for this scale of decision [NR].

E. When MCDA is needed:
- [E] C06 supports MCDA only for criteria that cannot be monetised or entered in the optimiser (stakeholder satisfaction, executive support); [E] C01 combines six criteria by counting because they select different risk sets. [E] C10 documents rank-reversal instability for AHP/TOPSIS-type methods (not construction-specific). [E] C22: response ranking changed under alternative criteria-weight scenarios (weights from expert perception) although four MCDM methods agreed with each other; [E] C25: in the highway case the MCDA-preferred response was also the cheapest and equal-fastest, i.e., dominated the others on the monetisable criteria. [NR] No paper I read shows MCDA is required when all impacts are monetisable or that it beats constrained cost minimisation. [I] For a single masonry activity whose impacts are cost and delay, MCDA is not needed for the core decision; keep it optional for non-monetary items (safety, quality, reputation), and expect ranking sensitivity to the added/removed alternatives (C10).

F. Not supported / gaps:
- No paper read gives a validated daily delay-cost number for Indian masonry; the closest are C11 (CPWD LD structure, rate discrepancy), C16 (abstract only), C19/C02 (non-Indian case parameters, "not universal" per C02).
- No peer-reviewed formula seen for the financing component of daily delay cost (G01 lists none).
- P80 as a preferred contingency level is not evidenced in read papers; C21 recommends P90-P95 for its Peruvian road case only.
- Full text of C04 (the EV premises, the enlargement-factor regression) and C07 (model equations) not obtained; anything about them beyond the abstracts is unknown.
- C24's second result (multiple critical paths) cannot be reproduced from the text (saving = 3,600,000 - 2,853,602 with no residual DLD), so it should not be quoted as a validated benefit.
- Overlapping response effects and secondary risks: mentioned in C06, C07, C14, C25 as extensions; none was implemented in my read papers for a single-activity case except as noted; the current TEC_m formulation omits them.

## 6. Design decisions supported (summary for the implementation)
1. Compute per-iteration total cost = base + sum of realised risk costs + h*T_delay-related + l*max(0, T - T_c), then report E[C], P50/P80/P90, P(T > D), and CVaR (C02, C09).
2. Keep sum(P_i C_i) (EMV) as a sanity check and as a risk-matrix ranking aid; label it as a mean, not a contingency (C04, C20).
3. Evaluate each response m by TEC_m = C_mit + mean of simulated residual cost, with residual modelled by a mitigation-rate or after-response probability/impact (C01 eq. 6, C06 eq. 17-19); apply a budget cap (C01 eq. 9, C06 eq. 21).
4. Apply the deadline constraint P(T_m > D) <= alpha on the same simulated draws (C03 quantile form; C01 objective 4.4 as a precedent).
5. Report alternatives that change under different criteria (C01 Table 5 shows R6 and R3 enter or leave depending on the criterion).
6. Keep LD, contractor overhead, idle resources and financing as separate parameters (G01, C12, C11, C19); parameterise LD as rate x contract (or package) value x days with an optional cap (C24 eq. 1, C11, C19), and run a sensitivity check on the LD rate because in C27 a high-probability term dominated the ranking.
7. Add a per-day break-even check next to the TEC ranking: mitigation cost per day of delay avoided versus delay cost per day (C24 rule; C19 numbers).

## 7. Unverified statements and leads NOT read (do not cite as evidence)

Seen only in search-engine summaries or OpenAlex titles; not fetched or not readable:
- Baccarini, D. and Love, P. (2014), Statistical characteristics of cost contingency in water infrastructure projects, JCEM 140(3): a search summary reported 228 Australian water projects, mean contingency added 8.46% vs 13.58% required. DOI seen only inside a search URL (10.1061/(ASCE)CO.1943-7862.0000820, unresolved). Full text NC.
- Statement that the EV total "will be overrun about 50% of the time" attributed to Vegas-Fernandez appeared only in a search summary; not in the OpenAlex abstract I read. Not used.
- Delay costs "20-30%" of project cost and LD "Rs 20,000 per day capped at 40 days" appeared in legal-blog search snippets; not peer-reviewed, not verified.
- PMI Learning Library articles on decision-tree analysis for the risk-averse organisation and expected utility for contingency allocation: seen as titles in search results only.
- OpenAlex/DOAJ titles (open-access flagged, NOT read; DOIs as listed by those indexes, not resolved): 10.28991/cej-030950 Risk Response Selection in Construction Projects (Civil Engineering Journal, 2018; the journal page timed out); 10.2298/fuace201117020m Triangular distribution and PERT method vs payoff matrix for decision-making support in risk analysis of construction bidding (Facta Universitatis 2020; host refused connection); 10.2495/risk140211 Estimating post- and pre-mitigation contingency in construction (WIT 2014); 10.1016/j.procs.2017.11.080 mathematical model to select risk response strategies, Saba Tower (2017); 10.1051/matecconf/201927002001 Risk based decision making in highway slope geometry design (MATEC 2019, keyword EMV per DOAJ listing).
- Already promoted from this list to full entries after reading: Chatterjee et al. 2018 (C22), Zhang, Bai and Kang 2022 (C23), Choi and Lee 2024 (C24), Ahmadi et al. 2017 (C25), Buertey et al. 2012 (C26), Hong et al. 2023 (C27).
- Fang, C., Marle, F., Xie, M. and Zio, E. (2013), An integrated framework for risk response planning under resource constraints in large engineering projects, IEEE Trans. Eng. Manage. 60(3), 627-639, DOI 10.1109/tem.2013.2242078: existence confirmed via search results and OpenAlex (green OA, HAL hal-00926363); the HAL page returned an access-denied challenge; not read.
- Velasquez, M. and Hester, P.T. (2013), An analysis of multi-criteria decision making methods, Int. J. Oper. Res. 10(2), 56-66: the PDF host had an expired certificate; not read.
- Chance-constrained project scheduling papers (JORS 2018 uncertain chance-constrained programming model, DOI 10.1057/s41274-016-0122-2 as seen in a search URL; IEEE 2004 conference paper): not read.
- CPWD GCC official text for Clause 2 rate: not fetched (fetch failed).

## 8. Suggested next actions when the tools are available again
- Resolve the CPWD Clause 2 rate (1% vs 1.5% per month) from the current official GCC.
- Obtain full texts (institutional access) of C04, C05, C07, C16; read Fang et al. (2013) from HAL and Baccarini and Love (2014).
- Re-run the OpenAlex queries that failed (chance-constrained scheduling, delay cost with financing/overhead, contingency P80, expected utility) after the rate limit clears, plus one on "delay damages" in India; look for a peer-reviewed treatment of the financing cost of delay.
- Check any of the section 7 OpenAlex titles for the P80 and decision-tree/utility evidence.
