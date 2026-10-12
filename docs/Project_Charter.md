# Project Charter: Bricks-ly (v1, 2026-10-08)

**Project.** Delay-risk identification and prioritisation for brick/block masonry in Indian building projects: an evidence-traceable offline decision-support tool. NICMAR University Pune, final-year B.Tech project. Registered title: "Framework for Brickwork Labor-Productivity and Delay-Risk Prediction Using Managerial Factors in Selected Indian Building Projects" (scope revised 2026-09-28; retitle or scope-revision table is the supervisor's decision, see `docs/Audit_Corrections_2026-10-08.md`).
**Supervisor / team:** [to be filled in by the team].

1. **Purpose.** Help a site engineer identify, register and prioritise delay risks for one masonry activity. Every number carries a Source label; published survey evidence (RII) is used only as a labelled ordinal starting point.
2. **Objectives.** (O1) a verified risk library with a documented factor-to-risk mapping and, still to do, second-coder agreement (kappa); (O2) rules, register, 5x5 matrix and exports, implemented and tested; (O3) analysis of how consistent the published RII rankings are, including sensitivity; (O4) software verification now, and later an expert survey and a usability session (real n, reported as obtained).
3. **In scope.** Library (46 risks), site-fact rules (22), register with owner/trigger/response fields, matrix with literature tier, exports, PySide6 wrapper, Windows build, the optional cost/options decision layer that uses only user-entered numbers.
4. **Out of scope.** Labour-productivity models, other activities, cloud/mobile versions, any AI-generated probability, delay or cost, synthetic validation data.
5. **Deliverables.** Code, tests and Windows builds; the ~130-page report with appendices (`report/`); the seed dataset and verification log; the proposed survey instrument (not yet administered); the AI-use declaration.
6. **Integrity rules.** No invented numbers or papers; every number has a Source; AI supplies no numbers; no "validation" or "predicts" claims about the seed; the example stays ILLUSTRATIVE; withdrawn wording stays withdrawn (enforced by `tests/test_relevance_guard.py`).
7. **Status (2026-10-08).** Done: audits, fixes, committee upgrades, guard tests, analysis package, report draft. Open: second coder, expert survey, usability session, site pilot, supervisor decisions (title, corpus count, omitted A14/A10/A21 rows, event/condition tag, risk merges, fully uncoloured seed tier).
8. **Constraints.** No site data; offline operation; purposive survey sample.
9. **Key risks.** Low survey response; supervisor rejects the scope revision; seed changes after mapping review; build problems on target laptops.
10. **Acceptance.** All tests green including guard tests; supervisor sign-off on title, seed display and corpus figure.
11. **Approvals.** Supervisor [signature/date]; team members [signatures/dates].
