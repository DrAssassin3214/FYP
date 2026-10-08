# Appendix J. Glossary and abbreviations

**Table J.1.** Terms used in this report. Definitions follow the use in this project, not necessarily a standard.

| Term | Meaning in this report |
|---|---|
| Activity | One masonry work package (brick or block walls of a floor or part of a building), the unit for which a case is built. |
| Agreement check | A comparison of the order of risks in one survey with the order of the literature seed, using rank correlation on the risks both have. It is exploratory and low-powered; it is not validation. |
| AAC | Autoclaved aerated concrete (block). |
| Assumption | A Source label for a value or rule chosen by the project team with no supporting data. Every assumption is listed in Appendix H. |
| Band, class | One of five ordinal groups (1 to 5). The seed puts the 30 seeded risks into five bands of six by mean RII. Probability and impact are also classified 1 to 5. |
| Case | The JSON file that holds one activity, its site facts, risks, entered numbers and sources (Appendix D). |
| CPWD | Central Public Works Department (India); its labour norms are cited in the legacy productivity code, which is out of scope. |
| Delay (in the tool) | Extra working days of delay if the risk occurs, entered by the user as a range (PERT, triangular, uniform or fixed). |
| Derived Calculation | A Source label for a number computed from other labelled numbers; it inherits ILLUSTRATIVE if its inputs do. |
| EMV | Expected monetary value: the probability-weighted cost of an outcome. Used only in the optional decision layer, on user-entered numbers. |
| Expert Judgment | A Source label for a value or mapping that comes from a person's professional judgment. The factor-to-risk mapping is Expert Judgment by one coder. |
| Fact | A site condition entered as Yes / No / Unknown or as a number; the input of a rule. |
| Held-out study | One of the 6 surveys in the seed file that does not feed the seed and is used only for the agreement check (M10, M15, M14, A10, A21, HAS25). |
| Holm correction | A step-down adjustment of p-values for several tests, controlling the chance of any false positive (Holm, 1979). |
| Historical Data | A Source label for numbers from the organisation's own past projects. None has been collected. |
| ILLUSTRATIVE | Marker on the example case: every number is a placeholder, not evidence and not site data. |
| Kappa (Cohen's) | Chance-corrected agreement of two coders on categories (Cohen, 1960). Planned for the factor-to-risk mapping (Appendix G); not computed. |
| Kendall's W | Coefficient of concordance of several rankings (0 = no agreement, 1 = complete). |
| Library | The 46 candidate masonry delay risks (Appendix B). |
| Literature | A Source label for a value taken from a published paper. |
| Literature tier | The labelled ordinal position (1 to 5) given to a risk from the literature seed when no numbers are entered; an Assumption, shown as a grey dashed chip, not counted in level totals. |
| Mapping | The assignment of a survey factor to a library risk: direct, related or none. |
| Matrix (5 x 5) | A grid of probability class by impact class whose cells are given a level by the product of the classes. |
| Monte Carlo | Repeated random sampling of risk occurrence and delay to build a distribution of project duration. Offered only as an optional layer on entered numbers; it is not used on survey values. |
| P90 | The duration not exceeded in 90% of simulated runs (decision layer only). |
| PERT | A three-point delay distribution (minimum a, most likely m, maximum b) with mean (a + 4m + b) / 6. |
| Planned duration | The planned working days of the activity; the denominator of the impact fraction. |
| Register | The list of risks of one activity with their numbers, sources, status and (as text) owner, early-warning sign, response type, action and review date. |
| RII | Relative importance index: sum of respondents' weights divided by (highest weight x number of respondents). It measures how important respondents rated a factor, not its probability or days of delay. |
| Rule | A logical condition on facts that flags a library risk as relevant or elevated (Appendix C). |
| Seed (literature seed) | The default ordering of library risks by mean RII from the 5 seed studies; an ordinal starting position and an Assumption, to be replaced by expert and site data. |
| Seed study | One of the 5 surveys (M01, A02, M06, A14, A15) that feed the seed. |
| Source label | The tag on every number: Literature, Historical Data, User Input, Expert Judgment, Derived Calculation or Assumption. |
| User Input | A Source label for a number typed in by the user for the case at hand. |
| WBS | Work breakdown structure; used in the earlier, larger scope (Chapter 1, scope revision), not in the current tool. |
