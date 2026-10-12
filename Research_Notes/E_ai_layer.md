# Topic Group E - AI layer: literature notes (SAVE 3 - verified items only; 57 IDs E01-E57)

Project: AI-assisted, literature-grounded Monte Carlo + risk-matrix + EMV decision-support system, one activity (brick masonry, India). AI role limited to retrieval, risk-identification assistance, evidence-cited explanation and mitigation-option drafting. All numbers and decisions come from a deterministic engine.

Compiled: 2026-09-26. Status: interim file written after a rate-limit interruption; will be re-written as more items are verified.

## 0. Integrity conventions used in this file

- NR = number/detail not reported in the text I could see. NC = not checked/not collected.
- "Evidence level" says what I actually saw:
  - FULL-TEXT = I extracted and read the text (PDF saved by the fetch tool, or publisher HTML page returned by the fetch tool).
  - PAGE-SUMMARY = publisher/repository page fetched through the fetch tool, which returns a model-summarised page; numbers quoted from it are as returned, not re-checked against a PDF.
  - ABSTRACT = abstract only (Crossref, PubMed, Semantic Scholar or repository abstract).
  - SNIPPET = only a search-engine result summary; treated as weak, flagged.
- DOI "verified" = the DOI resolved in the Crossref REST API (api.crossref.org/works/DOI) and title/authors/venue matched. NIST/EU documents are labelled STANDARD/GUIDANCE, not empirical research.
- "OA (CC BY ...)" is written only where a licence was visible: Crossref licence field, the arXiv/PMC/publisher page returned by the fetch tool. "Elsevier TDM licence" or "ACM copyright" in Crossref is NOT an open-access licence, so those are marked "OA not verified".
- Papers outside construction are labelled GENERAL (non-construction). Medical statistics papers are used only for their general statistical findings about sample size, and this is stated.

## 1. Search strings used and counts

WebSearch tool, 39 successful calls by me (a 40th was refused because the shared 200-call session budget ran out; WebFetch then also hit a session limit, so the rest of the work used public metadata APIs via PowerShell: Crossref, OpenAlex, PubMed E-utilities, Semantic Scholar batch API). Result counts per WebSearch are the tool's ~9-10 links each (not full hit counts); OpenAlex/Crossref gave true hit counts where shown.

WebSearch strings (abbreviated, in order run):
1. large language models construction risk management retrieval-augmented generation evaluation hallucination
2. systematic review artificial intelligence construction project risk management 2023
3. systematic review construction delay prediction machine learning
4. Uhm Kim Ahn Jeong Kim "RAG-GPT" construction safety information abstract ...
5. ChatGPT limitations risk identification mitigation strategies construction project risk assessment JCEM 2025
6. LLM construction schedule delay analysis generative AI GPT-4 claims delay analysis evaluation
7. large language model construction risk identification GPT-4 case study project risks generation evaluation experts
8. retrieval-augmented generation building code regulations construction question answering LLM evaluation faithfulness
9. explainable machine learning SHAP construction project delay prediction
10. explainable artificial intelligence XAI construction industry systematic review
11. sample size small dataset machine learning construction projects overfitting ... linear regression outperforms
12. small sample size machine learning prediction models "modern modelling techniques are data hungry" simulation study
13. sample size for developing clinical prediction model overfitting events per variable Riley Statistics in Medicine
14. construction management machine learning small data limitations dataset size review construction project data scarcity
15. Seven failure points when engineering a retrieval augmented generation system Barnett
16. Enabling Large Language Models to Generate Text with Citations ALCE Gao EMNLP 2023 ...
17. hallucination rates reference accuracy ChatGPT GPT-4 Bard systematic reviews fabricated references JMIR Chelli
18. PAL program-aided language models ... OR Toolformer ...
19. rule-based expert system construction project risk assessment knowledge acquisition experts validation case study journal
20. hybrid fuzzy rule-based system Monte Carlo simulation construction schedule delay risk decision support
21. ontology SWRL rules construction risk knowledge-based decision support system explainable reasoning
22. large language model agent construction scheduling simulation tool calling deterministic calculation neuro-symbolic construction
23. systematic literature review machine learning construction delay prediction PRISMA papers reviewed research gaps
24. review artificial intelligence construction risk management "papers" reviewed 2020 2024 knowledge-based systems fuzzy Bayesian ...
25. review of large language models in construction industry systematic review applications limitations 2024 2025
26. expert system construction delay risk knowledge-based system rule elicitation validation conflict resolution
27. "expert system" construction delay causes mitigation "rule base" developed interviews validated experts ...
28. machine learning versus simple baseline construction cost estimation small sample regression comparable ANN ...
29. "no performance benefit of machine learning over logistic regression" systematic review Christodoulou
30. LLM contract risk identification retrieval-augmented generation construction contracts accuracy 76.7%
31. review "construction delay" artificial intelligence machine learning literature review ... reviewed articles
32. bibliometric systematic review artificial intelligence construction schedule delay risk prediction Scopus PRISMA 2025
33. Rudin "Stop explaining black box machine learning models ..." Nature Machine Intelligence
34. Bansal "Does the Whole Exceed its Parts" ... CHI 2021 overreliance
35. Poursabzi-Sangdeh "Manipulating and Measuring Model Interpretability" CHI 2021 ...
36. Lundberg Lee "A Unified Approach to Interpreting Model Predictions" NeurIPS 2017 SHAP
37. "Artificial intelligence in construction risk management: a decade of developments ..." abstract 87 studies
38. "Artificial Intelligence (AI) in Construction Management (CM): A Systematic Review of Models and Methods" Buildings 2026
39. Erfani Khanjar "Large Language Models for Construction Risk Classification ..." twelve classification pipelines ...

Later API-only queries (after the WebSearch/WebFetch limits): 3 arXiv API title lookups (chunking, LLM non-determinism, Toolformer), 9 Crossref bibliographic searches (e.g. "explainable machine learning SHAP construction project delay prediction", "Investigating the Use of ChatGPT for the Scheduling of Construction Projects", "Is semantic chunking worth the computational cost", "Model Cards for Model Reporting"), 2 further Semantic Scholar batch calls, and PMC E-utilities full-text retrieval for four open-access papers (PMC11153973, PMC4289553, PMC6837442, PMC6950629). OpenAlex began returning HTTP 429 after ~12 calls, so it was not used further.

Metadata API queries (PowerShell): about 75 Crossref DOI look-ups (all DOIs below), 8 OpenAlex boolean title/abstract searches (e.g. `"expert system" AND construction AND (delay OR risk)` from 2015: 155 hits; `"knowledge-based" AND construction AND ("risk management" OR delay OR "cost overrun") AND (rules OR "case-based reasoning")` from 2018: 19 hits; `("large language model" OR LLM OR ChatGPT) AND construction AND (delay OR "risk response" OR "risk mitigation" OR "risk assessment")` from 2023: 264 hits; `"Monte Carlo" AND construction AND (expert system OR rule-based OR fuzzy) AND (schedule OR delay) AND hybrid` from 2018: 12 hits), 3 PubMed E-utilities abstract fetches, 1 Semantic Scholar batch call (13 DOIs).

## 2. Summary table of verified entries

| ID | Paper (short) | Topic | Domain | Evidence level | Access |
|---|---|---|---|---|---|
| E01 | Nyqvist 2024 ECAM | LLM risk mgmt vs experts | construction | PAGE-SUMMARY + ABSTRACT | OA CC BY 4.0 (publisher page) |
| E02 | Aladag 2023 Sustainability | LLM accuracy risk mgmt | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E03 | Oral 2026 ECAM | LLM vs experts, safety risk | construction | ABSTRACT | OA not verified |
| E04 | Martin/James/Chadee 2025 JCEM | ChatGPT risk assessment | construction | SNIPPET | OA not verified |
| E05 | Erfani & Khanjar 2025 Buildings | LLM risk classification | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E06 | Sammour 2026 JCEM (arXiv 2411.08320) | LLM safety exam, errors | construction | FULL-TEXT (arXiv version) | journal OA not verified |
| E07 | Uhm 2025 AutCon | RAG-GPT safety info | construction | SNIPPET | closed |
| E08 | Saparamadu 2025 Buildings | vector-DB chatbot, contracts | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E09 | Saka 2024 DBE | GPT in construction | construction | FULL-TEXT (arXiv) | OA CC BY 4.0 (Crossref+arXiv) |
| E10 | Ghimire 2024 Buildings | GenAI opportunities | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E11 | Aqib 2025 arXiv | RAG retrievers, building code | construction | FULL-TEXT (preprint) | preprint, peer review NC |
| E12 | Lewis 2020 NeurIPS | RAG foundational | GENERAL | FULL-TEXT (arXiv) | arXiv |
| E13 | Es 2024 EACL (RAGAs) | RAG faithfulness eval | GENERAL | FULL-TEXT (arXiv) | arXiv CC BY 4.0 |
| E14 | Gao 2023 EMNLP (ALCE) | citation eval | GENERAL | FULL-TEXT (arXiv) | ACL Anthology (licence NC) |
| E15 | Barnett 2024 CAIN | RAG failure points | GENERAL | FULL-TEXT (arXiv) | ACM (OA NC) |
| E16 | Liu 2024 TACL | lost in the middle | GENERAL | FULL-TEXT (partial) | OA CC BY 4.0 (Crossref) |
| E17 | Chelli 2024 JMIR | fabricated references | GENERAL (medical) | FULL-TEXT (PMC XML) | OA CC BY 4.0 (PMC page) |
| E18 | Love 2023 AEI | XAI in construction | construction | FULL-TEXT (arXiv) | arXiv CC BY 4.0; journal NC |
| E19 | Naghdi 2026 AutCon | XAI review, 55 papers | construction | ABSTRACT | OA not verified |
| E20 | Rudin 2019 NMI | interpretable vs explained | GENERAL | FULL-TEXT (arXiv) | arXiv; journal OA NC |
| E21 | Bansal 2021 CHI | explanations and over-reliance | GENERAL | FULL-TEXT (partial) | ACM (OA NC) |
| E22 | Poursabzi-Sangdeh 2021 CHI | interpretability user study | GENERAL | FULL-TEXT (partial) | arXiv v4 |
| E23 | Zhang 2016 JCEM (B-RIES) | rule+case expert system | construction | ABSTRACT | OA not verified |
| E24 | Islam 2019 ESWA | knowledge-based ES cost overrun | construction | ABSTRACT (S2) | OA not verified |
| E25 | Amiri 2017 Safety Sci | fuzzy probabilistic ES | construction | SNIPPET | closed |
| E26 | Zhasmukhambetova 2025 Future Transp | risk+scheduling hybrids review | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E27 | Gao 2023 PAL (ICML) | LLM offloads computation | GENERAL | FULL-TEXT (partial) | arXiv/PMLR |
| E28 | NIST AI RMF 1.0 (2023) | trustworthy AI guidance | STANDARD/GUIDANCE | FULL-TEXT (partial) | NIST report |
| E29 | NIST AI 600-1 (2024) | GenAI profile | STANDARD/GUIDANCE | FULL-TEXT (partial) | NIST report |
| E30 | EU HLEG 2019 | Ethics Guidelines | STANDARD/GUIDANCE | PAGE-SUMMARY | EC page |
| E31-E41 | reviews | see section 5 | construction | mostly ABSTRACT | see table |
| E42 | van der Ploeg 2014 BMC MRM | data hungry | GENERAL (medical stats) | FULL-TEXT (PMC XML) | OA CC BY 4.0 (PMC page) |
| E43 | Vabalas 2019 PLOS ONE | small-sample validation | GENERAL | FULL-TEXT (PMC XML) | OA CC BY 4.0 |
| E44 | Riley 2019 Stat Med Part II | minimum sample size | GENERAL (medical stats) | ABSTRACT (PubMed) | PMC6519266; CC BY-NC 4.0 (Crossref) |
| E45 | Christodoulou 2019 JCE | ML vs logistic regression | GENERAL (medical) | ABSTRACT (PubMed) | OA not verified |
| E46 | Davila Delgado 2021 ASOC | small data construction | construction | ABSTRACT (S2) | green repository copy; version/licence per OpenAlex only |
| E47 | Zhang & Li 2024 JAABE | ML vs baseline, duration | construction | ABSTRACT (S2) | OA CC BY 4.0 (Crossref) |
| E48 | Naser 2026 J Big Data | ML with small data survey | GENERAL | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E49 | Prieto 2023 Buildings | ChatGPT-generated schedule | construction | ABSTRACT | OA CC BY 4.0 (Crossref) |
| E50 | Taiwo 2025 AEJ | GenAI Delphi + RAG case study | construction | ABSTRACT (S2) | CC BY 4.0 listed in Crossref licence field |
| E51 | Qu 2025 Findings NAACL | chunking strategies | GENERAL | ABSTRACT (arXiv) | ACL Anthology (licence NC) |
| E52 | Schick 2023 Toolformer (NeurIPS) | LLM tool use | GENERAL | ABSTRACT (arXiv) | arXiv |
| E53 | Atil 2024 arXiv | LLM non-determinism | GENERAL | ABSTRACT (arXiv), PREPRINT | arXiv |
| E54 | Mitchell 2019 FAT* | Model Cards (documentation) | GENERAL | ABSTRACT (S2) | arXiv copy; ACM copyright |
| E55 | Chen 2025 JAABE | ontology + rule-library risk KB | construction | ABSTRACT (S2) | CC BY-NC 4.0 (Crossref) |
| E56 | Kaska & Kiral 2026 Research Square | explainable ML, limited data | construction | ABSTRACT, PREPRINT | CC BY 4.0 (Crossref) |
| E57 | Namazian 2019 IJERPH | Monte Carlo + Bayesian network | construction | ABSTRACT (PMC) | OA CC BY (PMC licence text) |

## 3. Detailed entries

### A. LLMs / generative AI / RAG in construction

**E01 - Nyqvist R., Peltokorpi A., Seppanen O. (2024). Can ChatGPT exceed humans in construction project risk management? Engineering, Construction and Architectural Management 31(13): 223-243.**
- DOI 10.1108/ECAM-08-2023-0819 (Crossref verified; published 2024-12-16).
- Access: publisher page returned "CC BY 4.0, open access" via the fetch tool (Crossref licence field only shows Emerald site policy). Evidence: ABSTRACT (Crossref, verbatim) + PAGE-SUMMARY for numbers.
- Built/tested: mixed-methods comparison of ChatGPT (GPT-4) with 16 Finnish risk-management experts on a construction project risk management test (simulated health-centre renovation case in Helsinki); anonymous blind peer review; questions on risk identification, analysis and control.
- Numbers (as returned by the page summary): 16 human respondents; 19 human reviewers; 1 ChatGPT response; scores 1-10. Overall human mean 5.7 +/- 1.9 vs ChatGPT 8.6 +/- 1.2. Risk identification 6.1 vs 8.2; risk analysis 5.3 vs 8.4; risk control 5.8 vs 8.6. ChatGPT self-review of humans 7.6 +/- 1.0 and of itself 9.0 +/- 0.5. Themes: ChatGPT more comprehensive; humans more specific/practical; feasibility of ChatGPT strategies a concern (abstract: strategies "lack practicality and specificity").
- Limitations: only one ChatGPT response (n = 1), one simulated case, GPT-4 version of 2023; reviewers rated plausibility/comprehensiveness, not ground-truth correctness.
- Design decision supported: LLM is useful as a drafting assistant for comprehensive risk/response lists, but drafts need human review for specificity and feasibility; a high fluency/comprehensiveness score is not evidence of correctness, so LLM output must be tagged "unverified draft".

**E02 - Aladag H. (2023). Assessing the Accuracy of ChatGPT Use for Risk Management in Construction Projects. Sustainability 15(22): 16071.**
- DOI 10.3390/su152216071 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence field). Evidence: ABSTRACT only (Crossref); full text not seen (MDPI blocked).
- Built/tested: KPIs defined per risk-management sub-process; questionnaire of prompt templates put to ChatGPT for different project types; responses rated by experts in focus groups.
- Findings (abstract): "moderate level of performance"; more accurate in risk response and risk monitoring than in risk identification and risk analysis. Numeric scores NR (abstract only).
- Limitations: not stated in abstract (NR).
- Design decision: ChatGPT-type models are comparatively better at risk-response drafting than at analysis, which fits restricting the LLM to identification assistance and mitigation-option drafting; quantitative analysis stays in the engine.

**E03 - Oral M., Alboga O., Aydinli S., Erdis E. (2026). Usability of large language models for building construction safety risk assessment. ECAM 33(9): 7021-7048.**
- DOI 10.1108/ecam-08-2024-1143 (Crossref verified; published 2026-07-14). Access: no licence in Crossref; OA not verified. Evidence: ABSTRACT (Crossref).
- Built/tested: risks and precautions defined for 12 work items in building construction; ten experts and ChatGPT rated risk importance on a five-point Likert scale; similarity computed with Modified Manhattan Distance; precaution selections compared.
- Findings (abstract): LLM answers similar to experts in risk scores and precaution selection; ChatGPT similarity value "surpasses" the similarity among experts. Numeric values NR.
- Limitations: NR (abstract only); ten experts.
- Design decision: supports LLM as a decision-support second opinion on hazard lists, not as a source of final scores.

**E04 - Martin H., James J., Chadee A. (2025). Exploring Large Language Model AI tools in Construction Project Risk Assessment: Chat GPT Limitations in Risk Identification, Mitigation Strategies, and User Experience. J. Constr. Eng. Manage. 151(9): 04025119.**
- DOI 10.1061/JCEMD4.COENG-16658 (Crossref verified; authors listed by Crossref as Hector Martin, Jennifer James, Aaron Chadee). Access: OA not verified. Evidence: SNIPPET ONLY (search-result summary; abstract not retrieved).
- Built/tested (per snippet): mixed-method comparing ChatGPT-assisted and human evaluations, interviews and a case study; discusses errors of omission, over/underestimation of probabilities and impacts, and treatment of residual risk after mitigation.
- Numbers NR. Limitations NR.
- Design decision (tentative, snippet only): LLM probability/impact estimates should not be used as inputs; the engine should take probabilities/impacts from elicited or literature-sourced distributions.

**E05 - Erfani A., Khanjar H. (2025). Large Language Models for Construction Risk Classification: A Comparative Study. Buildings 15(18): 3379.**
- DOI 10.3390/buildings15183379 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence field). Evidence: ABSTRACT (repository abstract page via fetch tool).
- Built/tested: benchmark of twelve model configurations for classifying construction risk items into generic risk categories: classical NLP (TF-IDF, Word2Vec), BERT, GPT-4 with zero-shot, instruction and few-shot prompts.
- Numbers (abstract): "GPT-4 with few-shot prompts achieve a competitive performance (F1 = 0.81) approaching that of the best classical model (BERT + SVM; F1 = 0.86), all without the need for training data." Dataset size, per-pipeline scores NR (full text not seen).
- Limitations: NR.
- Design decision: an LLM can tag/classify risk statements with reasonable agreement without training data, useful where labelled data is scarce; a supervised BERT+SVM style baseline should be the comparison reference.

**E06 - Sammour F., Xu J., Wang X., Hu M., Zhang Z. (2026). Responsible AI in Construction Safety: Systematic Evaluation of Large Language Models and Prompt Engineering. J. Constr. Eng. Manage. 152(1): 04025217.**
- DOI 10.1061/JCEMD4.COENG-16639 (Crossref verified). Text read from the arXiv preprint (arXiv:2411.08320, 29 pages), which may differ from the journal version. Access: journal OA not verified; arXiv licence NC.
- Built/tested: GPT-3.5 and GPT-4o on three Board of Certified Safety Professionals (BCSP) exams, 385 questions over seven knowledge areas; accuracy, reliability (repeated measures ANOVA) and consistency (entropy, 0-2.32 bits); prompt strategies (zero-shot, few-shot, chain-of-thought etc.).
- Numbers: GPT-4o 84.6% and GPT-3.5 73.8% (both above ~60% pass threshold); prompt-strategy accuracy variation up to 13.5% (GPT-3.5) and 7.9% (GPT-4o), "no single prompt configuration proves universally effective". Error analysis of 42 lowest-performing outputs: lack of knowledge 38%, reasoning flaws 31%, memory issues 24%, calculation errors 7%. Reliability: no significant difference across repetitions (p = 0.957). Highest average entropy 0.31 bits (13.2%) in the 21-30% accuracy bin; 201/385 questions (52.2%) in the 91-100% accuracy range had entropy 1.1%. Observed hallucination example: invented non-existent OSHA standards.
- Authors' statements: even with temperature, seed and context window controlled, identical queries sometimes gave different responses, "hindering efforts to fully trust the model"; LLMs make arithmetic errors after setting up problems correctly (e.g. powers) and authors advise caution for any calculation and suggest function calling to specialised mathematical tools; suggest instructing the model to decline out-of-scope questions; note RAG limitations ("tug-of-war" between retrieved and parametric knowledge; "lost in the middle").
- Limitations: multiple-choice exam questions rather than project decisions; two OpenAI models; the remaining limitations section not fully read (NC).
- Design decisions supported: (1) numerical calculation must not be delegated to the LLM; (2) LLM outputs cannot be assumed reproducible, so store the generated text verbatim in the audit log rather than regenerate it; (3) include a "decline if not in evidence" instruction plus a retrieval guardrail; (4) LLM output tagged unverified.

**E07 - Uhm M., Kim J., Ahn S., Jeong H., Kim H. (2025). Effectiveness of retrieval augmented generation-based large language models for generating construction safety information. Automation in Construction 170: 105926.**
- DOI 10.1016/j.autcon.2024.105926 (Crossref verified; a 2024 SSRN preprint version also exists, DOI 10.2139/ssrn.4819837). Access: Elsevier TDM licence only; closed (OpenAlex/Semantic Scholar say closed). Evidence: SNIPPET ONLY (ScienceDirect and SSRN pages returned 403; summary came from a search result).
- Built/tested (per snippet): RAG-GPT compared with four other GPT models; responses judged by 2 researchers, 10 construction safety experts and 30 construction workers.
- Findings (snippet): RAG-GPT superior quantitatively; experts rated its answers more contextually relevant with high marks for accuracy and inclusion of essential information; motivating problems named as "inaccurate numerical responses, a lack of detailed information, and hallucination problems". Numeric scores NR.
- Design decision: RAG grounding improved expert-judged accuracy over non-RAG GPT in a construction-safety setting; motivation for retrieval from a curated corpus, but note the numeric-response weakness again supports engine-computed numbers. (Evidence weak: snippet.)

**E08 - Saparamadu P.V.I.N., Sepasgozar S.M.E., Guruge R.N.D., Jayasena H.S., Darejeh A., Ebrahimzadeh S.M., Eranga B.A.I. (2025). Optimising Contract Interpretations with Large Language Models: A Comparative Evaluation of a Vector Database-Powered Chatbot vs. ChatGPT. Buildings 15(7): 1144.**
- DOI 10.3390/buildings15071144 (Crossref verified). Access: OA, CC BY 4.0 (Crossref). Evidence: ABSTRACT.
- Built/tested: publicly available specialised chatbot built on ChatGPT with vector embeddings of a construction regulation/legal database (architecture design, data preparation, vector embeddings, model integration); standardised tests, qualitative + quantitative.
- Numbers (abstract): chatbot "average score of 88%", ChatGPT 36%. Number of test items, grader, and scoring rubric NR (full text not seen).
- Limitations: NR; domain is contract law, not risk analysis.
- Design decision: retrieval over a domain corpus substantially raised test scores over the unaugmented model in a construction-related task; supports RAG over a curated brick-masonry corpus.

**E09 - Saka A., Taiwo R., Saka N., Salami B.A., Ajayi S., Akande K., Kazemi H. (2024). GPT models in construction industry: Opportunities, limitations, and a use case validation. Developments in the Built Environment 17: 100300.**
- DOI 10.1016/j.dibe.2023.100300 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence list includes creativecommons.org/licenses/by/4.0; arXiv 2305.18997 also CC BY 4.0). Evidence: FULL-TEXT (arXiv version, 58 pages).
- Built/tested: critical literature review, expert discussion and a BIM + GPT prototype for material selection and optimisation (data-retrieval module, NLP prompt processing, UI, integration module); zero-shot and few-shot tests.
- Findings: opportunities across project lifecycle; challenges include hallucination, accepted input formats, cost, reliability, trust, acceptability, domain technicalities, skills, interoperability. Authors write that reliance on hallucinated scheduling text "could lead to project delay or cost overrun" and that experts flagged hallucination as a major barrier because wrong information could endanger lives and property.
- Metrics: none. Authors state the prototype "was also not subjected to any quantitative validation".
- Limitations (authors): search limited to English and named databases; small expert group; no quantitative validation of prototype.
- Design decision: hallucination is a recognised barrier in construction; LLM output must be tagged unverified and never feed scheduling numbers directly.

**E10 - Ghimire P., Kim K., Acharya M. (2024). Opportunities and Challenges of Generative AI in Construction Industry: Focusing on Adoption of Text-Based Models. Buildings 14(1): 220.**
- DOI 10.3390/buildings14010220 (Crossref verified; arXiv title "Generative AI in the Construction Industry: Opportunities & Challenges", arXiv 2310.04427). Access: OA, CC BY 4.0 (Crossref). Evidence: ABSTRACT (arXiv page via fetch tool).
- Built: literature analysis, industry perception via word-frequency analysis, expert perspectives; conceptual GenAI implementation framework and recommendations. Numbers NR (abstract only).
- Limitations NR.
- Design decision: background support that construction GenAI adoption lags and needs a governed implementation framework; low weight (no evaluation metrics).

**E11 - Aqib M., Hamza M., Mei Q., Chui Y.H. (2025). Fine-Tuning Large Language Models and Evaluating Retrieval Methods for Improved Question Answering on Building Codes. arXiv:2505.04666 (PREPRINT; journal publication NC).**
- No DOI verified for a journal version. Access: arXiv non-exclusive licence (not open licence). Evidence: FULL-TEXT (38 pages).
- Built/tested: RAG QA over the National Building Code of Canada; retrievers compared (TF-IDF, BM25, Elasticsearch, S-BERT cosine, DPR variants); pre-trained vs fine-tuned LLMs. 991 context-question-answer pairs used for fine-tuning.
- Numbers seen: BERT-F1 for Elasticsearch 0.845, 0.849, 0.847, 0.844 at top-1/3/5/10; top-1 BERT precision ES 0.884, TF-IDF 0.882, BM25 0.874; authors state Elasticsearch was the most robust retriever and that lexical methods (ES, BM25, TF-IDF) and S-BERT-Cos performed closely. After fine-tuning, absolute generation scores stayed "relatively low": Llama-2-7b F1 0.271 pre-trained to 0.387 fine-tuned, fine-tuned BLEU 0.228 and ROUGE-1 0.411 (authors' own wording: "relatively low absolute scores").
- Limitations: metrics are similarity metrics (BERTScore/BLEU/ROUGE) rather than faithfulness/citation accuracy; preprint.
- Design decision: for a small technical corpus, a lexical/BM25-type retriever (possibly hybrid with embeddings) is a defensible, explainable baseline; retrieval choice should be evaluated on own questions.

### B. RAG design, citation grounding, faithfulness (GENERAL, non-construction)

**E12 - Lewis P., Perez E., Piktus A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020 (arXiv:2005.11401).**
- No publisher DOI (NeurIPS proceedings); arXiv identifier only (arXiv-issued DOI NC). Evidence: FULL-TEXT (arXiv PDF, 19 pages). GENERAL.
- Built: RAG models combining a parametric seq2seq generator with a non-parametric dense retrieval memory (Wikipedia index).
- Content seen: abstract states that "providing provenance for their decisions and updating their world knowledge remain open research problems" for pre-trained models; the paper shows the retrieval index can be "hot-swapped" to update knowledge without retraining; authors write "Qualitatively, we find that RAG models hallucinate less and generate factually correct text more often than BART" (a qualitative statement; quantitative task results NR here).
- Limitations: Wikipedia corpus, general QA tasks.
- Design decision: foundational justification for a replaceable, version-controlled evidence index (updating the corpus updates the AI layer) and for provenance via retrieved passages.

**E13 - Es S., James J., Espinosa Anke L., Schockaert S. (2024). RAGAs: Automated Evaluation of Retrieval Augmented Generation. Proc. 18th EACL: System Demonstrations, pp. 150-158.**
- DOI 10.18653/v1/2024.eacl-demo.16 (Crossref verified). Access: arXiv 2309.15217 shows CC BY 4.0 (arXiv page); ACL Anthology licence NC. Evidence: FULL-TEXT (arXiv 8-page version). GENERAL.
- Built: reference-free RAG evaluation with three metrics: faithfulness F = |V|/|S| (fraction of statements extracted from the answer that an LLM judges as inferable from the retrieved context), answer relevance (mean cosine similarity between the question and questions regenerated from the answer), context relevance (extracted crucial sentences / total sentences). Judge model gpt-3.5-turbo-16k.
- Dataset/metrics: WikiEval, 50 Wikipedia pages on events since 2022; two annotators, agreement ~95% (faithfulness, context relevance) and ~90% (answer relevance). Accuracy of pairwise agreement with humans (faithfulness / answer relevance / context relevance): RAGAs 0.95 / 0.78 / 0.70; GPT Score 0.72 / 0.52 / 0.63; GPT Ranking 0.54 / 0.40 / 0.52. Authors: context relevance hardest; ChatGPT struggles selecting crucial sentences from longer contexts.
- Limitations: small dataset (50), Wikipedia general knowledge, LLM-as-judge (judge could be wrong on engineering text); not validated in engineering.
- Design decision: claim-level faithfulness checking (decompose the answer into statements and verify each against retrieved chunks) is a practical automatic guardrail/regression test, but must be re-validated against expert-labelled masonry examples.

**E14 - Gao T., Yen H., Yu J., Chen D. (2023). Enabling Large Language Models to Generate Text with Citations. Proc. EMNLP 2023, pp. 6465-6488.**
- DOI 10.18653/v1/2023.emnlp-main.398 (Crossref verified). Access: ACL Anthology; licence not checked. Evidence: FULL-TEXT (arXiv 2305.14627). GENERAL.
- Built: ALCE benchmark (ASQA, QAMPARI, ELI5) with automatic metrics for fluency, correctness and citation quality (citation recall, citation precision via NLI).
- Numbers: abstract: on ELI5 "even the best models lack complete citation support 50% of the time". Agreement with humans: Cohen's kappa 0.698 (citation recall) and 0.525 (citation precision); accuracy against human labels 85.1% (recall) and 77.6% (precision).
- Limitations (authors): MAUVE unstable/sensitive to output length; ELI5 automatically generated claims may not cover all possible answers; citation quality limited by the NLI model, which cannot detect "partially support" and so gives lower citation precision than human evaluation; datasets do not cover multi-hop reasoning, math reasoning or code completion.
- Design decision: even retrieval-grounded LLMs cite incompletely or wrongly, so citations must be machine-checked (does the cited chunk exist and support the claim) and displayed with the evidence text; measure citation recall/precision on a test set.

**E15 - Barnett S., Kurniawan S., Thudumu S., Brannelly Z., Abdelrazek M. (2024). Seven Failure Points When Engineering a Retrieval Augmented Generation System. Proc. IEEE/ACM 3rd Int. Conf. on AI Engineering - Software Engineering for AI (CAIN 2024), pp. 194-199.**
- DOI 10.1145/3644815.3644945 (Crossref verified). Access: ACM copyright policy in Crossref; OA not verified. Evidence: FULL-TEXT (arXiv version, 6 pages). GENERAL.
- Built: experience report from three RAG case studies (Cognitive Reviewer, AI Tutor, BioASQ with 4017 open-access documents and 1000 questions).
- Content: seven failure points: FP1 missing content, FP2 missed top-ranked documents, FP3 not in context (consolidation), FP4 not extracted, FP5 wrong format, FP6 incorrect specificity, FP7 incomplete. Lessons include: RAG systems need continuous calibration (chunk size, retrieval strategy); adding metadata (file name, chunk number) improves retrieval; testing only possible at runtime. Automated evaluation (OpenAI Evals) was more pessimistic than a human rater on BioASQ; authors note the human raters were not domain experts.
- Limitations: experience report, qualitative; numbers of failures per point NR.
- Design decision: implement an explicit "not in corpus" refusal path for FP1, keep chunk IDs/metadata, log retrieval results; test with domain-relevant questions.

**E16 - Liu N.F., Lin K., Hewitt J., Paranjape A., Bevilacqua M., Petroni F., Liang P. (2024). Lost in the Middle: How Language Models Use Long Contexts. Trans. ACL 12: 157-173.**
- DOI 10.1162/tacl_a_00638 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence field). Evidence: FULL-TEXT (arXiv 2307.03172, abstract and figure captions read; per-model accuracies NR). GENERAL.
- Finding (abstract): performance is often highest when relevant information is at the beginning or end of the input context and "significantly degrades" when it is in the middle, even for explicitly long-context models (multi-document QA and key-value retrieval).
- Design decision: pass a small number of highest-ranked chunks, ordered by relevance, rather than stuffing the context.

**E17 - Chelli M., Descamps J., Lavoue V., et al. (2024). Hallucination Rates and Reference Accuracy of ChatGPT and Bard for Systematic Reviews: Comparative Analysis. J. Med. Internet Res. 26: e53164.**
- DOI 10.2196/53164 (Crossref verified). Access: OA, CC BY 4.0 (PMC page as returned by fetch tool; PMC11153973). Evidence: FULL-TEXT (PMC XML text retrieved; the precision/recall sentence, 471 references and 33 prompts confirmed verbatim). GENERAL (medical).
- Built/tested: GPT-3.5, GPT-4 and Bard prompted to produce references for 11 systematic reviews (shoulder rotator-cuff and three other fields), 471 references analysed against the reviews' own reference lists.
- Numbers: hallucination rate 39.6% (55/139) GPT-3.5, 28.6% (34/119) GPT-4, 91.4% (95/104) Bard; precision 9.4% (13/139), 13.4% (16/119), 0% (0/104); recall 11.9% (13/109) GPT-3.5, 13.7% (15/109) GPT-4, Bard none. Hallucination definition: a paper is hallucinated if any 2 of title, first author, year are wrong.
- Limitations (authors): single medical topic, three models, no prompt-optimisation guidelines.
- Design decision: the LLM must not produce bibliographic citations from its memory; every citation in the output must resolve to a record in the project's own verified corpus (ID lookup), with a verifier that rejects unknown IDs.

### C. Explainable AI, interpretable models and trust

**E18 - Love P.E.D., Fang W., Matthews J., Porter S., Luo H., Ding L. (2023). Explainable artificial intelligence (XAI): Precepts, models, and opportunities for research in construction. Advanced Engineering Informatics 57: 102024.**
- DOI 10.1016/j.aei.2023.102024 (Crossref verified; journal licence in Crossref is Elsevier TDM). arXiv:2211.06579 page states CC BY 4.0 (arXiv version only; journal-version OA NC). Evidence: FULL-TEXT (arXiv, 58 pages, only abstract-level content extracted so far).
- Built: narrative review of XAI relevance to construction; a framework categorising XAI literature; future directions on stakeholder needs and data fusion; aims to "help alleviate the scepticism and hesitancy toward AI adoption".
- Numbers: number of papers reviewed NR. Text also notes that "how trust is incorporated into the vast array of existing ML models is ambiguous" and cites the position that trust can be subjective (a person may accept an explanation without it being warranted).
- Limitations: narrative not systematic.
- Design decision: explanations should be designed for the stakeholder (site engineer, project manager), supporting a plain-language evidence-linked explanation layer.

**E19 - Naghdi M., Mahmoudi N., Erfani A., Ilbeigi M. (2026). Explainable artificial intelligence in construction engineering and management: Review of applications, trends, and opportunities. Automation in Construction 190: 107112.**
- DOI 10.1016/j.autcon.2026.107112 (Crossref verified). Access: repository page shows no licence; Elsevier TDM; OA not verified. Evidence: ABSTRACT (repository page).
- Review: PRISMA-guided; 55 peer-reviewed journal articles; growing use of SHAP for tree-based and ensemble models; persistent challenges "small and imbalanced datasets, weak validation across contexts, limited human evaluation", and insufficient integration with BIM and digital twins.
- Design decision: XAI in construction is mostly post-hoc SHAP on ensembles trained on small data with little human evaluation; supports choosing inherently transparent components instead of black-box ML plus post-hoc explanation.

**E20 - Rudin C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nature Machine Intelligence 1(5): 206-215.**
- DOI 10.1038/s42256-019-0048-x (Crossref verified). Text read from arXiv:1811.10154 v3 (20 pages); journal OA not verified (Springer TDM licence). GENERAL.
- Content: argues that creating post-hoc explanations of black boxes "is likely to perpetuate bad practices"; "Explanations are often not reliable, and can be misleading"; recommends inherently interpretable models (sparsity, monotonicity, domain constraints) for high-stakes decisions.
- Limitations: position/argument paper; not construction.
- Design decision: use interpretable rule- and simulation-based components for decisions, so the explanation is the calculation itself.

**E21 - Bansal G., Wu T., Zhou J., Fok R., Nushi B., Kamar E., Ribeiro M.T., Weld D. (2021). Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance. CHI 2021.**
- DOI 10.1145/3411764.3445717 (Crossref verified). Access: author-hosted PDF read; publication rights licensed to ACM; OA not verified. Evidence: FULL-TEXT (first pages/abstract). GENERAL.
- Tested: mixed-method user studies on three datasets, AI with accuracy comparable to humans, explanations in some conditions.
- Finding (abstract): complementary improvements from AI augmentation were "not increased by explanations"; explanations "increased the chance that humans will accept the AI's recommendation, regardless of its correctness". Setup numbers seen: pilot unassisted human accuracy 87% (Beer review task) and 85% (Amzbook task); 50 selected examples set so AI accuracy was 84%, comparable to humans. Outcome tables (team accuracy per condition) not extracted (NR here).
- Design decision: an explanation can increase acceptance without improving decisions; the interface must separate engine-computed results from the LLM narrative and avoid persuasive framing, and any reliance should be tested (user study) rather than assumed.

**E22 - Poursabzi-Sangdeh F., Goldstein D.G., Hofman J.M., Wortman Vaughan J., Wallach H. (2021). Manipulating and Measuring Model Interpretability. CHI 2021.**
- DOI 10.1145/3411764.3445315 (Crossref verified). Text read from arXiv:1802.07810 v4 (67 pages). Access: ACM; OA not verified. GENERAL.
- Tested: pre-registered experiments (N = 3,800) varying number of features and model transparency (clear vs black box) for functionally identical models.
- Findings (abstract): participants shown a clear model with few features could better simulate its predictions but did not more closely follow its predictions; a clear model made them "less able to detect and correct for the model's sizable mistakes, seemingly due to information overload".
- Design decision: transparency alone does not guarantee better human error-detection; keep displayed explanation short (few key drivers) and test with users.

### D. Rule-based / knowledge-based systems and hybrids

(Koulinas 2020 and 2021 already collected; not repeated.)

**E23 - Zhang L., Wu X., Ding L., Skibniewski M.J., Lu Y. (2016). BIM-based risk identification system in tunnel construction. J. Civil Eng. and Management 22(4): 529-539.**
- DOI 10.3846/13923730.2015.1023348 (Crossref verified). Access: Crossref licence blank; OpenAlex flags gold OA; OA not verified. Evidence: ABSTRACT (Crossref).
- Built: BIM-based Risk Identification Expert System (B-RIES) with BIM extraction, knowledge-base management and risk-identification subsystems; knowledge base = fact base + rule base + case base; hybrid case-based and rule-based reasoning; IFC used to link BIM data to risk factors; case study on water-gushing hazard at one metro station in China.
- Metrics: NR (feasibility/effectiveness stated qualitatively).
- Limitations: single case study (per abstract).
- Design decision: separate fact base, rule base and case base with explicit provenance; hybrid rules + cases; the rule base should store source and expert-confirmation metadata.

**E24 - Islam M.S., Nepal M.P., Skitmore M., Kabir G. (2019). A knowledge-based expert system to assess power plant project cost overrun risks. Expert Systems with Applications 136: 12-32.**
- DOI 10.1016/j.eswa.2019.06.030 (Crossref verified). Access: QUT ePrints copy referenced by Semantic Scholar; licence not checked; OA not verified. Evidence: ABSTRACT (Semantic Scholar).
- Built: fuzzy canonical model (FCM) integrating fuzzy group decision-making and a Canonical model (modified Bayesian belief network); designed to cut the expert effort of eliciting conditional probabilities and reduce subjectivity/uncertainty in expert judgement; case study of a power plant project (construction and commissioning phase) identified critical risks (e.g. complexity of lifting and rigging heavy equipment, inadequate site/soil investigation, poor contractor planning and scheduling).
- Metrics: NR (abstract).
- Limitations: NR (single case study per abstract).
- Design decision: expert-elicitation burden is a known bottleneck in knowledge-based systems; keep elicitation to a small number of parameters per risk (e.g. three-point estimates) and record who supplied them.

**E25 - Amiri M., Ardeshir A., Fazel Zarandi M.H. (2017). Fuzzy probabilistic expert system for occupational hazard assessment in construction. Safety Science 93: 16-28.**
- DOI 10.1016/j.ssci.2016.11.008 (Crossref verified). Closed access. Evidence: SNIPPET ONLY (search result summary; abstract not retrieved).
- Per snippet: rule base generated from fuzzy risk-based statistical and data-mining analysis of an accident database, literature review and expert interviews; tested on four major construction case studies.
- Numbers NR. Design decision (tentative): rules can be sourced from three channels (data, literature, experts) and each rule should carry its channel. Weak evidence.

**E26 - Zhasmukhambetova A., Evdorides H., Davies R.J. (2025). Integrating Risk Assessment and Scheduling in Highway Construction: A Systematic Review of Techniques, Challenges, and Hybrid Methodologies. Future Transportation 5(3): 85.**
- DOI 10.3390/futuretransp5030085 (Crossref verified). Access: OA, CC BY 4.0 (Crossref). Evidence: ABSTRACT.
- Review scope: probability-impact (P-I), Monte Carlo simulation, fuzzy set theory, AHP with CPM and PERT scheduling; findings: CPM/PERT remain widely used but limited for dynamic uncertainty; MCS, fuzzy sets and AHP help but need careful adaptation; hybrid/integrated approaches combining risk assessment and scheduling are increasingly relevant; Bayesian networks flagged as promising. Number of papers reviewed NR (abstract).
- Design decision: supports a hybrid of risk-matrix (P-I) screening with Monte Carlo schedule simulation; the AI layer sits outside this hybrid.

**E27 - Gao L., Madaan A., Zhou S., Alon U., Liu P., Yang Y., Callan J., Neubig G. (2023). PAL: Program-aided Language Models. ICML 2023 (PMLR 202; arXiv:2211.10435).**
- No publisher DOI; arXiv identifier. Evidence: FULL-TEXT (abstract read, 34 pages). GENERAL.
- Built: LLM writes programs as intermediate reasoning steps and a Python interpreter executes them; tested on 13 mathematical, symbolic and algorithmic reasoning tasks.
- Numbers (abstract): PAL with Codex reaches state-of-the-art few-shot accuracy on GSM8K, surpassing PaLM-540B with chain-of-thought by absolute 15% top-1. Authors' motivation: LLMs "often make logical and arithmetic mistakes in the solution part, even when the problem is decomposed correctly".
- Limitations: benchmark tasks, not engineering decisions.
- Design decision: architectural precedent for the LLM proposing structured inputs/steps while a deterministic runtime performs the calculation (in the proposed system the "runtime" is the fixed Monte Carlo/EMV engine, and the LLM would not write code that changes numerical logic).

### E. Standards and guidance (NOT empirical research)

**E28 - Tabassi E. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1, 26 January 2023.**
- DOI 10.6028/NIST.AI.100-1 (Crossref verified). Evidence: FULL-TEXT (PDF, 48 pages; sections 3.1, 3.4, 3.5 read). STANDARD/GUIDANCE.
- Content: trustworthiness characteristics include valid and reliable; accountable and transparent; explainable and interpretable. Text states "Accountability presupposes transparency"; maintaining provenance of training data and supporting attribution of decisions "can assist with both transparency and accountability"; proportionate transparency where consequences are severe.
- Design decision: adopt audit-trail and documentation practice proportionate to consequences; map system features to these characteristics in the final report.

**E29 - NIST (2024). Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile. NIST AI 600-1, 26 July 2024.**
- DOI 10.6028/NIST.AI.600-1 (Crossref verified; no authors listed). Evidence: FULL-TEXT (PDF, 64 pages; confabulation section and MS-2.5 actions read). STANDARD/GUIDANCE.
- Content: defines "confabulation" as confidently stated erroneous or false content (colloquially hallucination); notes generated outputs may include "confabulated logic or citations that purport to justify or explain the system's answer, which may further mislead humans into inappropriately trusting the system's output". Suggested actions include: MS-2.5-002 document the extent to which human domain knowledge is employed (RLHF, fine-tuning, retrieval-augmented generation, content moderation, business rules); MS-2.5-003 "Review and verify sources and citations in GAI system outputs during pre-deployment risk measurement and ongoing monitoring"; MS-2.5-005 verify that fine-tuning or RAG data is grounded.
- Design decision: mandatory citation verification and documented RAG corpus provenance; label LLM text as unverified.

**E30 - High-Level Expert Group on AI (European Commission) (2019). Ethics Guidelines for Trustworthy AI, 8 April 2019.**
- DOI NR/NC. Evidence: PAGE-SUMMARY (EC library page; PDF not read). GUIDANCE.
- Seven requirements listed on the page: human agency and oversight; technical robustness and safety; privacy and data governance; transparency; diversity, non-discrimination and fairness; societal and environmental well-being; accountability (auditability). No reuse licence statement seen.
- Design decision: human-in-the-loop sign-off and auditability requirements.

### G. Evidence on when machine learning is NOT justified (small data)

(Medical/statistical papers below are GENERAL; used only for their generic findings on sample size, model complexity and validation.)

**E42 - van der Ploeg T., Austin P.C., Steyerberg E.W. (2014). Modern modelling techniques are data hungry: a simulation study for predicting dichotomous endpoints. BMC Med. Res. Methodol. 14: 137.**
- DOI 10.1186/1471-2288-14-137 (Crossref verified). Access: OA, CC BY (PMC page as returned by fetch tool). Evidence: FULL-TEXT (PMC XML text retrieved; abstract results confirmed verbatim: LR stable at approximately 20 to 50 EPV; RF, SVM and NN unstable with high optimism even with >200 EPV; paper also states its results confirm the accepted rule of at least 10 EPV even for LR). GENERAL (medical cohorts).
- Tested: logistic regression (LR), CART, SVM, neural nets, random forests on three clinical cohorts replicated to large size: HNSCC 1,282 patients replicated 20x (25,640 subjects, 7 predictors); TBI 1,731 x10 (17,310, 10 predictors); CHIP 3,181 x6 (19,086, 12 predictors). "Data hungriness" = minimum events per variable (EPV) at which optimism <0.01.
- Numbers: LR reached stable AUC at about 20-50 EPV; SVM, NN and RF needed over 10 times as many EPV; RF, SVM and NN still showed instability/high optimism even above 200 EPV (from the abstract as returned by search; page summary consistent).
- Limitations (authors): non-linearity not a major issue in the cohorts; default settings; three cohorts with differing incidence; LASSO not evaluated.
- Design decision (inference for a small brick-masonry dataset): flexible ML needs far more data per predictor than simple models, so ML is not justified with tens of records.

**E43 - Vabalas A., Gowen E., Poliakoff E., Casson A.J. (2019). Machine learning algorithm validation with a limited sample size. PLOS ONE 14(11): e0224365.**
- DOI 10.1371/journal.pone.0224365 (Crossref verified). Access: OA, CC BY 4.0 (Crossref + PMC page). Evidence: FULL-TEXT (PMC XML text retrieved; abstract sentence on K-fold CV bias at N = 1000 confirmed verbatim; paper also notes small sample size is associated with higher reported classification accuracy in the literature). GENERAL.
- Tested: SVM (RBF) with SVM-RFE and logistic regression with t-test feature selection; simulated Gaussian-noise and discriminable data with N from 20 to 1000; literature survey of 55 autism studies (median N = 80).
- Findings: K-fold cross-validation gives strongly biased performance estimates with small samples and the bias is still evident at N = 1000; nested CV and a train/test split gave unbiased estimates; non-nested feature selection biased results more than parameter tuning.
- Limitations: balanced binary classification with two algorithm types.
- Design decision: if any predictive model is ever fitted to a small construction dataset, use nested cross-validation or a hold-out set and report against a baseline.

**E44 - Riley R.D., Snell K.I.E., Ensor J., Burke D.L., Harrell F.E., Moons K.G.M., Collins G.S. (2019). Minimum sample size for developing a multivariable prediction model: Part II - binary and time-to-event outcomes. Statistics in Medicine 38(7): 1276-1296.**
- DOI 10.1002/sim.7992 (Crossref verified). Access: PMC6519266; Crossref licence CC BY-NC 4.0. Evidence: ABSTRACT (PubMed). GENERAL (medical).
- Content: minimum n and events E chosen to meet three criteria (shrinkage factor >= 0.9; absolute difference <= 0.05 between apparent and adjusted Nagelkerke R2; precise overall risk estimate); worked examples needing EPP of at least 4.8 (Chagas disease diagnostic model) and at least 23 (recurrent VTE prognostic model); "rules of thumb (eg, 10 EPP) should be avoided".
- Design decision: the required sample size depends on the number of candidate predictors and expected model fit, so pre-specify a sample-size justification before claiming an ML model.

**E45 - Christodoulou E., Ma J., Collins G.S., Steyerberg E.W., Verbakel J.Y., Van Calster B. (2019). A systematic review shows no performance benefit of machine learning over logistic regression for clinical prediction models. J. Clin. Epidemiol. 110: 12-22.**
- DOI 10.1016/j.jclinepi.2019.02.004 (Crossref verified). Access: Elsevier TDM; OA not verified. Evidence: ABSTRACT (PubMed). GENERAL (medical).
- Numbers: 71 of 927 studies; median sample size 1,250 (range 72-3,994,872), 19 predictors, eight events per predictor; 282 LR-vs-ML comparisons; for 145 low-risk-of-bias comparisons the difference in logit(AUC) between LR and ML was 0.00 (95% CI -0.18 to 0.18); for 137 high-risk-of-bias comparisons ML was 0.34 (0.20-0.47) higher; potential validation bias in 48 (68%) studies; calibration not addressed in 56 (79%). Conclusion: "no evidence of superior performance of ML over LR".
- Design decision: an apparent ML advantage can be an artefact of biased validation; always include a simple baseline (expert PERT/regression).

**E46 - Davila Delgado J.M., Oyedele L. (2021). Deep learning with small datasets: using autoencoders to address limited datasets in construction management. Applied Soft Computing 112: 107836.**
- DOI 10.1016/j.asoc.2021.107836 (Crossref verified). Access: Elsevier TDM; green repository copy (submitted version, cc-by-nc-nd per OpenAlex, not viewed); OA not verified. Evidence: ABSTRACT (Semantic Scholar). CONSTRUCTION.
- Statement (abstract): "Poor data management practices and the low level of digitisation of the construction industry represent a big hurdle to compiling big datasets". Tested autoencoder augmentation on two financial datasets (underground and overhead power transmission projects) predicting project cost with a deep neural network regressor: average model-score improvement 7.2% (underground) and 11.5% (overhead); average error improvement 22.9% and 56.5%. Original dataset sizes NR (abstract).
- Limitations: cost data of power transmission projects; synthetic augmentation; not delay data.
- Design decision: confirms that construction datasets are typically too small for deep learning without augmentation; augmentation adds complexity and synthetic-data risk, not justified for this project.

**E47 - Zhang S., Li X. (2024). A comparative study of machine learning regression models for predicting construction duration. J. Asian Architecture and Building Engineering 23(6): 1980-1996.**
- DOI 10.1080/13467581.2023.2278887 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence field). Evidence: ABSTRACT (Semantic Scholar). CONSTRUCTION. COUNTER-EVIDENCE.
- Tested: KNN, SVR, gradient boosting trees (GBT), ANN forecasting construction days per work area from progress, workload, labour, weather, planned days and location; "a simple and widely used baseline model" used for comparison; ANN and GBT "produced significantly superior results"; GBT more computationally efficient. Dataset size and error values NR.
- Design decision: not all comparisons favour baselines; with sufficient field data ML can beat a simple baseline, so the decision must be data-size dependent and baseline-referenced. (Inference.)

**E48 - Naser M.Z. (2026). A review of machine learning with small and limited data. Journal of Big Data 13(1): 18.**
- DOI 10.1186/s40537-025-01346-9 (Crossref verified). Access: OA, CC BY 4.0 (Crossref). Evidence: ABSTRACT. GENERAL (author is a civil/structural engineer; not construction-specific).
- Content (abstract): survey of ML for small and very small datasets; trade-offs including overfitting, generalisation error and bias-variance; identifies "minimal interventions"; role of synthetic data; emerging directions include incorporating domain knowledge and causal principles and integrating symbolic reasoning with statistical learning. No numbers.
- Design decision: supports domain-knowledge-driven (symbolic/rule) modelling for small-data settings.

## 4. Additional detailed entries (E49-E57)

**E49 - Prieto S.A., Mengiste E.T., Garcia de Soto B. (2023). Investigating the Use of ChatGPT for the Scheduling of Construction Projects. Buildings 13(4): 857.**
- DOI 10.3390/buildings13040857 (Crossref verified). Access: OA, CC BY 4.0 (Crossref). Evidence: ABSTRACT (Crossref); full text not seen. CONSTRUCTION.
- Built/tested: ChatGPT generated a construction schedule for a simple project; a pool of participants rated the interaction experience and output quality. Abstract: ChatGPT "can generate a coherent schedule that follows a logical approach to fulfill the requirements of the scope"; participants positive; "the technology still has limitations, and further development is needed before it can be widely adopted". Numbers (participants, scores) NR.
- Limitations: simple project, participant-rated quality (not measured against actual durations).
- Design decision: an LLM can draft a plausible logical sequence but this is not validated durations; in the proposed system the LLM must not generate activity durations or delays that enter the simulation.

**E50 - Taiwo R., Bello I.T., Abdulai S.F., Yussif A.-M., Salami B.A., Saka A., Ben Seghier M.E.A., Zayed T. (2025). Generative artificial intelligence in construction: A Delphi approach, framework, and case study. Alexandria Engineering Journal 116: 672-698.**
- DOI 10.1016/j.aej.2024.12.079 (Crossref verified). Access: Crossref licence field lists creativecommons.org/licenses/by/4.0 (plus Elsevier TDM); treated as OA CC BY 4.0. Evidence: ABSTRACT (Semantic Scholar). CONSTRUCTION.
- Built/tested: Delphi study plus systematic review and expert consultation; framework for firm-specific GenAI solutions; case study with a GenAI model querying contract documents using RAG.
- Numbers (abstract): 76 potential GenAI applications across construction phases and 18 key challenges (domain-specific, technological, adoption, ethical); in the case study "RAG improves the baseline LLM, GPT-4, by 5.2, 9.4, and 4.8 % in terms of quality, relevance, and reproducibility". Sample size/rubric of the case study NR (abstract).
- Limitations: NR from abstract; single contract-query case.
- Design decision: RAG gave modest, measurable gains over a plain GPT-4 baseline on a construction document task (effect sizes are small, so evaluation must be done on own corpus); recommends robust validation protocols.

**E51 - Qu R., Tu R., Bao F.S. (2025). Is Semantic Chunking Worth the Computational Cost? Findings of the ACL: NAACL 2025, pp. 2155-2177.**
- DOI 10.18653/v1/2025.findings-naacl.114 (Crossref verified; arXiv 2410.13070). Access: ACL Anthology; licence not checked. Evidence: ABSTRACT (arXiv). GENERAL.
- Tested: semantic chunking vs fixed-size chunking on document retrieval, evidence retrieval and retrieval-based answer generation. Abstract: "the computational costs associated with semantic chunking are not justified by consistent performance gains". Numbers NR (abstract only).
- Design decision: start with simple fixed-size (or structure-based: section/paragraph) chunking with overlap and metadata; treat chunk size as a calibrated parameter (E15) rather than adopting expensive semantic chunking by default. (Inference.)

**E52 - Schick T., Dwivedi-Yu J., Dessi R., Raileanu R., Lomeli M., Zettlemoyer L., Cancedda N., Scialom T. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. NeurIPS 2023 (arXiv:2302.04761).**
- No publisher DOI. Evidence: ABSTRACT (arXiv API). Venue NeurIPS 2023 taken from a search-result listing (not independently verified). GENERAL.
- Content (abstract): LMs "struggle with basic functionality, such as arithmetic or factual lookup"; Toolformer learns which APIs to call, when, with which arguments; tools include a calculator, Q&A system, two search engines, translation system and calendar; improved zero-shot performance. Numbers NR.
- Design decision: precedent for tool-calling architectures where arithmetic/lookup are delegated to external tools; in this project the only tools exposed to the LLM would be read-only (retrieve evidence, read engine outputs), not tools that change the model.

**E53 - Atil B., Aykent S., Chittams A., Fu L., Passonneau R.J., Radcliffe E., Rajagopal G.R., Sloan A., Tudrej T., Ture F., Wu Z., Xu L., Baldwin B. (2024). Non-Determinism of "Deterministic" LLM Settings. arXiv:2408.04667 (v5). PREPRINT (no journal reference on arXiv; peer-review status NC).**
- No DOI verified. Evidence: ABSTRACT (arXiv API). GENERAL.
- Tested: five LLMs configured to be deterministic on eight tasks over 10 runs, zero-shot and few-shot. Numbers (abstract): accuracy variations up to 15% across runs; gap between best and worst possible performance up to 70%; "none of the LLMs consistently delivers repeatable accuracy across all tasks, much less identical output strings"; introduces TARr@N and TARa@N agreement metrics.
- Design decision: corroborates E06; LLM outputs are not reproducible even at "deterministic" settings, so audit records must store the generated text and any reproducibility claim must be limited to the deterministic engine (seeded simulation). Preprint status flagged.

**E54 - Mitchell M., Wu S., Zaldivar A., Barnes P., Vasserman L., Hutchinson B., Spitzer E., Raji I.D., Gebru T. (2019). Model Cards for Model Reporting. Proc. FAT* 2019, pp. 220-229.**
- DOI 10.1145/3287560.3287596 (Crossref verified; arXiv 1810.03993 copy). Evidence: ABSTRACT (Semantic Scholar). GENERAL.
- Content (abstract): proposes model cards, short documents accompanying trained models with benchmarked evaluation, intended use context and evaluation procedure details, "to clarify the intended use cases ... and minimize their usage in contexts for which they are not well suited". No numbers.
- Design decision: ship an AI-layer "model card"/system card documenting model version, intended use (retrieval, drafting, explanation only), prohibited uses (no numerical outputs), evaluation results and known failure modes.

**E55 - Chen Y., Liang B., Hu H. (2025). Research on ontology-based construction risk knowledge base development in deep foundation pit excavation. J. Asian Architecture and Building Engineering 24(3): 1640-1658.**
- DOI 10.1080/13467581.2024.2329361 (Crossref verified). Access: OA, CC BY-NC 4.0 (Crossref licence field). Evidence: ABSTRACT (Semantic Scholar). CONSTRUCTION.
- Built: ontology knowledge base for deep foundation pit excavation risk via a six-step method (classes, hierarchy, objects, data attributes); ontology instances created "to further evaluate the integrity, correctness and consistency of the developed knowledge base"; rule libraries; case studies show rule reasoning identifies potential risk events and provides prevention measures. Numbers NR.
- Limitations: NR (abstract).
- Design decision: rule libraries should be checked for integrity, correctness and consistency (i.e. detect conflicting or incomplete rules) before use; a consistency check is a concrete validation step for the rule base. (Inference for the check design.)

**E56 - Kaska M.S., Kiral I.A. (2026). Explainable Machine Learning for Early-Stage Construction Duration Prediction Using Limited Project Information. Research Square preprint (posted 2026-09-08). PREPRINT, not peer reviewed.**
- DOI 10.21203/rs.3.rs-10706536/v1 (Crossref verified, type posted-content; licence CC BY 4.0 per Crossref). Evidence: ABSTRACT (Crossref). CONSTRUCTION.
- Built/tested: 209 completed construction projects; explanatory variables project cost, public/private status, project type, location; Random Forest, Extra Trees, XGBoost and ANN compared using holdout, cross-validation, repeated holdout and repeated cross-validation.
- Numbers (abstract): selected holdout XGBoost R2 = 0.853, MAE = 174.5 days, RMSE = 227.7 days, MAPE = 27.0%; repeated validation mean R2 = 0.755 (repeated holdout) and 0.732 (repeated cross-validation), "sensitivity to data partitioning". Authors state the framework "should not be considered an alternative to a detailed CPM schedule".
- Limitations (authors): internal validation only; "subject to external validation".
- Design decision: with about 200 records a single holdout overstates performance; supports reporting repeated validation and preferring conservative estimates; also shows typical MAPE of ~27% for a simple early-stage ML model (a benchmark a simple expert-elicited approach would need to be compared against). PREPRINT flagged.

**E57 - Namazian A., Haji Yakhchali S., Yousefi V., Tamosaitiene J. (2019). Combining Monte Carlo Simulation and Bayesian Networks Methods for Assessing Completion Time of Projects under Risk. Int. J. Environ. Res. Public Health 16(24): 5024.**
- DOI 10.3390/ijerph16245024 (Crossref verified). Access: OA, CC BY 4.0 (Crossref licence; PMC6950629 licence text). Evidence: ABSTRACT (PMC). CONSTRUCTION (industrial case).
- Built: structure combining Monte Carlo simulation with Bayesian networks to assess the aggregated impact of interacting risks on project completion time; implemented in an industrial case study to validate the model. Numbers NR (abstract).
- Limitations: NR from abstract.
- Design decision: precedent for hybrid probabilistic-reasoning + Monte Carlo structures in construction time risk; risk interactions are a known gap when a purely additive matrix is used.

## 5. Systematic and other reviews of AI in construction risk and delay (2020-2026)

More than eight review-type papers verified. "N" = number of papers reviewed as stated in the abstract/page. Evidence level in brackets.

| ID | Citation | Scope | N reviewed | Main gaps identified | Access |
|---|---|---|---|---|---|
| E31 | Tian K., Zhu Z., Mbachu J., Ghanbaripour A., Moorhead M. (2025). AI in risk management within the realm of construction projects: bibliometric analysis and SLR. J. Innov. Knowl. 10(3): 100711. DOI 10.1016/j.jik.2025.100711 [Crossref verified; page via fetch: abstract verbatim] | AI applications, risk categories, key algorithms; bibliometrics (VOSviewer), Bradford/Lotka laws, thematic analysis | 84 peer-reviewed articles, 2014-2024 | data quality, model interpretability, workforce skills hinder AI integration; blockchain integration; adaptive risk models for responsible adoption | OA CC BY 4.0 (Crossref) |
| E32 | Tian K., Zhu Z., Mbachu J., Moorhead M., Ghanbaripour A. (2025). AI in construction risk management: a decade of developments, challenges, and integration pathways. J. Risk Res. 28(9-10): 1078-1110. DOI 10.1080/13669877.2025.2512080 [Crossref verified; abstract via Bond Univ. repository page] | ML, NLP, knowledge-based reasoning, optimisation algorithms, computer vision across risk identification, assessment, response, monitoring; PRISMA + NVivo (search snippet) | 87 studies, 2014-2024 | fragmentation, limited adaptability, socio-organisational resistance; structured guidance needed for responsible AI deployment; notes NLP and KBR support compliance and rule-based decision-making | closed (no licence seen) |
| E33 | Gao Y., Yiu T.W., Shen X., Tam V.W.Y. (2026). Large language models in smart construction: a systematic review of implementation strategies, applications and future directions. ECAM 33(15): 159-181 (Crossref issue date 2026-12-14, i.e. a future-dated/early-access record). DOI 10.1108/ECAM-10-2025-1668 [Crossref verified; page via fetch] | LLMs across construction tasks; most use pretrained models adapted by fine-tuning, RAG or prompt engineering | 142 peer-reviewed articles (2020-2025, mostly 2024-2025) | abstract: "challenges persist in domain adaptation, hallucination control, data privacy and lifecycle integration"; page summary also lists missing evaluation standards/benchmarks and governance frameworks | OA CC BY 4.0 (Crossref) |
| E34 | Egwim C.N., Alaka H., Demir E., Balogun H., Ajayi S. (2022/2023). Systematic review of critical drivers for delay risk prediction: towards a conceptual framework for BIM-based construction projects. Front. Eng. Built Environ. 3: 61 (online 2022-10-13). DOI 10.1108/FEBE-05-2022-0017 [Crossref verified; page via fetch] | delay risk drivers for BIM-based projects; PRISMA | 50 articles (31 journals, 17 proceedings, 2 books) | no consolidated framework for selecting delay-risk drivers in BIM-based projects; limited analysis of variables before building predictive models; contractor-related and external drivers most important | OA CC BY 4.0 (publisher page; Crossref shows publisher policy only) |
| E35 | Mohamed M.A.H., Al-Mhdawi M.K.S., Ojiako U., Dacre N., Qazi A., Rahimian F. (2025). Generative AI in construction risk management: a bibliometric analysis of the associated benefits and risks. Urban. Sustain. Soc. 2(1): 198-230. DOI 10.1108/USS-11-2024-0069 [Crossref verified; page via fetch] | GenAI benefits and risks in construction risk management; Scopus | 55 articles (of 473 identified), 2014-2024 | lack of comprehensive GenAI risk-management models; need for interdisciplinary work; geographic concentration (USA, UK, China); risks span nine areas including security, data and performance | OA CC BY (Crossref) |
| E36 | Razi N., Badhan S.J., Samsami R. (2026). AI in Construction Management (CM): A Systematic Review of Models and Methods. Buildings 16(11): 2225. DOI 10.3390/buildings16112225 [Crossref verified; abstract via Crossref] | AI methods vs CM functions; taxonomy; Gen-AI, XAI, transformers | 191 peer-reviewed articles, 2020-2025 | legal analytics, robotics, cybersecurity underexplored; AI concentrated in risk and safety management, decision support, monitoring/control; ML and optimisation used for cost estimation and scheduling | OA CC BY 4.0 (Crossref) |
| E37 | Gao Y., Antwi-Afari M.F., Huang Y., Chen Z.-S., Manzoor B. (2026). AI in Construction Project Management: A Systematic Literature Review of Cost, Time, and Safety Management. Buildings 16(5): 1061. DOI 10.3390/buildings16051061 [Crossref verified; abstract via Crossref] | cost, time (incl. delay risk prediction, planning/scheduling) and safety; PRISMA, Scopus | 392 articles | abstract states challenges and research gaps were discussed; specific gaps not in the abstract (NR) | OA CC BY 4.0 (Crossref) |
| E38 | Sadikoglu E., Demirkesen S. (2026). Mapping the state-of-the-art: bibliometric and systematic analysis of ML and AI-based cost and time prediction in construction. J. Asian Archit. Build. Eng. DOI 10.1080/13467581.2026.2641274 [Crossref verified; N from search snippet only, abstract not retrieved] | ML/AI cost and time prediction; bibliometrics + content analysis | 303 studies (SNIPPET only) | NR | CC BY-NC 4.0 (Crossref) |
| E39 | Zhang W. (2026). ML and AI in construction project cost prediction: scientometric analysis and qualitative review. Front. Built Environ. 12: 1867673. DOI 10.3389/fbuil.2026.1867673 [Crossref verified; abstract via Crossref] | cost prediction; PRISMA; WoS + Scopus | 138 articles | "unstable data quality, limited cross-regional generalization, and low model interpretability" | OA CC BY 4.0 (Crossref) |
| E40 | Arar E., Halicioglu F.H. (2025). Understanding ANNs as a Transformative Approach to Construction Risk Management: A Systematic Literature Review. Buildings 15(18): 3346. DOI 10.3390/buildings15183346 [Crossref verified; abstract via Crossref] | ANN in construction risk management; PRISMA 2020; Scopus 1990-2024 | 84 studies (4648 records -> 2483 -> 132 -> 86 -> 84) | data quality, computational demands, interpretability; recommends hybrids (fuzzy, GA, Monte Carlo), XAI, real-time data | OA CC BY 4.0 (Crossref) |
| E41 | Kampelopoulos D., Tsanousa A., Vrochidis S., Kompatsiaris I. (2025). A review of LLMs and their applications in the AEC industry. Artif. Intell. Rev. 58(8): 250. DOI 10.1007/s10462-025-11241-7 [Crossref verified; abstract via Crossref] | LLM applications and use cases in AEC | NR | notes limited number of studies in AEC; emerging challenges and recommendations (details NR) | OA CC BY 4.0 (Crossref) |
| (E18) | Love et al. 2023 (narrative XAI review) | see E18 | NR | - | - |
| (E19) | Naghdi et al. 2026 (XAI in CEM) | see E19 | 55 | small/imbalanced data, weak validation, limited human evaluation | closed |
| (E09,E10,E26) | Saka 2024; Ghimire 2024; Zhasmukhambetova 2025 | see entries | - | - | - |

## 6. What the evidence supports about the proposed AI role

Labels: [DIRECT] = a paper reports this; [INFERENCE] = my reasoning for the design, not a finding of any paper.

1. LLMs can draft comprehensive risk and response lists that human raters score highly, but with weaker practicality/specificity and only moderate accuracy. [DIRECT] E01 (8.6 vs 5.7 mean score; "lack practicality and specificity"), E02 ("moderate level"), E03 (similar to experts). [INFERENCE] Restrict the LLM to identification assistance and mitigation-option drafting; every LLM-drafted item is tagged "unverified - requires reviewer confirmation".
2. LLMs make calculation and reasoning errors and are not reproducible even with controlled settings. [DIRECT] E06 (calculation errors 7% of failure cases; identical queries sometimes differ under controlled temperature/seed; authors advise against relying on LLMs for calculation and suggest function calling), E27 (arithmetic mistakes even when decomposition is right; offloading to an interpreter helps), E07 snippet (inaccurate numerical responses named as a challenge), E52 (LMs struggle with arithmetic; tool use as remedy), E53 preprint (accuracy varies up to 15% across runs at "deterministic" settings), E49 (ChatGPT schedules coherent but only participant-rated). [INFERENCE] All numbers (distributions, simulation, risk scores, EMV) come from the deterministic engine; the LLM never edits parameters or results; any tools exposed to the LLM are read-only; LLM text is stored verbatim with model name/version/parameters in the audit log.
3. Ungrounded LLMs fabricate references at high rates. [DIRECT, general medical] E17 (hallucination 28.6-91.4%; precision 0-13.4%). [INFERENCE] The LLM may cite only chunk/paper IDs supplied in the retrieved context; a verifier rejects any ID not in the curated corpus and checks quoted text against the chunk.
4. Retrieval grounding improves domain answers but is not sufficient, and effect sizes vary widely. [DIRECT] E08 (88% vs 36%), E50 (RAG improved GPT-4 by only 5.2, 9.4 and 4.8% on quality, relevance, reproducibility), E07 snippet (RAG-GPT superior, experts), E12 (index hot-swap and provenance), E11 (lexical retrievers competitive on building-code text), E51 (semantic chunking not consistently better than fixed-size), versus limits: E14 (best models lack complete citation support 50% of the time on ELI5), E16 (middle-of-context degradation), E15 (seven failure points including missing content and not extracted), E06 (retrieval "tug-of-war"). [INFERENCE] "Answer only from retrieved evidence" prompt + explicit "not in corpus" refusal path + top-k ordered context + per-claim faithfulness check (E13) + human review; NIST AI 600-1 (E29) calls for verifying sources/citations and grounded RAG data.
5. Faithfulness can be evaluated automatically, with caveats. [DIRECT] E13 (0.95 agreement on WikiEval faithfulness; 0.70 on context relevance), E14 (kappa 0.698/0.525). [INFERENCE] Use these metrics as regression tests, but calibrate them on a small expert-labelled set of masonry claims before trusting them.
6. Explanations do not automatically produce better decisions. [DIRECT] E21 (explanations raise acceptance regardless of correctness), E22 (transparent model did not increase following and reduced detection of model mistakes), E20 (post-hoc explanations can mislead; prefer interpretable models), E19 (construction XAI mostly post-hoc SHAP, little human evaluation). [INFERENCE] The primary explanation is the engine's own trace (inputs, rule IDs, distributions, seed); the LLM narrative is secondary, cited and labelled; plan a small usability check for over-reliance.
7. Rule/knowledge-based systems in construction combine fact/rule/case bases and hybrid inference, elicitation from experts is a bottleneck, and knowledge bases are checked for integrity, correctness and consistency. [DIRECT] E23, E24, E55 (E25 snippet); Koulinas 2020/2021 already collected. [INFERENCE] Each rule stored with an ID, source citation, elicitation channel and reviewer; an automated consistency check flags contradictory or incomplete rules; conflict rules resolved by a documented precedence. NOTE: I did not find in verified papers a description of formal rule conflict-resolution in construction expert systems (gap in my search).
8. Hybrid risk assessment + scheduling is a recognised direction. [DIRECT] E26 (hybrid P-I/MCS/fuzzy/AHP; BNs promising), E40 (recommends hybrids with Monte Carlo and XAI). Reviews show AI in risk management is dominated by ML/CV, with NLP and knowledge-based reasoning for compliance and rule-based decision making (E32). [INFERENCE] The proposed rule + Monte Carlo + EMV + LLM-explanation architecture is consistent with the literature direction; no paper found in my searches evaluates an LLM interpreting outputs of a deterministic Monte Carlo/EMV engine in construction (absence within my 39 searches only).
9. Traceability/trustworthiness. [GUIDANCE] E28 (transparency, provenance, accountability proportional to consequences), E29 (documentation of RAG data and human knowledge incorporated), E30 (human oversight, auditability); [DIRECT, general] E54 (model cards: documented intended use, evaluation and limits). [INFERENCE] Provide an AI-layer model card; log: input hash, engine version, rule-set version, RNG seed, retrieved chunk IDs, prompt, model ID/version/parameters, raw LLM output, reviewer decision.
10. Small data: ML is hard to justify. [DIRECT, general medical/statistical] E42 (LR stable at ~20-50 EPV; SVM/NN/RF need >10x and stay unstable above 200 EPV), E43 (K-fold CV biased even at N=1000), E44 (sample size depends on predictors and expected fit; avoid 10-EPP rule), E45 (no evidence ML > LR in low-bias comparisons; 0.00 logit(AUC) difference). [DIRECT, construction] E19 (small and imbalanced datasets), E39 (unstable data quality), E46 (construction data scarcity; augmentation needed). [DIRECT, construction, PREPRINT] E56 (209 projects: single holdout R2 0.853 vs repeated-validation means 0.755 and 0.732, "sensitivity to data partitioning"; MAPE 27.0% in the selected holdout). COUNTER-EVIDENCE: E47 (ML beat a simple baseline in one duration study; size NR). [INFERENCE] For one activity and likely tens of records, use expert/literature-elicited distributions and no trained ML model; if ML is added later, require a baseline, nested validation and a pre-stated sample-size rationale.

## 6b. Composition of the list and a recommended core shortlist

The brief asked for 25-35 papers; this file holds 57 IDs because reviews (E31-E41) and short-evidence items were kept for completeness. Composition of the 57 IDs: 3 standards/guidance (E28-E30, not empirical); 11 reviews in the review table (E31-E41); 5 further review-like or narrative items (E09, E10, E18, E19, E26); 19 GENERAL non-construction papers (E12-E17, E20-E22, E27, E42-E45, E48, E51-E54); 19 construction primary studies or tools (E01-E08, E11, E23-E25, E46, E47, E49, E50, E55-E57). Three items are preprints and flagged as such: E11 (arXiv), E53 (arXiv, general) and E56 (Research Square). E04, E07 and E25 rest on search snippets only and are weak evidence.

Recommended core shortlist for citing (33 IDs; peer-reviewed or clearly labelled guidance, except E56 which is a preprint): E01, E02, E05, E06, E08, E09 (LLM/RAG in construction); E12, E13, E14, E15, E17, E51 (RAG design/faithfulness/citations, general); E18, E19, E20, E21, E22 (XAI/trust); E23, E24, E55 (rule/knowledge-based); E26, E27 (hybrid/tool use); E28, E29, E30, E54 (governance/traceability); E31, E32, E33 (systematic reviews of AI in construction risk and LLMs); E42, E44, E45, E56 (small-data ML evidence; E56 is a preprint).

## 7. Open items / not yet verified (to continue)

- Zagia et al. 2026 (Buildings 16(16): 3149, XGBoost-SHAP on 22 delay risk factors, DOI verified) was seen but NOT reported because it is already in the project library (Research_Papers folder 1). Other candidates verified by DOI only, abstract NR: Tian et al. 2026 AEI prefabricated delay XAI (10.1016/j.aei.2025.104219); Taghipour et al. 2026 ASEJ FIDIC delay XAI (10.1016/j.asej.2026.104362); Dikmen et al. 2022 Computers in Industry rule-based complexity-risk tool (10.1016/j.compind.2022.103694); Xiahou et al. 2022 JCEM BIM design-stage safety risk with rule base (10.3846/jcem.2022.16560; abstract via Crossref: design and review rules in a knowledge base, one case study).
- Candidates seen only by title or snippet and NOT used as evidence: Lundberg & Lee 2017 SHAP; Riley et al. 2020 BMJ (no abstract retrievable); Okudan et al. 2021 ESWA CBR risk tool (abstract empty in Semantic Scholar); Liao et al. 2025 J. Comput. Civ. Eng. prefabricated safety RAG QA (DOI 10.1061/JCCEE5.CPENG-6315 verified, abstract NR); Zhang et al. 2026 RAG-for-CR J. Constr. Eng. Manage. (DOI 10.1061/JCEMD4.COENG-18263 verified, abstract NR); Gundidza et al. 2025 PRICAI delay-risk LLM classification (DOI 10.1007/978-981-96-0119-6_30 verified, abstract NR); Abioye 2021 J. Build. Eng. AI review (abstract truncated); Pan & Zhang 2021 AutCon review (closed); Al-Mhdawi 2023 SSRN preprint on ISO 31000 (preprint).
- Not yet found: explicit rule conflict-resolution methods in construction expert systems (only integrity/consistency checking, E55); construction SHAP-delay papers with verified numbers outside the project library (a search snippet mentioned one Springer paper with accuracy 79.29% and recall 88.9%, not verified and not used); tool-use/neuro-symbolic papers specific to construction; evaluations of an LLM interpreting outputs of a deterministic Monte Carlo/EMV engine.
- Tool limits reached: shared WebSearch budget and WebFetch session limit; remaining discovery done through Crossref/OpenAlex/PubMed/Semantic Scholar APIs.
