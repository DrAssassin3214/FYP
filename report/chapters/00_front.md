<!-- Front matter: title page, certificate, declarations, acknowledgements, abstract, keywords, abbreviations. Names, roll numbers and dates are deliberately left blank for the team to fill in. -->

# Title page

**DELAY-RISK IDENTIFICATION AND PRIORITISATION FOR BRICK MASONRY WORK IN INDIAN BUILDING PROJECTS: AN EVIDENCE-TRACEABLE DECISION-SUPPORT TOOL**

*(Registered project title: "Framework for Brickwork Labor-Productivity and Delay-Risk Prediction Using Managerial Factors in Selected Indian Building Projects". Section 1.6 explains how the work reported here relates to the registered title.)*

A Final Year Project Report submitted in partial fulfilment of the requirements for the degree of

**Bachelor of Technology in Civil Engineering**

by

| Name | Roll / enrolment number |
|---|---|
| [Team member 1: full name] | [number] |
| [Team member 2: full name] | [number] |
| [Team member 3: full name] | [number] |

Under the guidance of

[Name and designation of project guide]

[School / department name]
[Full institution name and campus, to be confirmed by the team: NICMAR, Pune]

[Month and year of submission]

\newpage

# Certificate

This is to certify that the project report entitled **"Delay-Risk Identification and Prioritisation for Brick Masonry Work in Indian Building Projects: An Evidence-Traceable Decision-Support Tool"** (registered title: **"Framework for Brickwork Labor-Productivity and Delay-Risk Prediction Using Managerial Factors in Selected Indian Building Projects"**) is a record of the work carried out by

1. [Name of team member 1], [number]
2. [Name of team member 2], [number]
3. [Name of team member 3], [number]

under my guidance, in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in Civil Engineering at [institution name]. To the best of my knowledge the work has not been submitted to any other institution for the award of a degree or diploma.

Place: [place]  
Date: [date]

| | |
|---|---|
| [Signature] | [Signature] |
| [Name, designation of project guide] | [Name, designation of Head of Department / Programme Chair] |

\newpage

# Declaration

We declare that this report is our own account of the project. Where we have used the work of others, we have named it and listed it in the References. Every numerical value in the report is either (a) copied from a cited published source, (b) computed from such values by a script or calculation that is named next to the result, (c) entered by a user of the tool as a labelled example, or (d) stated as an assumption of the tool and labelled as one. We have not collected, fabricated or altered any site data or survey responses. No site data and no expert survey were collected for this report, and the example case in the report is illustrative only.

We understand that any misrepresentation of the above is a breach of academic integrity.

| Name | Signature | Date |
|---|---|---|
| [Team member 1] | | |
| [Team member 2] | | |
| [Team member 3] | | |

\newpage

# Declaration on the use of AI assistants

This project was carried out with substantial help from AI coding and writing assistants (Claude models from Anthropic, run as coding agents and chat sessions). We state what they did, what they did not do, and what the team is responsible for.

## What AI agents did

**Table 0.1.** Tasks performed with AI assistance, and the check the team is asked to record for each.

| Area | What the AI agents did | Check recorded by the team |
|---|---|---|
| Software | Wrote and edited most of the Python code of the tool (rules engine, risk matrix, register, exports, local web interface, PySide6 desktop wrapper, optional decision layer in `app/analysis.py`) and the automated tests. | [Team member, date: code read and tests run] |
| Literature search and notes | Ran keyword searches against open metadata sources, screened the resulting records by title and abstract, and wrote the research notes in `Research_Notes/`. The screening judgements are model output and were not independently re-read in full by a human (see Chapter 3 and `docs/Literature_Database_Report.md`). | [Team member, date: sample of records checked] |
| Data transcription | Transcribed relative importance index (RII) values from published papers into `data/literature_seed.json`. A later audit by AI agents compared all 182 rows with the printed tables and found the values matched; it also found and corrected metadata errors. | [Team member, date: rows spot-checked against the PDFs] |
| Audits and reviews | Ran a research-methods audit, an engine audit and four simulated committee reviews (engineering/UX, domain expert, methods, external examiner). These produced the list of withdrawn claims and corrected wording in `docs/Audit_Corrections_2026-10-08.md` and `docs/Project_Handoff_Summary.md`. They are not a substitute for review by the supervisor or an external examiner. | [Guide, date: reviewed] |
| Statistics | Wrote the scripts that compute the cross-study agreement statistics and sensitivity analyses (`scripts/`, `analysis/`). | [Team member, date: results re-computed] |
| Drafting | Drafted the text of this report from the repository files, with each number traced to a file or script output. | [Team member, date: report read in full] |

## What AI did not do

The AI assistants did **not** supply any probability, delay duration, cost, productivity rate, survey response or site observation. All probabilities, delays and costs that appear in the tool are typed in by a user and carry a Source label. The numbers taken from the literature are RII values copied from the published papers. The AI-suggestion feature of the tool can propose risk names, mechanisms and identifiers of evidence records only, and the tool rejects numeric fields in its output (guard rules described in Chapter 5). The example case in this report was written by the team for illustration and is labelled ILLUSTRATIVE wherever it appears.

## What the team must verify

The team remains responsible for the content. Before submission the team should confirm, and record in Table 0.1, that: (1) the transcribed RII values and the factor-to-risk mapping have been checked by a human against the source papers; (2) the references exist and say what the report attributes to them, in particular the items listed as unverified in the reference assembly notes; (3) the statistics have been re-run by a team member; (4) the wording in the report about what was and was not done matches the real project history; and (5) the declaration above is accurate for each team member.

\newpage

# Acknowledgements

[To be written by the team. Suggested content: the project guide and any co-guide; the Head of Department; the faculty and practitioners who will be asked to rate risks in the expert-survey phase, if that phase goes ahead; family and friends. Do not name anyone who has not agreed to be named.]

\newpage

# Abstract

Delays in brick and block masonry recur in Indian building projects, and published delay-cause studies rank factors by relative importance index (RII) without carrying the ranking into a site-level risk register. This report describes an offline decision-support tool for delay risk in one activity, brick or blockwork masonry. The registered title promised labour-productivity and delay prediction from managerial factors in selected Indian projects. Because no site access was available, the scope was reduced to risk identification, a source-labelled risk register and a five-by-five probability-impact matrix, and the report states this change openly.

The tool holds 46 masonry delay risks, 22 rules that flag risks from site facts, and a register in which every number carries a Source label (Literature, Historical Data, User Input, Expert Judgment, Derived Calculation or Assumption). For 30 of the 46 risks an ordinal starting position is derived from 182 RII values transcribed from 11 published surveys; five studies form the seed and six are held out. An RII measures importance, not probability or days, so this starting position is an assumption of the tool and is labelled as one. An optional Monte Carlo and expected-monetary-value layer uses only numbers the user enters.

Agreement between the published rankings is weak. Cross-prediction between seed studies gave Spearman correlations of 0.09 to 0.64, none significant, and agreement with three held-out surveys (0.28, 0.63 and -0.18) did not survive correction for multiple testing. No site data were collected and no expert survey was run, so the tool is verified as software but not validated on real projects, and the example case is illustrative. Site validation and expert elicitation are defined as future work.

# Keywords

brick masonry; construction delay; risk register; probability-impact matrix; relative importance index; decision support; India

\newpage

# List of abbreviations

**Table 0.2.** Abbreviations used in this report.

| Abbreviation | Meaning |
|---|---|
| AAC | Autoclaved aerated concrete (block) |
| AI | Artificial intelligence |
| APA | American Psychological Association (citation style, 7th edition) |
| BIS | Bureau of Indian Standards |
| CPWD | Central Public Works Department (India) |
| CSV | Comma-separated values (file format) |
| DSS | Decision-support system |
| EMV | Expected monetary value |
| FYP | Final year project |
| GUI | Graphical user interface |
| IEC | International Electrotechnical Commission |
| ISO | International Organization for Standardization |
| LLM | Large language model |
| LOSO | Leave-one-study-out |
| MC | Monte Carlo (simulation) |
| NICMAR | The institution at which the project was carried out (see title page) |
| P-I | Probability-impact (as in P-I matrix) |
| PERT | Programme evaluation and review technique (three-point estimate) |
| RII | Relative importance index |
| SE | Standard error |
| WBS | Work breakdown structure |
| Seed | The default ordinal starting position of a library risk derived from RII values of the seed studies |
| Held-out study | A published survey whose RII values are not used to build the seed and are used only for comparison |
| ILLUSTRATIVE | Label for example numbers that are not evidence |
