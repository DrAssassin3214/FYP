# Topic Group A - Masonry and India evidence (literature search notes)

Project: AI-assisted, literature-grounded Monte Carlo + risk-matrix + EMV decision support for BRICK MASONRY in INDIAN building construction.
Search date: 26 Sep 2026. Searcher: research sub-agent (WebSearch / WebFetch / built-in browser pane).

## 0. How to read this file (integrity rules applied)

- A number appears in this file ONLY if it was visible in text I actually retrieved (full-text PDF/HTML, or a publisher/RG abstract page). Every such number carries a source location.
- Otherwise the field says **NR** (not reported) or **NC** (not checked).
- "Evidence depth" labels:
  - **FULL TEXT** = I obtained the paper's own text (PDF text extracted, or full HTML) and read the cited parts.
  - **FULL TEXT (fetch-summarised)** = the fetch tool returned a machine summary of the full page; the numbers were quoted back by that summariser and I did not re-read the raw page. Treat as "probably right, re-check against the PDF before citing".
  - **ABSTRACT ONLY** = I saw only the abstract (publisher page, ResearchGate abstract block, KoreaScience page, NepJOL page).
  - **SNIPPET ONLY** = I only saw a search-engine result summary. These are LEADS, not evidence. Nothing in the SNIPPET tier should be typed into the model.
- "OA verified" = I saw a licence statement in the article PDF/page itself (or on the publisher page). If the licence came only from ResearchGate or OpenAlex metadata, it is marked as such.
- Transferability tags: **India-specific**, **comparable** (Nepal/Bangladesh/Pakistan/Sri Lanka), **international**.

## 1. PRISMA-style summary (honest, approximate)

There was no database export, so the tallies below are counts of distinct records I noted while reading result lists, not a formal PRISMA count.

| Stage | Count (approx.) |
|---|---|
| Web-search queries run (WebSearch) | 30 |
| Structured-index queries (OpenAlex API, Crossref API) | about 12 (some rate-limited, 429) |
| Distinct candidate records noticed in result lists (titles/snippets) | about 90 |
| Records opened (page/PDF/abstract actually retrieved) | 31 |
| Excluded on screening (off-topic, commercial blog, news, lab-type task, infrastructure-only with no transferable numbers, duplicates of already-collected papers) | about 60 |
| INCLUDED in this file | 22 (A01-A22) |
| of which FULL TEXT read | 6 (A01, A02, A05 partly via summariser, A07, A15/A16 via summariser, A21) - see per-item labels |
| of which ABSTRACT ONLY | 11 |
| of which SNIPPET ONLY | 2 |

Search strings used (verbatim or near-verbatim):
1. brick masonry labour productivity India construction sites mason output per day study
2. causes of delay in building construction projects India relative importance index questionnaire survey
3. material shortage brick supply delay risk Indian construction projects lead time
4. labour absenteeism migrant labour festival Indian construction productivity study
5. "masonry" productivity "India" labour output "man-hours" brickwork case study journal open access
6. monsoon rain delay masonry construction India productivity loss percent rainy days
7. rework brick masonry quality defects India construction cost time overrun study
8. Nepal building construction delay causes RII brick masonry
9. Loganathan Kalidindi masonry labor construction productivity variation Indian case study (+ crew/wall terms)
10. Engineering Journal Karthik Rao labour productivity brick masonry wall India time motion
11. Bangladesh building construction delay causes brick masonry labour productivity study
12. Sri Lanka construction labour productivity brick laying masonry factors study
13. weather delay construction India monsoon days lost building projects survey RII rainfall
14. Doloi Sawhney Iyer Rentala analysing factors affecting delays in Indian construction projects
15. Indian construction labour shortage festival return native village absenteeism percentage
16. Kerala construction delay causes labour shortage material building projects RII study
17. brick price volatility shortage brick kiln ban construction India supply chain risk
18. Shrishirmal Salgude time and motion study brickwork plastering residential
19. productivity brick masonry CPWD actual skilled unskilled labour coefficient India
20. Assessment of Construction Labour Productivity in India brick masonry (skilled vs CPWD)
21. Ponmalar Aravindraj Nandhini factors influencing labour productivity residential Indian scenario (x2)
22. Guha Biswas monsoon risks construction sites India Kolkata Monte Carlo
23. rework in Indian construction projects causes and cost percentage residential
24. Analysis of Labor Productivity in Bricklaying Operation ... Surkhet Nepal
25. Johari Jha work motivation construction labour productivity India
26. brickwork productivity Monte Carlo simulation probability distribution mason output (returned only generic MC pages - nothing usable)
27. rainfall impact construction labour productivity India rain days work stoppage
28. material management building construction India survey cement bricks steel shortage
29. Indian construction workers working days per month rainy season festival holidays
30. "masonry" "delay" India building activity-level delay brickwork plastering risk assessment
31. AAC block vs brick masonry productivity India (only commercial blogs returned)
32. Ha Duy Khanh Soo Yong Kim workers' experience productivity brick masonry
Plus OpenAlex filter queries (masonry/brickwork/bricklaying + productivity; India + delay) and Crossref title look-ups used to verify DOIs.

## 2. Access / process log (things the caller should know)

- ResearchGate pages were readable in the built-in browser pane for abstracts (title, abstract, licence tag, author list). After several page loads ResearchGate raised a Cloudflare "security check" page; I stopped using ResearchGate at that point and did NOT attempt to pass the check.
- One attempt to open a ResearchGate PDF link in the browser pane triggered a file-download / save dialog for the user. I did not retry and did not save anything. (Apologies for that; it is logged here so you can dismiss the dialog if it is still open.)
- WebFetch cannot read publishers that return 403 (ASCE, T&F, ScienceDirect, MDPI, granthaalayah, academia.edu, core.ac.uk). Where WebFetch fetched a PDF, the harness cached the binary under its own tool-results folder (not a deliberate download by me); I extracted text from those cached copies with pypdf into my scratch folder (`...\scratchpad\A_masonry\`). No files were saved anywhere in your project except this notes file.
- Semantic Scholar API and some OpenAlex/Crossref calls returned HTTP 429 at times.
- A "session limit" message appeared once during WebFetch late in the search; the search was wrapped up shortly after.

## 3. Summary table (one line per paper)

| ID | Authors (year) | Country / tag | Topic slots (1-7) | Depth | OA verified |
|---|---|---|---|---|---|
| A01 | Reddy & Chambrelin (2021) | India / India-specific | 1, 6-ish (time waste) | FULL TEXT | Yes, CC BY 3.0 (IOP page) |
| A02 | Ponmalar, Aravindraj, Nandhini (2018) | India (Chennai) / India-specific | 1, 3, 4, 5 | FULL TEXT | Licence not in PDF; CC BY 4.0 shown on ResearchGate page only |
| A03 | Loganathan & Kalidindi (2015) | India (Tamil Nadu) / India-specific | 1, 4 | ABSTRACT ONLY | No (full text not accessible) |
| A04 | Lawaju, Parajuli, Shrestha (2021) | Nepal / comparable | 1 | ABSTRACT ONLY | No (copyright reserved by journal) |
| A05 | Rana, Sharma, Neupane, Shrestha (2023) | Nepal / comparable | 1, 4 | ABSTRACT ONLY | NC |
| A06 | Karthik & Rao (2016), labour parameters | India / India-specific | 1, 7 | ABSTRACT ONLY | NC |
| A07 | Gerek, Erdis, Mistikoglu, Usmen (2015) | Turkey / international | 1, 7 | FULL TEXT | OpenAlex lists CC-BY; licence not seen in the PDF text I read |
| A08 | Loganathan & Kalidindi (2016) | India (6 states) / India-specific | 4 | ABSTRACT ONLY | No |
| A09 | Guha & Biswas (2008) | India (Kolkata) / India-specific | 5 (+ Monte Carlo) | ABSTRACT ONLY | No (pre-2010) |
| A10 | Pinky Devi & Sindhu (2025) | India (infrastructure) / India-specific but not buildings | 2, 3, 5 | FULL TEXT (fetch-summarised) | Yes, CC BY 4.0 (Springer page) |
| A11 | Soundarya et al. (2025) | India (Chennai residential) / India-specific | 2, 4, 5, 6 | FULL TEXT (fetch-summarised) | Yes, CC BY-NC-ND 4.0 (fetch) |
| A12 | Mehta & Gaikwad (2017) | India (residential) / India-specific | 2, 4 | ABSTRACT ONLY | NC |
| A13 | Noushad, Saud, Neduvancheri (2023) | India (Kerala high-rise) / India-specific | 2 | ABSTRACT ONLY | No (paywalled preview) |
| A14 | Abeysinghe & Jayathilaka (2022) | Sri Lanka / comparable | 2, 3, 4, 5 | FULL TEXT (PMC, quoted twice) | Yes, CC BY (PMC) |
| A15 | Manoharan et al. (2022) | Sri Lanka / comparable | 4 | FULL TEXT (fetch-summarised) | Yes, CC BY 4.0 (Emerald page) |
| A16 | Kar & Jha (2020) | India / India-specific | 3 | SNIPPET ONLY (metadata verified via Crossref) | No |
| A17 | Reddy & Rao (2022) | India / India-specific | 2, 3 | SNIPPET ONLY (metadata verified via Crossref) | No |
| A18 | Singh, Rohila, Khursheed, Paul (2022) | India (SPA Delhi) / India-specific | 6 | ABSTRACT ONLY | NC |
| A19 | Tankkar & Wanjari (2015) | India / India-specific | 2, 4 | ABSTRACT ONLY | NC |
| A20 | Kaja & Jauswal (2023) | India (residential) / India-specific | 1 | ABSTRACT ONLY | NC |
| A21 | Ouansrimeang & Wisaeang (2024) | Thailand / international | 2, 4 (festival labour) | FULL TEXT | Yes, CC BY (PDF text) |
| A22 | Abbasian-Hosseini et al. (2014) and Ha & Kim (2021) - see section 5 (leads only, not read) | international | 1 | SNIPPET ONLY / NOT READ | NC |

(A22 is a placeholder for two unread international masonry leads; do not count it as a verified paper.)

## 4. Per-paper cards

### A01 - Reddy & Chambrelin (2021) - India, brickwork time-and-motion (BEST INDIA-SPECIFIC FULL TEXT FOUND)
- Authors: G. Vinod Kumar Reddy, K. Shyam Chambrelin (Koneru Lakshmaiah Education Foundation, Guntur, AP).
- Title: Application of Time and Motion study for Brickwork activity in Residential building.
- Venue: IOP Conf. Ser.: Materials Science and Engineering 1197 (2021) 012038 (ICACE 2021). DOI 10.1088/1757-899X/1197/1/012038 (printed on the PDF).
- Access: OPEN ACCESS, licence verified in text: "Content from this work may be used under the terms of the Creative Commons Attribution 3.0 licence" (PDF p.2; also IOPscience page).
- Country/sample: seven residential building sites, Vijayawada / Guntur / Visakhapatnam (Sec. 4.1); site work Feb-Mar 2021; video-recorded time study; crew = masons + helpers "aged 25-35 years with 10-16 years of work experience", traditional tools (abstract).
- Key numbers (Tables 1-9):
  - Crew sizes observed: 2 (sites 1, 4, 5, 6, 7), 3 (site 3: 2 masons + 1 helper), 4 (site 2: 2 masons + 2 helpers) (Tables 1-7).
  - Unit: AAC at sites 1, 2, 4, 5; red bricks at sites 3, 6, 7 (Tables 1-7). (So the paper mixes brick and AAC.)
  - Observation windows: 0:58:52 to 1:55:09 (hh:mm:ss) per site (Table 8) - i.e. each site is ONE short (about 1-2 h) observation.
  - Work efficiency (Table 9): Site1 72.90 %, Site2 89.14 %, Site3 90.62 %, Site4 62.57 %, Site5 72.08 %, Site6 77.63 %, Site7 79.82 %. Text: "efficiencies are varying in the range of 60-90%" (Sec. 4.2).
  - Unproductive time per crew observation (Table 8): 0:06:19 to 0:25:45; helpers frequently idle 15-44 min of a ~1-2 h window (Tables 1-7).
  - Causes named for low efficiency: "Lack of work targets to complete the tasks; Poor work planning; Improper monitoring of workers; Lack of precise and accurate control over labor tasks" (Sec. 4.2). Conclusion adds "Poor site management, Target less work environment, Material shortage, Miscommunications, Issues related to electricity, Equipment breakdown" (Sec. 5).
- **WARNING on their productivity column**: Table 9 gives "Productivity (m2/hr)" 35.59, 33.08, 32.32, 26.48, 31.40, 53.94, 17.26 and the text says "15-60 m2/hr". Those are area/(observation minus unproductive time) for wall areas of 18.8-56.6 m2 within ~1-2 h by 2-4 people. That is physically implausible for hand brick/AAC laying and about two orders of magnitude above other reported daily outputs (e.g. Mahamid 2020, already collected: 26.2 m2/day for a whole day). The area measurement basis is not explained. **Do NOT use the m2/hr column in the Monte Carlo.** The efficiency percentage and idle-time shares are the only defensible outputs.
- Transferability: India-specific (Andhra Pradesh; mixed AAC/brick).
- Model use: effective-working-time factor / idle-time share for the labour-productivity block (62-91 % efficiency range as a triangular/beta prior, with the caveat of tiny sample); qualitative causes for the risk register.
- Limitations: n = 7 single short observations; productivity column unreliable; no SD; no daily output; mixture of AAC and brick.

### A02 - Ponmalar, Aravindraj, Nandhini (2018) - India (Chennai) brick masonry work-hours and RII (FULL TEXT)
- Title: Study on factors influencing labour productivity in residential buildings in Indian scenario.
- Venue: International Journal of Engineering Technologies and Management Research (IJETMR) 5(2): 239-248, Feb 2018. DOI 10.29121/ijetmr.v5.i2.2018.168 (verified via doi redirect and ResearchGate page); the PDF header also prints Zenodo DOI 10.5281/zenodo.1198950.
- Access: full PDF read (via a Semantic Scholar-hosted copy). Licence NOT printed in the PDF text I extracted; ResearchGate's page for the item shows "License CC BY 4.0" - so OA is claimed by RG metadata only (unverified on the journal page; granthaalayah returned 403).
- Country/sample: two 3-storey residential buildings (12 flats each), Kundrathur area, Chennai; questionnaire to supervisors, project engineers and labourers; 35 factors, RII with weights 1-4; number of respondents NR.
- Key numbers:
  - Manpower RII (Table 1): lack of experience 0.787 (rank 1); **absenteeism 0.751 (rank 2)**; age 0.730; misunderstanding among labourers 0.680; accidents 0.650; personal problems 0.610.
  - Resource RII (Table 2): lack of required construction material 0.780 (rank 1); lack of tools/equipment 0.760; poor site condition 0.751; material storage location 0.700; increase in price of material 0.550 (rank 9). Text: "shortage of river sand" cited as severe.
  - Miscellaneous (Fig. 1, values printed as 775.8 / 700 / 665.5 / 650 on a ~1000 scale): payment delays 775.8; **weather condition 700 (rank 3)**; shortage of water 650 (rank 5).
  - Brick masonry site record (Sec. 4.4, 5, Table 3): both projects' masonry activity duration 20 days; total work-hours **144 (Project A) and 158 (Project B)**; total lost work-hours 11.76 and 9.7; "work-hour over run" 8.17 % and 6.14 %; ineffective days "8 of 20 = 40 %" (A) and "7 of 20 = 35 %" (B). (Internal inconsistency: Sec. 4.4 says Project A "required 160 work-hours" but Table 3 and Sec. 5 say 144.)
- Transferability: India-specific (Tamil Nadu, small residential).
- Model use: (i) absenteeism, material shortage and weather as ranked risk items with RII-based likelihood/severity seeds; (ii) 35-40 % of days "ineffective" and 6-8 % hours lost as an order-of-magnitude for productivity-loss frequency (definitions are the authors' own and loosely defined); (iii) very rough hours-per-activity anchor (144-158 work-hours per 20-day masonry activity for a 557-850 m2 built-up-area building; wall quantity NR).
- Limitations: no wall quantities, no crew composition, respondent count NR, weak methodology description, internal number conflict (160 vs 144), predatory-tier journal risk. Use as low-weight evidence.

### A03 - Loganathan & Kalidindi (2015) - India (Tamil Nadu), masonry crew productivity variation (ABSTRACT ONLY)
- Title: Masonry labor construction productivity variation: an Indian case study. Indian Lean Construction Conference (ILCC), Mumbai, Feb 2015, vol. 1. DOI NR. (ResearchGate page read in browser pane.)
- Access: full text not accessible (RG "Download" needs login). OA: no.
- From abstract (RG): pilot study at one construction project in Tamil Nadu; "Results of the analysis indicate that 20% to 40% production variation between different construction crews involved in masonry construction of the project"; migrant/seasonal workers a "significant portion of the total construction workforce"; labour cost "30 to 50% of the total cost of a project".
- A search-engine summary (SNIPPET ONLY, source page not identified, do not use) also claimed: 23 crews, 115 mm brickwork wall, two months of daily data, crews from 3 masons + 2 helpers to 17 masons + 11 helpers, average 39 masons/day. I could not confirm these in any text I read. **Treat as a lead to verify.**
- Model use: crew-to-crew productivity coefficient of variation prior (20-40 % variation between crews) - but "production variation" is not defined in the abstract (range vs SD?), so NC until full text is read.

### A04 - Lawaju, Parajuli, Shrestha (2021) - Nepal (Kathmandu Valley) brick masonry ANN (ABSTRACT ONLY)
- Journal of Advanced College of Engineering and Management 6, DOI 10.3126/jacem.v6i0.38356 (NepJOL page read). Licence text on page: "JACEM reserves the copyright for the published papers..." (i.e. not a Creative Commons licence).
- Abstract: 44 factors from literature, top 13 chosen; ANN (NeuroSolutions), 65 % training / 20 % cross-validation / 15 % testing; MSE 0.019. Production-rate values and sample size not in the abstract; full PDF (>10 MB) could not be fetched.
- Tag: comparable. Model use: which factors matter for masonry production rate (qualitative). Numbers: NR.

### A05 - Rana, Sharma, Neupane, Shrestha (2023) - Nepal (Surkhet) bricklaying (ABSTRACT ONLY)
- Advances in Engineering and Technology: An International Journal 3(1): 103-119, Dec 2023, DOI 10.3126/aet.v3i1.60628 (ResearchGate page).
- Abstract: questionnaire (Likert), Cronbach's alpha 0.976, RII + mean response analysis + ANN sensitivity; highest factor group "Material related factors", then leadership, manpower, other. Snippet from a search summary (unverified) said absenteeism of craftsmen among key factors.
- Tag: comparable. Numbers other than alpha: NR.

### A06 - Karthik Dasari & Rao (2016) - India, labour constants in Standard Schedules of Rates (ABSTRACT ONLY)
- Title: A Study on Construction Labour Productivity Parameters in India, April 2016 (ResearchGate). Journal NR on the page I saw.
- Abstract: compares labour output constants used for standard schedule rates (SSR) across Indian departments (central and state), referenced to IS 7272 Part I; examples are for RCC not masonry (page snippet). No masonry numbers seen.
- Model use: pointer to where SSR/CPWD-type "output norms" for brickwork can be sourced (IS 7272; CPWD DAR); NOT a productivity measurement. Mason output norms would come from CPWD/state SSR documents rather than this paper.

### A07 - Gerek, Erdis, Mistikoglu, Usmen (2015) - Turkey, masonry crew productivity (FULL TEXT)
- Title: Modelling masonry crew productivity using two artificial neural network techniques. Journal of Civil Engineering and Management 21(2): 231-238; DOI 10.3846/13923730.2013.802741 (printed on PDF). OpenAlex lists this as gold OA with a CC-BY licence; the PDF text I read had a VGTU copyright line and no CC statement, so OA licence is "per OpenAlex".
- Sample: 147 crews, data Sep 2006-Sep 2008 from randomly selected building sites (about 80 % southern Turkey) (Sec. 2). Crew = skilled + unskilled workers; productivity = m2/h of whole crew. Inputs include number of skilled/unskilled, age, experience, wage type, days worked per week, daily work hours, overtime, break time, accommodation, wall type (brick, iso-brick, briquette, AAC, light brick) and mortar type (pre-mixed / on-site) (Table 1).
- Results: FFNN mean testing MAPE 14.341 % (mean R 0.803); RBNN mean MAPE 14.955 % (mean R 0.860) (Tables 2-3). Lowest MAPE shown in Table 3 is 10.152 % (RB24); the text says best RBNN "92.64 %" (1-MAPE) - table and text disagree slightly.
- **No descriptive statistics (mean, SD, min, max) of crew productivity are reported in the pages I read.** So this does not supply a distribution.
- Tag: international. Model use: justification that crew size/experience/hours/wall-type/mortar-type are the input factors to vary in the model; confirms crew-level modelling is standard. Limitations: no numbers usable for India.

### A08 - Loganathan & Kalidindi (2016) - India, absenteeism and turnover of migrant workers (ABSTRACT ONLY)
- Absenteeism and Turnover of Migrant Construction Workers in Indian Projects - A Survey-Based Study. Construction Research Congress 2016 (ASCE), pp. 1793-1802. DOI 10.1061/9780784479827.179 (Crossref verified). Abstract read on ResearchGate.
- Abstract facts: interviews with project managers and labour sub-contractors on **15 projects in six states (Delhi, Gujarat, Karnataka, Maharashtra, Pondicherry, Tamil Nadu)**; "illness, injury, lack of basic facilities, and payment delays are the significant factors contributing to absenteeism and turnover"; construction "about 10% to nation's GDP and employs approximately 35 million people"; major share of workforce is migrant. Absenteeism percentages: NR in abstract.
- OA: No. Model use: labour-availability risk drivers (payment delay, illness/injury, amenities) for the risk register; probability values NC.

### A09 - Guha & Biswas (2008) - India (Kolkata), monsoon impact on building works with Monte Carlo (ABSTRACT ONLY; outside 2010-2026)
- Monsoon risks for construction sites in India. 2008 IEEE International Conference on Industrial Engineering and Engineering Management (IEEM). DOI 10.1109/IEEM.2008.4738167 (ResearchGate page).
- Abstract: housing project at various stages in monsoon; time and cost data from the contractor; extra time for monsoon-sensitive items such as foundations assessed against weather records; Monte Carlo simulations; "monsoon has increased the project duration by about 5% and the cost by 12%"; Kolkata.
- Figure caption seen on the page: activity durations "baseline, low and high" (three-point estimates) from site personnel (optimistic and pessimistic).
- Also (from a citing paper's snippet on the RG page): monsoon onset mid-June to mid-September; highest rainfall in August (328 mm) - second-hand, NC.
- This is the ONLY India-specific monsoon + Monte Carlo + building source found. It is pre-2010, so flag it as an exception you may wish to keep. Activity-level (masonry) monsoon factors: NR in what I saw; need the full text (ResearchGate PDF blocked/not opened).

### A10 - Pinky Devi & Sindhu (2025) - India, infrastructure delays (roads/bridges), OA (FULL TEXT, fetch-summarised)
- Delay Analysis of Infrastructure Construction Projects in India. Journal of The Institution of Engineers (India): Series A. DOI 10.1007/s40030-025-00899-5. Licence quoted on the Springer page: "licensed under a Creative Commons Attribution 4.0 International License" (OA verified).
- Sample: 72 construction management professionals.
- RII (as extracted): material-related issues 0.562 (rank 1); late material deliveries 0.652; material shortages 0.619; construction-site factors 0.555; contractor-related 0.506; weather conditions (external) 0.616.
- NOTE: infrastructure (roads/bridges), not buildings - use only as a corroborating India-wide signal for material-delay and weather-delay likelihood. RII is an importance index, NOT a probability.

### A11 - Soundarya et al. (2025) - India (Chennai) residential cost overrun and delay causes (FULL TEXT, fetch-summarised)
- An investigation study on residential buildings for cost overrun. Scientific Reports. DOI 10.1038/s41598-025-95984-x. Licence CC BY-NC-ND 4.0 (as stated on the page by the fetch tool).
- Sample: six sites in Chennai; clients, contractors and structural designers; Cronbach's alpha > 0.70; frequency index (FI), severity index (SI) and importance index (II) used - so this is one of few sources giving frequency and severity separately.
- Numbers (as extracted): overall lag in schedule FI 0.861, SI 0.819, II 0.71 (rank 1); **rework/extra work II 0.55 (rank 2)**; inadequate skilled labour II 0.53 (rank 3); inadequate design/specification II 0.52 (rank 4); climatic variation on project execution II 0.37 (rank 11); hike in materials cost II 0.29 (rank 12). Number of respondents: NR in what I saw.
- Model use: gives FI x SI style seeds for a risk matrix; but the individual FI/SI for rework, labour and weather were not retrieved (only II). Re-check the table in the PDF before using.

### A12 - Mehta & Gaikwad (2017) - India, residential delay causes (ABSTRACT ONLY)
- Delays and its Analysis: Indian Residential Construction Projects. Journal of Construction Engineering and Project Management 7(4): 20-28. DOI 10.6106/JCEPM.2017.7.4.020. (KoreaScience page read.)
- Abstract (verbatim key parts): questionnaire of 100 stakeholders; importance index, PCA, correlation analysis; "finance-related issues, as well as labour related problems as the dominating causes of delays". Values: NR in abstract. Full PDF (KoreaScience) could not be retrieved (session limit).
- Model use: residential context; labour issues as top-tier delay cause.

### A13 - Noushad, Saud, Neduvancheri (2023) - Kerala high-rise delay factors (ABSTRACT ONLY)
- Analysis of Causes and Effects of Critical Delay Factors in High Rise Building Projects of Kerala. Proceedings of SECON'23, Lecture Notes in Civil Engineering 381. DOI 10.1007/978-3-031-39663-2_8. Paywalled preview.
- Abstract: Delphi + 76 delay causes + RII across contractors, owners, designers, consultants, research scholars. No numbers in the preview.

### A14 - Abeysinghe & Jayathilaka (2022) - Sri Lanka, timely completion (FULL TEXT via PMC, quoted twice)
- Factors influencing the timely completion of construction projects in Sri Lanka. PLoS ONE. DOI 10.1371/journal.pone.0278318. PMC9754246; licence: Creative Commons Attribution (PMC page).
- Sample: "One hundred sixty-three responses were collected" from 1,416 distributed questionnaires (Data collection); 39 delay factors; respondents 28.8 % clients / 28.2 % contractors / 39.9 % consultants.
- Table 2 RII (verbatim rows from second, quote-only fetch): "Shortage of labourers (Skilled, semi-skilled, unskilled)" 0.8245, rank 2; "Delay of delivering materials to the site" 0.8098, rank 4; "Fluctuation of material prices in the market" 0.7890, rank 6; "Bad weather conditions" 0.6528, rank 30. Rank 1 (first extraction): shortage of skilled subcontractors/suppliers 0.8294.
- Tag: comparable (South Asian, building-inclusive). Model use: relative ordering supports the view that labour and material supply outrank weather; RII is importance not probability.

### A15 - Manoharan et al. (2022) - Sri Lanka labour-related productivity factors (FULL TEXT, fetch-summarised)
- Labour-related factors affecting construction productivity in Sri Lankan building projects: perspectives of engineers and managers. Frontiers in Engineering and Built Environment. DOI 10.1108/FEBE-03-2022-0009. OA: CC BY 4.0 (Emerald page).
- Sample: 90 upper-grade contractor firms (CIDA-registered). Of 32 factors, 21 critical (RII > 0.7). Top RII: skills shortage 0.82; lack of thinking abilities 0.81; lack of work experience 0.80; lack of knowledge in construction works 0.79; poor labour discipline 0.79. Also quoted: "labour costs contribute in a range of 30-50% of total project costs".
- Tag: comparable. Model use: skill-level effect on productivity risk.

### A16 - Kar & Jha (2020) - India, material management issues vs schedule/cost (SNIPPET ONLY; metadata verified)
- Examining the Effect of Material Management Issues on the Schedule and Cost Performance of Construction Projects Based on a Structural Equation Model: Survey of Indian Experiences. Journal of Construction Engineering and Management 146(9). DOI 10.1061/(ASCE)CO.1943-7862.0001906 (Crossref: authors Santu Kar, Kumar Neeraj Jha, 2020).
- Search-summary claims (UNVERIFIED): 33 material management issues, 15 expert interviews, 86 procurement professionals; "improper delivery of materials" most critical. ASCE page 403 to my tools; ARCOM abstract page had no abstract text. Do not cite numbers until read.
- Model use: relevant to brick/material delivery risk, but no brick-specific data seen.

### A17 - Vidyasagar Reddy & Hanumantha Rao (2022) - India, delay factors and material supply (SNIPPET ONLY; metadata verified)
- Analysing the critical delay factors and delay in material supply for construction projects in India. Materials Today: Proceedings 60: 1890-1897. DOI 10.1016/j.matpr.2021.12.529 (Crossref).
- Search-summary claim (unverified): 47 delay reasons identified, 25 most commonly reported grouped as client, contractor, consultant, labour and machinery, inventory. No values seen.

### A18 - Singh, Rohila, Khursheed, Paul (2022) - India, rework cost and prevention (ABSTRACT ONLY)
- Evaluation of rework cost and prevention cost of rework in building construction. International Journal of Sustainable Building Technology (as shown on the RG page; the RG DOI is 10.37628/ijsdt.v5i1.902) 5(1), March 2022; School of Planning and Architecture, Delhi.
- Abstract: defines rework, lists determinants (changes, omissions, errors, stakeholders); "intends to evaluate the rework cost and the cost of prevention of rework in civil works"; case-study rework cost comparison figure exists; no percentages in the abstract. Masonry-specific rework: NR.

### A19 - Tankkar & Wanjari (2015) - India delay factors (ABSTRACT ONLY)
- Identification of Critical Delay Factors in Execution of Construction Projects in India. Research Journal of Engineering and Technology 6(4): 389-398. DOI 10.5958/2321-581X.2015.00061.6.
- 85 respondents (33 clients, 10 consultants, 42 contractors); mean-score ranking of ten critical delay factors; top three: lack of human resources (skilled, semi-skilled, unskilled), poor site management, insufficient coordination and control. Abstract frames it around infrastructure projects. Values NR.

### A20 - Kaja & Jauswal (2023) - India, labour productivity impact on residential cost (ABSTRACT ONLY)
- Assessment of Construction Labour Productivity in India, Aug 2023 (School of Planning and Architecture, Vijayawada; ResearchGate). Journal NR on the page I saw.
- Abstract: questionnaire to architects/engineers/contractors, RII ranking, quantified impact on labour productivity applied to a residential project ("Labour Productivity Per Cum" figure exists). Numbers NR.
- A search-engine summary attributed "skilled labour 0.36 vs CPWD 0.47" for ground-floor brick masonry to this or a related paper. I could NOT find these numbers in any text I read (grep of the full texts I hold found no 0.36/0.47/CPWD). **Unverified; do not use.**

### A21 - Ouansrimeang & Wisaeang (2024) - Thailand, festival/harvest labour shortage (FULL TEXT)
- Analyzing the critical delay factors for construction projects in the public sector using relative importance index and machine learning techniques. Journal of Infrastructure, Policy and Development 8(8): 6208. DOI 10.24294/jipd.v8i8.6208. OA: PDF text says "licensed under the Creative Commons Attribution (CC BY) license".
- Sample: 30 public projects that were delayed; 28 factors.
- Numbers: contractor financial issues RII 0.777 (weighted 84.44 %); labour issues "such as a shortage of workers during the harvest season or festivals" RII **0.773 in the abstract but 0.733 in the results text (weighted 82.78 %)** - internal inconsistency.
- Tag: international (Thailand, public projects, not masonry). Only relevant as a documented example of seasonal/festival labour unavailability being ranked second; no Indian festival numbers found.

### A22 - Placeholder: international masonry leads NOT read (do not count)
- Abbasian-Hosseini et al. (2014), Verification of lean construction benefits through simulation modeling: A case study of bricklaying process, KSCE J. Civil Eng., DOI 10.1007/s12205-014-0305-9 - OpenAlex lists hybrid OA CC-BY-NC-ND. Not opened.
- Ha, Kim et al. (2021), The relationship between workers' experience and productivity: a case study of brick masonry construction, Int. J. Construction Management (23(4)), DOI 10.1080/15623599.2021.1899593 - T&F page 403; only search snippet seen (questionnaire + work sampling; Vietnam per the snippet). Not read.

## 5. What the literature I could read says, mapped to the model

| Model element | Best evidence found | Confidence |
|---|---|---|
| Effective working time of masonry crews (India) | A01: efficiency 62.57-90.62 % over 7 short observations; A02: 6-8 % of hours lost, 35-40 % "ineffective days" in 2 projects | Low (tiny samples, loose definitions) |
| Crew-to-crew productivity spread | A03 abstract: 20-40 % variation between crews (definition NC) | Low until full text read |
| Output rate (m2/day, bricks/day) | NOT obtained from any full text; A01's m2/hr column is implausible and must not be used | None |
| Crew composition | A01: 2 (1 mason + 1 helper), 3 (2M+1H), 4 (2M+2H) at sites observed | Low |
| Delay-cause ranking, India | A10 (RII material 0.562, weather 0.616), A11 (rework II 0.55, skilled labour II 0.53, climatic II 0.37, material-cost hike II 0.29), A12/A19 (labour, finance top) | Medium for rank order; RII is not a probability |
| Material supply | A02 (lack of material RII 0.780, rank 1 resource; price rise 0.55), A10 (late delivery 0.652, shortage 0.619), A14 (delay in delivering materials 0.8098), A16/A17 leads | Medium for ranking; brick-specific lead-time data: none |
| Labour availability / absenteeism | A02 (absenteeism RII 0.751, rank 2 manpower), A08 (causes: illness, injury, lack of facilities, payment delay; 15 projects, 6 states), A11 (inadequate skilled labour II 0.53), A14 (shortage of labourers 0.8245) | Medium for drivers; absenteeism rate: NR |
| Festival effects | A21 (Thailand only). Nothing peer-reviewed for India found | None for India |
| Monsoon | A09 (project +5 % duration, +12 % cost, Kolkata; Monte Carlo); A02 (weather RII 0.700); A10 (0.616); A11 (0.37); A14 (bad weather 0.6528, rank 30) | Medium-low; note weather is consistently ranked BELOW labour and material in building studies |
| Rework | A11 (rework II 0.55, rank 2, Chennai); A18 abstract only | Low; masonry-specific rate NR |

## 6. Topics where nothing usable was found

1. **Masonry output distributions (mean/SD/min/max) for India** - no accessible full text reported these. The only distribution-like statement is A03's abstract ("20% to 40% production variation").
2. **Output in m2/day, bricks/mason/day or man-hours per m3/m2 from a peer-reviewed Indian source** - not retrieved. The figures the web search surfaced (e.g. 6 m2/mason/day for 115 mm wall, 600 bricks/day, 1.25 and 1.00 m3/mason-day in foundation and superstructure, 12-15 vs 20-25 m2/day AAC vs brick) come from Scribd/blog/CPWD-norm pages and commercial blogs; I did not open or verify them and they are NOT peer-reviewed. CPWD Delhi Analysis of Rates / IS 7272 Part I would be the citable source for norms; not retrieved here.
3. **Brick-specific supply/lead-time/buffer-stock risk in Indian building construction** - only general material-delay RIIs (A02, A10, A14) and news items on brick-kiln closures (Tribune, Down To Earth, Mongabay; snippets only, quoting brick prices rising from Rs 3,700 to Rs 5,000 per 1,000 bricks - unverified, not peer-reviewed).
4. **Festival/holiday absenteeism quantification for India** - none. News snippets mention post-festival return rates (20 % non-return after Holi in a Ludhiana factory; 50-60 % after Chhath in some cases) - non-construction/unverified; do not use.
5. **Rain-days-lost or % productivity loss for MASONRY in India** - none. Only project-level (A09) and RII-level evidence.
6. **Masonry rework rate (% of work redone) with time/cost effect in India** - none. General building-rework percentages I saw (0.5-23 % of project cost; 2-6 %) came from search summaries of non-Indian or unidentified sources; not used.
7. **Delay-cost components (LD, idle labour, overhead) for Indian building sites** - none from a citable source.
8. **Working hours / days per week for Indian masons** - none from a paper; Gerek (Turkey) lists these as variables but I did not extract values; Ponmalar's "work-hours" per 20 days (144-158) is ambiguous.
9. **Bangladesh / Pakistan** - only search snippets (e.g. Springer "Construction delays in privately funded large building projects in Bangladesh", Asian J. Civil Eng. 2018; Nepal RCC delay study in Kalikot). Not opened, so not included as evidence.

## 7. Suggested next steps (for the caller)

1. Obtain the full text of A03 (Loganathan & Kalidindi 2015), A09 (Guha & Biswas 2008), A04/A05 (Nepal brick masonry production rates) and A12 (Mehta & Gaikwad 2017 PDF from KoreaScience) via institutional access or the authors - these are the most model-relevant items whose numbers I could not reach.
2. Get the CPWD Delhi Analysis of Rates / DSR labour norms and IS 7272 (Part 1) for brickwork output norms as the deterministic baseline (m3 or m2 per mason-day), then use A01/A02/A03 only for the variance and loss factors.
3. For the risk matrix, use the RII/II figures (A02, A10, A11, A14) as ordinal seeds only; convert to likelihood/impact with an explicit expert-elicitation step rather than treating RII as a probability.
4. Re-verify A10, A11, A15 numbers against the PDFs (they came through the fetch tool's summariser).
