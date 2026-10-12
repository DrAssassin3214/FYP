# Chapter 1. Introduction

## Background

### Brick masonry in Indian building construction

Brick and block masonry is labour-intensive hand work. In a framed residential or commercial building the walls are laid by gangs of masons and helpers after the structural frame is cast, and plastering, services and finishing trades cannot proceed in a room until its walls are up. A delay in masonry therefore delays the activities that follow it. The activity depends on the daily availability of skilled labour, on bricks or blocks and mortar materials arriving and being staged near the working face, on access and scaffolding, on weather, and on payment and supervision arrangements that determine whether a gang turns up and stays.

Three strands of published evidence, read for this project, describe how this work behaves on Indian sites. They are small studies and none of them is a representative sample of India, so they are used here only to describe the kind of problem, not to size it.

- Reddy and Chambrelin (2021) video-recorded brickwork at seven residential sites in Andhra Pradesh. Each site was observed once for roughly one to two hours, and the reported work efficiency ranged from 62.57% to 90.62% (Source: Literature; `Research_Notes/A_masonry_india.md`, card A01). The authors attribute low efficiency to lack of work targets, poor planning and monitoring, material shortage and equipment breakdown. The sample is seven short observations and the area-based productivity column of the paper is not usable, as discussed in the research notes.
- Ponmalar et al. (2018) recorded the brick masonry activity on two three-storey residential buildings in Chennai. Both activities were planned as 20 working days. The authors report 6.14% and 8.17% work-hour overrun and that 7 and 8 of the 20 days respectively were ineffective (Source: Literature; card A02). The definitions are the authors' own and the sample is two projects.
- Loganathan and Kalidindi (2015) report, from the abstract of a pilot study on one project in Tamil Nadu, a 20% to 40% production variation between masonry crews (Source: Literature; card A03; the abstract does not define the variation measure, and the full text was not accessible).

The same research notes record a second set of studies that name the drivers of workforce unavailability in India. Loganathan and Kalidindi (2016) interviewed project managers and labour sub-contractors on 15 projects in six states and report illness, injury, lack of basic facilities and payment delays as significant contributors to absenteeism and turnover among migrant construction workers. Guha and Biswas (2008) used Monte Carlo simulation on a housing project in Kolkata and report that the monsoon increased project duration by about 5% and cost by about 12% (Source: Literature; abstract only).

### Delay research in India and elsewhere

Most of the published work on construction delay asks practitioners to rate a list of candidate causes and then ranks the causes by an index, most often the relative importance index (RII). Chapter 2 reviews these studies in detail. Two features of this literature matter for the problem stated below. First, most surveys cover building or infrastructure construction in general, not one activity. Second, the output of a survey is a ranking of importance, whereas a site engineer who has to decide what to do on Monday morning needs to know which of the listed risks is present on the site, how likely it is to cause loss of working days, and what the loss would be. The ranking does not state these.

### Risk registers and matrices in practice

Risk management standards describe a cycle of identifying, analysing, evaluating and treating risk (International Organization for Standardization [ISO], n.d.). In project practice this cycle is commonly recorded in a risk register and summarised on a probability-impact (P-I) matrix, in which each risk is placed by a probability class and an impact class and given a level. A matrix is easy to read and to produce, but it is a coarse device with known weaknesses (Cox, 2008), which Chapter 2 discusses because they shape several design decisions in this project.

## Problem statement

A site engineer or planning engineer who wants to keep a risk register for the masonry activity of a building faces three practical problems.

1. **Identification is unaided.** There is no short, referenced list of the delay risks that are specific enough to masonry to be checked against a site, and general lists of delay causes mix project-level, contractual and activity-level items.
2. **Numbers have no source.** A register needs a probability and an impact for each risk. Practitioners can enter them, but a number typed into a spreadsheet usually carries no record of whether it came from past records, a published study, a colleague's opinion or a guess. A reviewer cannot tell which numbers are evidence and which are assumptions.
3. **Published rankings are not usable as probabilities.** Importance indices from delay surveys are the most accessible quantitative literature, but an RII is a rating of how important respondents consider a factor. It is neither a probability that the factor occurs nor a number of days lost. Using it as either, which is tempting because it is a number between 0 and 1, would present an opinion rating as a measurement.

The project therefore asks what a tool can honestly do for the masonry activity when the user has, at best, partial project data and the published literature offers rankings but not probabilities, and how far such a tool can be checked without site data.

## Aim

To develop and verify an offline tool that helps site engineers identify, register and prioritise delay risks in a brick/block masonry activity, with every value traceable to its source and published survey evidence used only as a labelled ordinal starting point.

## Objectives

1. Compile and verify a masonry delay-risk library from published delay/productivity surveys, with a documented and inter-coder-checked factor-to-risk mapping.
2. Implement site-condition rules, a source-labelled risk register and a 5x5 probability-impact matrix with all assumptions stated.
3. Analyse how consistent published RII rankings are (cross-study agreement, held-out comparison, sensitivity of matrix placement) to establish how far literature can stand in for project data.
4. Verify the software and evaluate it with practitioners (expert likelihood/impact ratings, face validity, usability), defining site validation as future work.

Two of these objectives are only partly met in the work reported here, and the report says so in the chapters concerned. For Objective 1, the mapping was done by a single coder, so the inter-coder check has not been carried out. For Objective 4, the software was verified by automated tests and by a hand-worked calculation, but no practitioner evaluation (expert rating or usability session) has been run. Table 1.1 records the status of each objective.

**Table 1.1.** Status of the objectives at the time of writing.

| Objective | Status | Where reported |
|---|---|---|
| 1. Library and mapping | Library of 46 risks built; 182 RII rows transcribed from 11 studies and compared with the printed tables; mapping done by one coder, second-coder check not done | Chapters 3 and 4 |
| 2. Rules, register, matrix | Implemented, with 22 site-fact rules; assumptions listed in an Assumption register | Chapter 5 |
| 3. Consistency of rankings | Cross-study agreement, leave-one-study-out cross-prediction, held-out comparison and sensitivity analyses done; results weak and not significant after correction | Chapter 4 |
| 4. Verification and evaluation | Software verification done; practitioner evaluation not done; site validation defined as future work | Chapters 6 and 8 |

Source: counts from `README.md` and `docs/Project_Handoff_Summary.md` section 9 (Literature / Derived Calculation from repository files); status entries are the authors' statement of work done.

## Scope

**In scope.**

- One construction activity: brick or block masonry in building projects in India.
- Identification of delay risks from a literature-derived library and from rules applied to site facts that the user enters.
- A register in which each risk can carry a probability, a delay range, a Source label for each number, an owner, an early-warning trigger, a response type (avoid, reduce, transfer, accept), an action and a review date.
- A five-by-five probability-impact matrix with stated edges and level thresholds, and exports (HTML report, image, CSV, Markdown, case file).
- An ordinal literature starting position, labelled as an Assumption, for the 30 of 46 library risks that have a survey value in the seed studies.
- An optional quantitative layer (Monte Carlo schedule simulation, delay-cost and expected-monetary-value comparison of responses) that uses only numbers entered by the user, each with a Source.
- A secondary-data analysis of the 11 published surveys held in the repository.

**Out of scope.**

- Any prediction of labour productivity, and any use of CPWD or BIS labour output norms in the tool. Legacy code for these exists in the repository, is not connected to the interface and is not used in any result in this report.
- Collection of site data, and any claim about the accuracy of the tool on real sites.
- An expert survey (a form is described in the project records; it has not been administered) and a usability study.
- Other activities (plastering, concreting), project-level scheduling, and cloud or mobile versions.
- Any probability, delay or cost supplied by an AI model.

**Limitations that apply to the whole report.** No site data were collected and no expert survey was run. The example case used to demonstrate the tool is illustrative and its numbers are not evidence. The RII values come from general building-construction surveys in India and Sri Lanka, not masonry-specific surveys, and the transcription covers only a subset of the factors in several of the papers. These limits are repeated where they bear on a result.

## Scope revision relative to the registered title

The registered title of the project is "Framework for Brickwork Labor-Productivity and Delay-Risk Prediction Using Managerial Factors in Selected Indian Building Projects". The first project plan described a desktop application that would take daily site conditions, look up a delay probability and a mitigation cost in a rules matrix, run a Monte Carlo simulation of the schedule using a work breakdown structure held in a database, and output a financial command based on expected monetary value. On 28 September 2026 the scope was cut to identification, register and matrix, The project records give the date of the decision but no written rationale. The reasons on which this report relies are that no site data were available, and that the probabilities, delays and costs the larger design needs could not be taken from the literature, since the survey rankings the project holds are importance ratings and cannot supply them. The code of the larger version was kept on disk. On 8 October 2026, at the team's request, a quantitative layer was reconnected that uses only user-entered numbers (Handoff section 8.14). The title has not been changed in the project records. Table 1.2 maps each term of the registered title and of the first plan to what was done, and why.

**Table 1.2.** Scope revision: registered title terms and first-plan features against what was done and what was deferred.

| Term or feature | Status in this report | What was done | Why, and what would be needed |
|---|---|---|---|
| "Framework" | Done (as a process) | A risk-management process of identify, analyse, evaluate and record, following the cycle described in ISO 31000, implemented as library, rules, register, matrix and exports | No change of meaning; it is a procedure and a tool, not a new theory |
| "Brickwork" | Done | Library, rules and the register are written for a brick/block masonry activity. The survey seed is not masonry-specific (see Chapter 4) | The surveys are general building-construction surveys; masonry-specific ratings would need an expert survey |
| "Labor-Productivity" | Deferred | Not modelled. Legacy productivity models and an India labour-norms file exist in the repository and are not used in any result | Needs measured output data from sites; a known defect in the legacy norms file was found in the audit; CPWD norms are planning norms, not measured productivity |
| "Delay-Risk" | Done (identification and prioritisation) | Risks are identified, registered and placed on a 5x5 matrix; an optional layer can simulate delay from entered numbers | Probabilities and delays for real sites need project records or expert elicitation |
| "Prediction" | Not done; wording withdrawn | The tool orders risks; it does not predict delays | An RII is importance, not likelihood, and no site outcome data exist to test a predictive claim |
| "Managerial Factors" | Partly done | The library contains management-type risks (for example poor planning, supervision, site management, communication, labour discipline) and some site facts relate to them. They are not analysed as a separate group of factors | A managerial-factor analysis needs project-level data on supervision hours, crew ratios and material staging |
| "Selected Indian Building Projects" | Not done | No projects were selected or studied. The seed uses published surveys from India and Sri Lanka | Needs site access and permission; a site data-collection form is described in the project records but was not used |
| Desktop application (PySide6) | Done, with a qualification | A local web interface runs offline in a browser and inside a PySide6 desktop window | The PySide6 window hosts the same local interface; it is not a separate native interface |
| Rules matrix of 27 states giving delay probability and mitigation cost | Replaced | 22 rules flag risks from site facts and give no numbers; the 5x5 matrix uses user-entered or labelled values | A lookup of probability and cost needs a source for each cell |
| Monte Carlo (10,000 runs), P90 delay, work breakdown database | Optional layer only | A Monte Carlo schedule simulation exists in the optional layer and runs on entered numbers. The database-based work breakdown is not used | No default distributions are supplied; results are only as good as the entered ranges |
| Expected monetary value and the "authorize mitigation / accept risk" command | Optional layer only | The layer compares entered response costs and effects with delay cost and returns a command worded as "preferred under the stated criterion" | No cost or effect size is supplied by the tool; real values need quotations and site records |
| CPWD labour norms | Not in the product | Context only, in Chapter 2 | Legacy norms file has a documented defect; out of scope |
| Daily dynamic risk from site conditions | Partly done | Site facts entered by the user trigger rules that flag risks | Rules are logical conditions labelled Assumption; practitioner endorsement not yet collected |
| Publication in a Scopus-indexed journal | Not supported by the present work | Not claimed | See Chapter 8 for routes that the work could support |

Sources: registered title and first-plan description from the project statement; scope history from `docs/Project_Handoff_Summary.md` sections 1, 8.13, 8.14 and 9; status of each item from `README.md` and the repository.

The decision on whether to change the registered title has not been recorded in the project files; a title that matches the work is proposed on the cover of this report, and the choice rests with the guide.

## Research gap

The review in Chapter 2 supports the following statement of the gap, stated as modestly as the evidence allows. Indian delay-cause studies rank factors by RII but stop at a ranking that does not carry into site risk registers. General risk tools and templates require the user to enter probabilities and impacts and do not tie them to evidence. Within the search reported in Chapter 2 we did not find an activity-level tool for masonry in which site conditions feed a register and every value carries a source label. Absence from a keyword search of titles and abstracts is weak evidence, and the corpus was not searched in full text. The gap is therefore a practical one that this project addresses, and not a claim that no such tool exists.

## Contribution

The contributions of the work are practical and modest.

1. A referenced library of 46 masonry delay risks, with the survey factors that support each one, and a documented rule for mapping survey factors to risks.
2. A verified secondary dataset of 182 RII rows from 11 studies, with a recorded source location and a list of the errors and omissions found in the transcription.
3. An offline tool in which every number in a register carries one of six Source labels, and in which assumptions of the tool (class edges, level thresholds, the equal-count bands, the one-class step for a rule flag) are named, listed and printed on every export.
4. An analysis, from published data only, of how far survey rankings agree with each other, which shows that the agreement is weak and so limits how much weight the literature starting position can bear.
5. A set of withdrawn claims, recorded with the reason, as a guide for later work that uses RII data in a risk register.

The project does not propose a new risk-analysis method. The probability-impact matrix, RII, Monte Carlo simulation and expected-value comparison are all established, and Chapter 2 cites published work that already combines several of them for construction schedules. The report makes no claim that the tool predicts delays, that it is accurate on real sites, or that it is the first of its kind.

## Structure of the report

Chapter 2 reviews the literature on delay causes, the RII method and its limits, risk-management standards, the critique of risk matrices, quantitative schedule risk analysis as context, labour productivity norms (briefly, as out of scope) and decision-support tools, and ends with a summary of the gap. Chapter 3 describes the methodology: design approach, literature search and screening, data extraction and verification, the factor-to-risk mapping, the construction of the seed and the statistical plan. Chapter 4 presents the secondary-data analysis of the 11 surveys, including what it does not show. Chapter 5 describes the system design: requirements, architecture, case schema, library, rules, matrix logic, the Assumption register and the guard on AI output. Chapter 6 reports software verification, a worked example labelled illustrative, sensitivity of the matrix and the known defects. Chapter 7 discusses what can and cannot be claimed and the threats to validity. Chapter 8 gives conclusions, limitations and future work, including the data that the productivity, Monte Carlo and expected-value parts of the registered title would need. References and appendices follow, including the 182-row seed table, the risk library and the rule table.

A note on numbers. Every number in the report is labelled with its Source (Literature, Historical Data, User Input, Expert Judgment, Derived Calculation or Assumption) in the sentence, table note or caption where it appears. No value labelled Historical Data appears in this report, because no site records were obtained.
