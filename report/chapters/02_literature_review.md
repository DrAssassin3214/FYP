# Chapter 2. Literature Review

## Purpose and approach

This chapter reviews the published work that bears on one question: what can a risk register for brick masonry draw from the literature, and what must it leave to the user? The review covers delay-cause studies in India and elsewhere, the relative importance index (RII) that most of them use, the risk-management standards and the probability-impact matrix on which registers rest, quantitative schedule risk analysis as context, labour productivity norms (briefly, because they are out of scope), and decision-support tools. It ends with a table of the gap that the project addresses.

The review rests on the evidence corpus held in the project repository: the 11 RII surveys transcribed into `data/literature_seed.json`, the research notes in `Research_Notes/` (topic groups A to F and the P1 to P3 notes), a screened metadata database of open bibliographic records, and a set of references on risk matrices and statistics named in the project's methods review. Each paper cited below was read at one of three depths, and the depth limits what the review says about it: full text; abstract only; or, for a few items, title and metadata only. Where only an abstract was read, the text says so. Papers that the research notes list as unread leads are not cited for their findings.

### The screened corpus

The project built a database of open bibliographic records (OpenAlex metadata) by keyword search and screening on titles and abstracts. The database report records 17,788 harvested records and 3,975 retained after screening (rules version 2026-10-07.1). Two other documents in the repository give different sizes (11,599 input and 3,550 included in the screening report; 21,902 harvested and 5,214 kept in the handoff summary), and the three have not been reconciled. Chapter 3 reports one reconciled count and explains the difference. The figures used here are those of the database report, and they describe the database only. The keyword rules are the authors' own, the screening used titles and abstracts, and the relevance judgements on 4,981 records were made by model reviewers and not checked by a human, so the corpus is a map of what the search found and not a census of the literature.

**Table 2.1.** Composition of the screened corpus (N = 3,975 works).

| Theme (a work may have several) | Works | Share of 3,975 |
|---|---:|---:|
| Delay causes and factors | 2,035 | 51.2% |
| Risk identification and assessment (RII, probability-impact, matrix) | 1,557 | 39.2% |
| Labour productivity and masonry work | 1,121 | 28.2% |
| Rule-based, expert-system and AI risk tools | 512 | 12.9% |

Source: counts from `docs/Corpus_Statistical_Analysis.md` and `docs/Literature_Database_Report.md` (Derived Calculation by regular-expression matching of title and abstract; shares are the counts divided by 3,975 and are not additive). Regular-expression matching measures how many abstracts mention a theme term, not how many studies used a method.

The corpus shows where the literature sits. About half of the works address delay causes, and fewer than 30% mention labour productivity or masonry. Themes overlap little: only 150 works carry both a delay-cause and a productivity-or-masonry tag, and the pairing of delay causes with rule-based or AI tools is also rare (204 works), partly because a title tags one theme (Source: `docs/Corpus_Statistical_Analysis.md`, section 3, with the caveat given there that the negative association is partly built into the tagging). Figure 2.1 shows the share of abstracts that mention each of several methods. Questionnaire surveys appear in 46.9% of abstracts and RII in 10.6% (423 works), whereas large language models appear in 0.4% (14 works) and machine learning in 5.7%; the machine-learning share rises from about 2% of abstracts in 1995 to 2009 to 10.4% in 2023 to 2026. India appears in 6.7% of abstracts (268 works), Sri Lanka in 1.2% and the Middle East in 6.8%.

![Figure 2.1. Share of screened works whose title or abstract mentions each method, with 95% intervals. Source: docs/Corpus_Statistical_Analysis.md section 6a (Derived Calculation, keyword matching; mentions are not evidence that the method was used).](figures/fig2_methods_share.png)

## Delay causes in building construction

### What a delay-cause survey does

A typical delay-cause study compiles a list of candidate causes from earlier papers and interviews, asks a sample of contractors, consultants, clients or workers to rate each cause on a five-point or four-point scale, and ranks the causes by an index computed from the ratings. The RII is the most common index in the corpus and in the studies read here. The ranking identifies which causes respondents consider most important in general. It does not identify which cause occurred on a given project, how often, or how many days it cost.

### Studies in India

Studies carried out in India and read for this project are of three kinds: RII surveys that enter the seed (Karthik & Rao, 2019; Ponmalar et al., 2018; Dixit et al., 2019), RII surveys held out of the seed (Pinky Devi & Sindhu, 2025), and a larger group read at lower depth, collected in Table 2.2.

Karthik and Rao (2019) surveyed 44 respondents from building firms in Telangana on factors affecting labour productivity. The ranked factors with RII of 0.700 or more include unsafe working conditions (0.809), poor planning and unrealistic scheduling (0.791 each), material shortage (0.777), payment delay (0.773) and work at height (0.764) (Source: Literature; `data/literature_seed.json`, M01). Only the 28 of 38 factors at or above 0.700 are listed in the paper's table, so lower-rated factors are absent, and the field case study in the paper concerns walls built from autoclaved aerated concrete (AAC) blocks, not bricks. Ponmalar et al. (2018) surveyed supervisors, project engineers and labourers on two residential buildings in Chennai; respondent numbers are not reported. Lack of experience (0.787), lack of construction material (0.780), lack of tools (0.760), absenteeism (0.751) and payment delays (0.7758) all rate highly, and weather is 0.700 (Source: Literature; M01 and A02 rows in the seed file; the paper's index uses weights of 1 to 4). Dixit et al. (2019) used 201 respondents across consultants, contractors, developers and academia in the Indian construction industry, with RII computed as total score divided by 5 x 201; the paper prints one factor twice with different values (Source: Literature, M06 note).

Pinky Devi and Sindhu (2025) surveyed 72 construction management professionals about delays in infrastructure (roads and bridges), not buildings, and ranked material-related issues first as a group (group mean 0.562), ahead of construction-site factors (0.555) and contractor-related factors (0.506) (Source: Literature; seed-file note for A10). This study is held out of the seed because it is not about buildings, and a repository audit recorded that about ten library risks overlap with its table, although those rows were not entered.

**Table 2.2.** Other Indian studies read for this project and not entered in the RII seed.

| Study | Design and sample | Finding relevant to masonry | Depth read |
|---|---|---|---|
| Reddy & Chambrelin (2021) | Video time-and-motion study, seven residential sites in Andhra Pradesh; one observation of about 1 to 2 hours per site; crews of 2 to 4 | Work efficiency 62.57% to 90.62%; causes named: lack of targets, poor planning and monitoring, material shortage, equipment breakdown | Full text |
| Loganathan & Kalidindi (2015) | Pilot on one project in Tamil Nadu | 20% to 40% production variation between masonry crews (measure not defined in the abstract) | Abstract only |
| Loganathan & Kalidindi (2016) | Interviews on 15 projects in six states | Illness, injury, lack of facilities and payment delays are significant contributors to absenteeism and turnover of migrant workers | Abstract only |
| Guha & Biswas (2008) | Monte Carlo study of a housing project in Kolkata, contractor time and cost data | Monsoon increased project duration by about 5% and cost by about 12% | Abstract only |
| Soundarya et al. (2025) | Six residential sites in Chennai; frequency, severity and importance indices | Overall lag in schedule has frequency index 0.861 and severity index 0.819; rework (importance index 0.55) and inadequate skilled labour (0.53) rank next | Full text (summarised by fetch tool) |
| Mehta & Gaikwad (2017) | Questionnaire to 100 stakeholders; importance index, principal component analysis | Finance-related and labour-related problems dominate (values not in the abstract) | Abstract only |
| Tankkar & Wanjari (2015) | 85 respondents (33 clients, 10 consultants, 42 contractors) | Lack of human resources, poor site management and insufficient coordination are the top three | Abstract only |
| Noushad et al. (2023) | Delphi and RII, high-rise buildings in Kerala, 76 delay causes | No numbers in the preview read | Abstract only |

Source: `Research_Notes/A_masonry_india.md`, cards A01, A03, A08, A09, A11, A12, A13 and A19 (Literature). The number of respondents in Soundarya et al. (2025) was not recorded in the notes.

These studies point the same way as the surveys: labour availability and skill, material supply, planning and management, payment and site conditions recur, and weather is cited but not always among the top factors. The masonry records are small. Reddy and Chambrelin's efficiencies come from seven short observations, Ponmalar et al.'s overrun figures from two projects, and Loganathan and Kalidindi's crew variation from one project, so none supports a probability or a delay distribution for a new site.

### Studies outside India

Six further RII studies in the corpus are from outside India, and two of the five seed studies are from Sri Lanka. Abeysinghe and Jayathilaka (2022) received 163 responses to a questionnaire of 39 delay factors in Sri Lankan construction; shortage of labourers (0.8245), delay in delivering materials (0.8098) and fluctuation of material prices (0.7890) are among the top factors and bad weather conditions is 0.6528 (rank 30 of 39). About 26% of respondents worked on road projects, so the sample is not only buildings (Source: Literature; seed-file note for A14). Manoharan et al. (2022) surveyed 90 upper-grade contractor firms on labour-related factors in Sri Lankan building projects; of 32 factors, 21 exceed an RII of 0.7, with skills shortage first (0.82).

Adebowale and Agumba (2023) pooled RII values of 35 productivity factors from ten surveys in a meta-analysis labelled by the authors as Middle East, although the paper itself includes Malaysia and Vietnam among them. Almeida et al. (2021) surveyed 47 directors, managers and engineers of private building companies in Brasilia on delay causes. Loekito et al. (2026) surveyed 83 construction workers in East Java, Indonesia, on productivity factors. Ouansrimeang and Wisaeang (2024) analysed 30 delayed public projects in Thailand with RII from 380 respondents and ranked contractor financial issues (0.777) and labour issues (0.733 in the results; the abstract prints 0.773) near the top. Hassoon et al. (2025) is the only study in the corpus whose subject is brickwork specifically: its abstract, the only part read, reports RII of 0.874 for planning and 0.856 for team size for brickwork and housing skeleton tasks in Iraq (Source: Literature; `Research_Notes/D_mitigation.md`, abstract only).

### The 11 studies in the seed file

Table 2.3 lists the 11 studies from which the project transcribed RII values. Five serve as seed studies, and six are held out and used only to compare the ranking they imply with the seed order. Figure 2.2 shows the number of rows entered per study.

**Table 2.3.** The 11 RII studies in the seed file: location, sample, scale, method and role.

| ID | Study | Location | Sample | Scale | Index / method | Masonry-specific | Role | Rows entered |
|---|---|---|---|---|---|---|---|---:|
| M01 | Karthik & Rao (2019) | India (Telangana) | 44 respondents | 1-5 | RII; field case on AAC walls | No | Seed | 28 |
| A02 | Ponmalar et al. (2018) | India (Chennai) | Not reported | 1-4 | RII; separate masonry site record | No | Seed | 14 |
| M06 | Dixit et al. (2019) | India | 201 respondents | 1-5 (inferred) | RII | No | Seed | 40 |
| A14 | Abeysinghe & Jayathilaka (2022) | Sri Lanka | 163 respondents | 1-5 | RII | No | Seed | 5 |
| A15 | Manoharan et al. (2022) | Sri Lanka | 90 firms | Not recorded | RII | No | Seed | 5 |
| M10 | Adebowale & Agumba (2023) | Middle East (10 studies) | 10 studies | Pooled RII | Meta-analysis, random model | No | Held out | 33 |
| M15 | Almeida et al. (2021) | Brazil (Brasilia) | 47 respondents | 1-4 | RII | No | Held out | 24 |
| M14 | Loekito et al. (2026) | Indonesia (East Java) | 83 workers | 1-4 stated | RII printed as W/(5N) | No | Held out | 23 |
| A10 | Pinky Devi & Sindhu (2025) | India (infrastructure) | 72 respondents | 1-5 | RII | No | Held out | 6 |
| A21 | Ouansrimeang & Wisaeang (2024) | Thailand (public projects) | 30 projects; 380 respondents | 1-5 | RII with machine learning | No | Held out | 2 |
| HAS25 | Hassoon et al. (2025) | Iraq | Not recorded | Not recorded | RII (abstract only) | Yes (brickwork) | Held out | 2 |

Source: `data/literature_seed.json`, fields `studies` and `rows` (Literature for the study attributes; row counts are a Derived Calculation by counting rows; total 182, of which 92 are in seed studies and 90 in held-out studies). Dixit et al. (2019) state no scale in the text; 1-5 is inferred from the RII denominator. For Loekito et al. (2026) the printed index equals total score divided by 5N although the text gives A = 4.

![Figure 2.2. RII rows entered per study (182 rows from 11 studies). Source: data/literature_seed.json (Derived Calculation).](figures/fig2_rows_per_study.png)

Three features of Table 2.3 limit how the studies can be used. First, none of the five seed studies is a masonry survey: M01 and A02 are general building labour-productivity surveys whose masonry content is a separate field record, and the two Sri Lankan studies include non-building respondents or only the top-ranked factors. Second, the transcription is a subset. A14 contributes 5 of its 39 factors, A15 5 of 32, A02 14 of 35, and M01 lists only the 28 factors at or above 0.700. A repository audit recorded that the omitted factors include some that rank higher than those entered (for example, financial difficulties of contractors, 0.8233, rank 3 in A14). Third, the studies use different scales and sample types, so absolute RII values are not comparable. M14, for example, prints an index that equals W/(5N) on a scale the text describes as 1 to 4.

### Masonry-specific productivity and delay literature

Direct evidence on masonry is thinner than on delay in general. The research notes record the following, mostly at abstract depth.

- Nepal: Lawaju et al. (2021) observed 35 sets of brick masonry output at seven sites in the Kathmandu Valley, chose 13 inputs from an RII survey of 44 factors and fitted an artificial neural network (a test set of five cases); Rana et al. (2023) used a Likert questionnaire with RII and neural-network sensitivity for bricklaying in Surkhet and report that material-related factors form the highest-ranked group (Cronbach's alpha 0.976). Numbers other than these were not seen (abstract only).
- Turkey: Gerek et al. (2015) modelled the productivity of 147 masonry crews with two neural-network techniques using crew size, experience, hours, wall type and mortar type as inputs, with test mean absolute percentage error of about 14.3% to 15.0% (full text). The paper does not report descriptive statistics of crew productivity, so it cannot supply a distribution for an Indian crew.
- Indonesia: Djohim et al. (2024) simulated the schedule of a modest house type and report that wall work was the most influential activity for delay (abstract only; Source: Literature).
- Iraq: Hassoon et al. (2025), as above.

These studies identify which inputs and factors matter for masonry output. They do not provide India-specific, measured daily outputs or delay frequencies that a risk register could use as probabilities. One research note records that the area-based productivity column of Reddy and Chambrelin (2021) is physically implausible and must not be used; only its efficiency percentages are used here, as context.

### Consolidating the factors

Across the seed studies, the same families of factors recur: labour availability, absenteeism and skill; material shortage and delivery; planning and scheduling; payment; site and equipment conditions; weather. The values differ by study. Weather, for instance, takes the values 0.700 (A02), 0.6528 (A14, rank 30 of 39), 0.764 (M01) and 0.6567 (M06) among the four seed studies that rate it, and labour shortage takes 0.751 (A02 absenteeism), 0.8245 (A14) and 0.723 (M01) (Source: Literature; `docs/Project_Handoff_Summary.md` section 8.2). An earlier statement of the project that weather is rated lower than other factors was a post-hoc finding on a ten-risk set, and the audit withdrew it (`docs/Project_Handoff_Summary.md`, section 8.6); it is not made in this report. The review draws only the weaker conclusion that the same families of factor appear in studies from different places, without agreement on their order.

### From factor families to the risk library

The project's risk library groups the factor families into 11 categories. Table 2.4 shows how many of the 46 library risks fall in each category, how many have a survey value in the seed studies, and how many are tagged as project-level and not activity-level. A risk with no seed value stays off the matrix until a user enters numbers.

**Table 2.4.** The 46 library risks by category: total, with a survey (seed) value, and tagged project-level.

| Category | Risks | With seed value | Without seed value | Tagged project-level |
|---|---:|---:|---:|---:|
| Labour | 13 | 9 | 4 | 0 |
| Material | 6 | 4 | 2 | 0 |
| Management | 6 | 4 | 2 | 2 |
| Design | 4 | 3 | 1 | 1 |
| Equipment | 3 | 1 | 2 | 0 |
| Financial | 3 | 2 | 1 | 2 |
| External | 3 | 2 | 1 | 3 |
| Safety | 2 | 2 | 0 | 0 |
| Weather | 2 | 1 | 1 | 0 |
| Quality | 2 | 1 | 1 | 0 |
| Site | 2 | 1 | 1 | 0 |
| **Total** | **46** | **30** | **16** | **8** |

Source: `data/risk_library_masonry.json` (Derived Calculation by counting records by `category`, `seed_status` and `scope`). The 38 original risks were built from the factors transcribed from the 11 studies; the 8 added on 2026-10-08 cite evidence records and carry a masonry-specific form labelled Expert Judgment, to be confirmed by an expert survey.

The table shows the effect of the literature on the library: the seeded risks are the ones that surveys happen to ask about, so labour, material and management risks are well covered by survey values, while masonry-specific conditions such as vertical transport, scaffolding, mortar supply and work-front availability have no survey value and depend entirely on what the user enters.

### Reviews of delay causes

Review papers in the corpus summarise this literature. Romzi and Doh (2022) review causes of project delay and list slow decision making, poor site management and supervision, labour shortage, scope change and late design approval, with number of studies and method not reported in the abstract. Abu Hasan et al. (2025) review 90 publications from 2007 to 2024, identify 93 common conflict factors, add 18 interviews and propose a conflict-delay model. Abd Aziz et al. (2022) review delay mitigation strategies in a systematic review. Ghaeb and Mahjoob (2023), reviewing 38 studies published from 1997 to 2020, observe that most work addresses risk identification and assessment and call for more work on risk response (the journal is modest and the review's method is thin). The reviews support a general point: identification and ranking of delay causes is well covered, and what is done with the ranking at the level of a single activity on a site is less so.

## The relative importance index and its limits

### Definition and a worked example

For a factor rated by N respondents on a scale from 1 to A, the relative importance index is

RII = (sum of the ratings given by all respondents) / (A x N),

so an RII of 1 would mean every respondent gave the top rating. The studies in the seed state this formula in various ways; Dixit et al. (2019), for example, define RII as total score divided by 5 x 201.

Worked example. In Karthik and Rao (2019) the factor "bad leadership skill" received 1, 5, 5, 27 and 6 respondents at ratings 1 to 5 (N = 44). The total score is 1 x 1 + 2 x 5 + 3 x 5 + 4 x 27 + 5 x 6 = 164, so RII = 164 / (5 x 44) = 0.7455 (Derived Calculation from the counts in `data/literature_seed.json`, note on M01). The paper prints 165 and 0.750 for this row; the repository keeps the printed value and records the inconsistency. The sample standard deviation of the 44 ratings is 0.92, so the standard error of the mean rating is 0.92 / sqrt(44) = 0.139 and the standard error of the RII is 0.139 / 5 = 0.028 (Derived Calculation, treating the ratings as independent). An approximate 95% interval is therefore about 0.745 +/- 0.055. A single respondent changing one rating by one point moves the index by 1 / (5 x 44) = 0.0045.

This example shows how much of the RII scale the sampling error of one survey item occupies. In the seed table of the project, the first six risks lie within 0.019 of each other and 24 of 30 risks lie within 0.096, while the standard error of one M01 item is about 0.03 (Source: `docs/Project_Handoff_Summary.md` section 8.2, audit estimate). Differences of less than about 0.05 between two RII values from one survey of this size should not be read as differences in importance.

### Importance is not probability or days

An RII answers the question "how important do respondents think this factor is?" It was designed to rank factors within a study. Three features separate it from a probability or a duration.

1. **It is a rating, not a count.** A factor can be rated important because its effect would be severe, because it occurs often, or because respondents have recently experienced it. The index does not separate frequency from severity. Soundarya et al. (2025) are unusual in reporting frequency and severity indices separately and combining them into an importance index: for the overall lag in schedule their frequency index is 0.861 and severity index 0.819, and the product of these two, 0.705, matches the reported importance index of 0.71 (Derived Calculation from values in `Research_Notes/A_masonry_india.md`). An RII on a single question cannot be decomposed this way.
2. **It is ordinal in use.** Moving from RII to a probability needs a mapping, and no validated mapping from importance to likelihood exists in the sources read. Research on elicitation records precedents for mapping qualitative levels to probability bands in project risk (Curto et al., 2022; Acebes et al., 2024) but not a validation of any mapping from survey importance.
3. **It depends on the respondent group and the scale.** Loekito et al. (2026) surveyed workers, whereas most of the other studies surveyed managers, engineers or consultants. The agreement check in Chapter 4 found a weak negative correlation between the worker survey and the seed order (rho = -0.18, 13 risks, p = 0.55, not significant); this is consistent with workers and managers rating factors differently but cannot be distinguished from noise with these data. Scales of 1 to 4 and 1 to 5 give different absolute RII values for the same opinions.

### Other limits recorded in the project's audit

Beyond the points above, the project's audit recorded the following limits of the secondary data. Truncation: M01 reports only factors with RII of at least 0.700 (28 of 38). Selection: the seed transcribes only a subset of factors from several papers. Single-study support: 14 of the 30 seeded risks rest on one study. Instability: when the ranking built from the other seed studies is compared with a left-out seed study's own order, the Spearman correlations are 0.09 (M01, n = 13), 0.37 (A02, n = 10), 0.64 (M06, n = 9) and 0.60 (A14, n = 4), none significant, and A15 cannot be tested with n = 2 (Source: `docs/Project_Handoff_Summary.md` section 8.4; Derived Calculation). Agreement with held-out studies is weak and not significant after correction for multiple testing (section 8.5 of the same document). Chapter 4 gives the method and numbers; they are summarised here because they determine how the RII may be used in a tool. It may order risks coarsely when nothing else is known; it cannot stand in for site data.

## Risk management standards

### ISO 31000

ISO 31000 is the international standard that gives principles and guidelines for risk management and describes a process in which risk is identified, analysed, evaluated and treated, with communication, monitoring and review throughout (ISO, n.d.). The standard is used here as the organising frame of the tool and not as a source of numbers. The wording of the process stages follows the project's own methodology description (`docs/Project_Handoff_Summary.md`, section 2) and should be checked against the current edition of the standard before submission (the edition year is not recorded in the repository).

### IEC 31010

IEC 31010 is the companion standard on techniques for risk assessment (International Electrotechnical Commission [IEC], n.d.). It is cited because the techniques of this project, a consequence-and-likelihood matrix, a register, and (optionally) Monte Carlo simulation, are among the kinds of technique that such standards catalogue. The content of the standard has not been reviewed in detail for this report, and the claim that it lists these techniques should be checked against the standard text.

### Mapping the tool onto the process

Table 2.5 shows which part of the tool serves each stage of the ISO 31000 process, and what the tool does not do.

**Table 2.5.** Stages of the risk-management process and the corresponding parts of the tool.

| Process stage | Part of the tool | What the tool does not do |
|---|---|---|
| Establish context | Case record: project, activity, planned duration, site facts | Does not set the organisation's risk appetite |
| Identify | Library of 46 risks; 22 site-fact rules; evidence-cited AI suggestions of names and mechanisms | Does not discover risks outside the library unless the user adds them |
| Analyse | User-entered probability and delay range with Source label; ordinal literature tier for 30 risks without entered numbers | Does not supply probabilities or delays |
| Evaluate | 5x5 probability-impact matrix with stated edges and thresholds (Assumptions); prioritisation by score | Does not decide which level is acceptable |
| Treat | Register fields for owner, trigger, response type, action, review date; optional comparison of responses using entered costs | Does not recommend a response or supply effect sizes |
| Monitor and review | Review date field; exports for the review meeting | Does not collect actual outcomes |

Source: `README.md`, `docs/Project_Handoff_Summary.md` sections 2, 8.14 and 9 (descriptive).

## Risk matrices and their critique

### Use of the matrix

A probability-impact matrix assigns each risk to a probability class and an impact class and reads a level from the cell. In the tool, the classes run from 1 to 5, the score is the product of the two class numbers, and the level is Low for a score up to 5, Moderate for 6 to 10, High for 11 to 15 and Extreme for 16 or more. These thresholds are Assumptions of the tool, not values from a source. Table 2.6 shows the resulting scores and levels.

**Table 2.6.** Score (probability class x impact class) and level in the tool's 5x5 matrix.

| Probability class \ Impact class | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 5 | 5 Low | 10 Moderate | 15 High | 20 Extreme | 25 Extreme |
| 4 | 4 Low | 8 Moderate | 12 High | 16 Extreme | 20 Extreme |
| 3 | 3 Low | 6 Moderate | 9 Moderate | 12 High | 15 High |
| 2 | 2 Low | 4 Low | 6 Moderate | 8 Moderate | 10 Moderate |
| 1 | 1 Low | 2 Low | 3 Low | 4 Low | 5 Low |

Source: Derived Calculation from the thresholds in `docs/Project_Handoff_Summary.md` section 4 (Assumption). Counting cells gives 10 Low, 7 Moderate, 4 High and 4 Extreme of 25.

### Cox (2008) and Duijm (2015)

Cox (2008) examined risk matrices and concluded that they have four problems: poor resolution, errors (a matrix can rate a quantitatively smaller risk higher than a larger one), suboptimal resource allocation and ambiguous inputs and outputs, and that they should be used with caution and with careful explanation of the embedded judgements (this review read the abstract only). Duijm (2015) gives recommendations on the use and design of risk matrices (this review read the reference details only; the paper's detailed recommendations should be reviewed before the chapter is finalised).

Table 2.6 illustrates the range-compression point that follows from Cox's critique. Because the level is a function of the product, the whole first row and first column are Low whatever the other class is: a risk in probability class 1 and impact class 5 scores 5 and is Low, and so is a risk in probability class 5 and impact class 1. Only 8 of 25 cells are High or Extreme. The thresholds are a design choice: a different cut at 4 or 6 would move cells between levels. Chapter 6 reports a sensitivity analysis on how many risks of the example case change level when the class edges and thresholds change. Two consequences are drawn for the design.

1. The matrix is presented as an aid to ordering, and the thresholds are printed on every export as Assumptions.
2. Risks with impact class 5 and an entered probability are also listed separately, as a filter and not as a score, so that a rare, severe risk is not hidden in the Low band.

### Beyond the matrix

Several papers in the corpus compare or combine matrices with simulation. Acebes et al. (2024) propose a quantitative methodology for risk prioritisation as an alternative to probability-impact matrices; the research notes record that rankings from a matrix and from Monte Carlo analysis differ in their example. Koulinas et al. (2021) use a risk matrix to set probability and impact for each activity and then run Monte Carlo simulation for an artificial-lake project in Greece, with a qualitative mitigation loop. Starczyk-Kolbyk and Jedras (2025) compare a matrix and Monte Carlo on cost for twelve risks of a high-rise office and report a high level of consistency between the methods (abstract only). Canesi et al. (2025) integrate a probabilistic risk matrix with Bayesian Monte Carlo simulation for cost overruns in infrastructure (abstract only). The papers show that matrix and simulation are used together, and that the relation between their rankings depends on the case.

## Quantitative schedule risk analysis: context

### Monte Carlo and three-point estimates

Monte Carlo schedule risk analysis samples activity durations and risk events many times and reports the distribution of the project finish. Activity durations are often given as three-point (optimistic, most likely, pessimistic) estimates under a beta-PERT assumption. The literature read for this project is critical of the assumptions behind that choice: the PERT variance is fixed by the range alone (Hahn, 2008), the mean and variance formulas do not correspond to a beta whose mode is the elicited value (Herrerias-Velasco et al., 2011), and Trietsch et al. (2012) argue for a lognormal core and report a Parkinson effect in recorded activity times. Flyvbjerg (2006) documents optimism bias in forecasts for large infrastructure projects, which implies that three-point estimates elicited from project teams may be too narrow. Song and Vanhoucke (2025) treat the interaction between risks in schedule risk analysis.

### Risk-event simulation in construction schedules

Monte Carlo simulation with risk events and mitigation has been applied to construction projects, including in India. Gheewala et al. (2025) simulated an elevated metro rail project with a baseline schedule of 711 days, 17 risks prioritised by a probability-impact approach and 1,000 simulations; all risks together gave a mean duration of 842 days, and a mitigation plan costing Rs 3.32 million reduced the mean and maximum durations by 26 and 76 days (abstract only). Ichsan et al. (2025) simulated the schedule of the Jakarta Central Railway Station project at the level of nine critical activities and compared pre- and post-mitigation (residual) risk, with response effects from a focus group of five panel members. Guha and Biswas (2008) applied Monte Carlo to monsoon effects on a Kolkata housing project. Koulinas et al. (2020) built a simulation-based expert system for delay risk in a hotel renovation. Hadad and Keren (2025) combine Monte Carlo simulation with budget-constrained selection of risk responses on an office building. Prins et al. (2022) model risk occurrence as a binary variable with a probability and apply Beta-PERT to durations in a mitigation-planning method for a tunnel project; this is a preprint. Table 2.7 sets these studies beside the present project.

**Table 2.7.** Closest published work combining risk events, simulation and mitigation, and how this project differs.

| Study | Level | What it does | Difference from this project |
|---|---|---|---|
| Prins et al. (2022) | Project (tunnel) | Binary risk occurrence, Beta-PERT, mitigation optimisation | No single-activity masonry focus; inputs from a project risk register |
| Ichsan et al. (2025) | Nine critical activities (railway station) | Pre- and post-mitigation schedule simulation | Response effects from a five-person focus group; not masonry |
| Gheewala et al. (2025) | Project (metro, India) | Matrix-prioritised risks, simulation, mitigation plan cost versus days saved | Project level; mitigation modelled as one plan, not as alternatives |
| Hadad & Keren (2025) | Project (office building) | Simulation with response budgeting | Dollar-based, project level, no schedule network |
| Koulinas et al. (2021) | Activity (lake project) | Risk matrix, simulation, qualitative mitigation loop | Not masonry; mitigation is a qualitative loop without residual quantification |
| Djohim et al. (2024) | Activity-level schedule of a house | Simulation identifies wall work as most influential | No mitigation |

Source: `Research_Notes/F_novelty_validation.md`, items F01, F03, F04, F05, F11 and F12 (Literature; abstracts or full text as marked in the notes).

The same research notes conclude that the individual mechanics of risk-event simulation with mitigation are published and not new, and the project therefore makes no claim to novelty in them. Two conditions apply to the simulation studies above. Their inputs (probabilities, ranges, response effects) come from project registers, contractor records, expert panels or focus groups, and the research notes found no construction paper that reports a calibration or back-test of a simulated range against actual outcomes (the closest, Ichsan et al., 2025, claims an accuracy figure in its abstract without a back-test in the text read). Khodabakhshian et al. (2023), in a systematic review of 48 papers on deterministic and probabilistic risk management approaches, note that experience, prior knowledge and historical data are required and often not documented or easily accessible. This is the data-scarcity problem that confronts a user of the optional layer in this project: the simulation can run, but the numbers it needs must be entered by the user and carry their own Source labels.

## Labour productivity norms (context only; out of scope)

The registered title mentions labour productivity. This section records what the research notes found, briefly, to show why productivity was not modelled.

India's planning norms for masonry labour are published as labour output constants. IS 7272 (Part 1), adopted in 1974 and reaffirmed in 2010, gives labour-days per unit of work for building works in north India, derived by the Central Building Research Institute from work-measurement observations on sites in Delhi and Roorkee (Bureau of Indian Standards, 1974). For brickwork in walls thicker than one brick the constant is 0.94 mason-days per cubic metre (with 1.80 labourer-days and 0.20 water-carrier-days). The CPWD Analysis of Rates for Delhi 2007 gives the same mason labour quantity for brickwork in superstructure, 0.47 plus 0.47 mason-days per cubic metre (Central Public Works Department, 2008). The research notes record that the CPWD brick masonry labour constants are identical across the 2007, 2012 and 2014 editions read and equal the 1974 constants, so they are long-standing planning norms and not fresh measurements. A state schedule read (Odisha, 2006) gives a mason total about 1.5 to 1.9 times the CPWD figure, with larger bricks, so published norms differ between sources by a large factor. The reading of the unit of the one-brick-wall row of IS 7272 is an inference from a low-resolution scan (Source: Literature; `Research_Notes/P3_india_norms.md`, records P3-01 to P3-04).

A norm is a planning constant with allowances built in; it is not a measurement of what a crew achieves on a given day, and it gives no distribution. Measured productivity studies read for this project are small (Reddy & Chambrelin, 2021; Loganathan & Kalidindi, 2015) or come from other countries (Gerek et al., 2015). A productivity model would need measured daily output by crew on Indian sites, which the project does not have. A defect in the legacy norms file in the repository was also recorded in the audit. Productivity is therefore listed in Chapter 8 as future work with its data prerequisites, and no CPWD number is used in any result in this report.

## Elicitation, verification and validation

The tool leaves probabilities and delays to the user. Where they come from experts, the elicitation literature applies, and where the tool itself is to be judged, so does the literature on verification and validation. This section records the sources the project draws on for its future-work plan (Chapter 8); none of them has been applied in the work reported here.

**Elicitation.** Bedford et al. (2006) review expert elicitation for reliability design and state that accurate subjective probabilities are not obtained by simply asking for a number, naming four standard biases (motivational, cognitive, anchoring and availability) and recommending structured elicitation with feedback. Williams et al. (2021) compare aggregation methods on a clinical example with three experts and ten seed questions and find that all three aggregation methods outperformed the individual experts, with equal weights a defensible default when experts and calibration questions are few. Dharmarathne et al. (2022) point out that tests of expert calibration on a modest number of questions have poor power. Ameyaw et al. (2016) reviewed 88 Delphi papers in construction engineering and management: panel sizes ranged from 3 to 93 with 8 to 20 the most common, rounds from 2 to 6, and a Likert scale was used in 41 papers; Delphi output is ordinal, and the review says nothing about converting Likert scores to probabilities. Curto et al. (2022) and Acebes et al. (2024) attach a probability range to each qualitative level (for example, "High" as a uniform range of 20% to 35% in one project) and simulate within the range; the ranges are set by each project's expert committee and are not transferable. These sources imply that, in this project, any mapping from a rating to a probability would be an explicit Assumption with a sensitivity check, and that an expert survey should report its sample size and agreement, not only a mean.

**Verification and validation.** Sargent (2013) describes approaches to deciding model validity, conceptual model validity, model verification, operational validity and data validity, and a procedure for documenting validation (the research notes record a discrepancy in the venue metadata of this item, which should be checked before submission). Verification, meaning that the software computes what its specification says, is possible without site data and is what Chapter 6 reports. Operational validity, meaning that outputs are accurate enough for their purpose on real cases, needs site outcomes, and is not claimed. Fowler et al. (2024) offer a template for face validity of a decision-support tool by surveying subject-matter experts (in a cybersecurity setting, not construction); a similar trial with site engineers is the nearest evaluation step available to this project and is proposed in Chapter 8.

## Decision-support tools for delay risk

### Tools in the literature

The tools reported in the corpus fall into three groups. The first is schedule risk software used in case studies, such as Primavera P6 with Risk Analyzer in Gheewala et al. (2025) and @RISK in Ichsan et al. (2025), which run simulation on a schedule and rely on the user to supply the distributions and probabilities. The second is expert systems and data-driven models: Koulinas et al. (2020) describe a simulation-based expert system for delay risk, and Zorrilla et al. (2026) report a decision-support system that applies clustering, anomaly detection and explainable machine learning to a dataset of construction documents, with an F1 score of 0.73 in bottleneck detection (abstract; no simulation of mitigation). The third is the use of large language models for risk identification and classification.

### Large language models

Vilibic et al. (2026) applied several large language models to risk identification in one project and conclude that human expertise remains crucial for prioritisation, contextual interpretation and mitigation. Erfani and Khanjar (2025) compare configurations for risk classification and report that few-shot GPT-4 reaches an F1 of 0.81 against 0.86 for the best classical model (BERT with a support vector machine). Martin et al. (2025) examine ChatGPT limitations in risk identification, mitigation strategies and user experience (the notes record the title only). A systematic review of large language models in smart construction (Gao et al., 2026) lists hallucination control and domain adaptation among persisting challenges. In the corpus, large language models appear in 14 abstracts, 0.4% of 3,975 works (Figure 2.1). The use in this project is limited to proposing risk names, mechanisms and evidence identifiers, and the design rejects numeric output (Chapter 5); the literature supports caution about letting such models supply numbers.

### What the tools do not provide

Within the corpus read, the tools take probabilities and durations as user input and do not record, for each number, where it came from. They are project-level more often than activity-level. The papers above also say little about how the tool user, a site engineer, would see which risk conditions are present on a particular day. A register kept as a plain spreadsheet has only the columns its author gives it; whether it carries a source for each number depends on the author. These observations are about the studies read and are not a survey of commercial software, which this project did not carry out. Chapter 7 compares features of the tool with the tools that could be checked.

## Summary and the research gap

**Table 2.8.** Summary of what the literature provides, what it lacks, and how this project responds.

| Need of a site engineer | What the literature provides | What it lacks | How this project responds |
|---|---|---|---|
| Know which delay risks to check for masonry | Many delay-cause surveys; ranked lists; reviews | Few masonry-specific surveys; most are general building or infrastructure; mixed project-level and activity-level items | A library of 46 risks, each with supporting survey factors, tagged by scope; 22 site-fact rules |
| Tell how important a risk is when nothing is entered | RII values from India and Sri Lanka | RII is importance, not probability or days; studies disagree weakly; one study per risk for 14 of 30 | An ordinal starting position labelled as an Assumption and replaced by entered values; the weak agreement reported |
| Record a probability and impact with their source | Matrix and register practice; Cox (2008) on matrix weaknesses | No recorded source for each number in the tools reviewed | Six Source labels on every number; assumptions printed on every export |
| Quantify schedule effect | Published simulation methods and Indian and international case studies | Inputs from teams or panels; no back-test on masonry activities | Optional layer using only entered numbers; no defaults |
| Use AI assistance safely | Studies of language models for identification and classification | Risk of hallucination; numbers from models unverified | AI may propose names and evidence identifiers only; numeric output rejected |
| Judge whether the tool works | Verification and validation guidance | No site data and no practitioner evaluation in this project | Software verification now; expert rating, usability and site validation defined as future work |

Source: synthesis of sections 2.2 to 2.9 of this chapter and the cited sources (descriptive).

The gap, in the form given in Chapter 1, is practical: published rankings do not carry into site risk registers, general tools ask for probabilities and impacts without tying them to evidence, and within this search we did not find an activity-level masonry tool in which each value carries its source. The search was by keyword on titles and abstracts, and the finding is not a statement that no such tool exists. The review also shows what the project cannot rely on: the survey rankings are weak and unstable as a base for probabilities, masonry-specific measured data are scarce, and simulation and matrix methods are established and not new. The project therefore limits itself to identification, a source-labelled register and prioritisation, with simulation as an optional layer that depends entirely on what the user enters.
