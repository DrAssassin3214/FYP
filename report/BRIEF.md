# Report writing brief (all chapter writers read this first)

Report: "Delay-Risk Identification and Prioritisation for Brick Masonry Work in Indian Building Projects: An Evidence-Traceable Decision-Support Tool" (working title; the official project title is "Framework for Brickwork Labor-Productivity and Delay-Risk Prediction Using Managerial Factors in Selected Indian Building Projects" - the Chapter 1 scope-revision table explains the difference). B.Tech Civil Engineering final-year project, NICMAR. Target: ~100 printed pages (A4, 11 pt, 1.15 spacing) including appendices.

## Facts you may state (verify against the repo before use; counts are pinned by tests/test_relevance_guard.py)
46 library risks (38 original + 8 added 2026-10-08), 30 seeded, 16 unseeded; 182 seed rows; 11 studies (5 seed: M01, A02, M06, A14, A15; 6 held-out: M10, M15, M14, A10, A21, HAS25); 22 site-fact rules; tests: run pytest for the current number; optional Monte Carlo/EMV decision layer added 2026-10-08 (app/analysis.py) using only user-entered numbers. NO site data was collected; NO expert survey has been run; example case is ILLUSTRATIVE.

## ABSOLUTE integrity rules
1. Never invent papers, authors, numbers, survey results, site data, quotes. Every number comes from a repo file, a script output in analysis/out/, or a command you ran now; cite its path in a table note or "Source:" line.
2. Every number carries a Source label (Literature, Historical Data, User Input, Expert Judgment, Derived Calculation, Assumption).
3. RII is importance, not probability or days. Never say the seed 'validates', 'predicts'. Use 'ordinal starting position', 'agreement check', 'held-out', 'coarse tiers only', 'weak, low-powered, inconclusive'.
4. No 'first', 'novel framework', 'state-of-the-art' claims. No claims of accuracy on real sites.
5. Citations in APA 7th (author-date). Cite ONLY works that appear in the repo evidence corpus (Literature_Evidence_Package.xlsx, Research_Notes/, data/literature_seed.json studies, docs/*.md) or in /tmp/claude-0/-home-claude-fyp/b6e485db-2d31-5ab7-a4a5-10d8b255e54b/scratchpad/committee/methods.md and examiner.md reference lists (e.g. Cox 2008; Duijm 2015; ISO 31000; IEC 31010). If a bibliographic detail (year, volume, pages, DOI) is not in the repo, leave it out rather than guess, and add the item to report/references_unverified.txt. Keep a list of all cited works in report/refs_used_<yourchapter>.txt (APA formatted) for the reference-list assembler.
6. State limitations honestly. Withdrawn wording is listed in docs/Project_Handoff_Summary.md section 8 and docs/Audit_Corrections_2026-10-08.md.
7. Prose is plain, specific, engineer-readable; no filler, no repeated paragraphs, no padding to reach page count; length comes from real content: tables, worked examples, method descriptions, figures with discussion.

## Format
Write Markdown to report/chapters/<NN>_<name>.md (pandoc-flavoured: `#` chapter, `##` section, `###` subsection; pipe tables with captions as `Table: caption` lines BEFORE the table written as bold line "**Table N.M.** caption"; figures as `![Figure N.M. caption](figures/file.png)` with figures copied to report/figures/). Number tables/figures by chapter. Do not hard-code page numbers. No HTML. Run PYTHONPATH=/usr/local/lib/python3.13/dist-packages for python. Do NOT commit; do NOT edit files outside report/ (except you may write new scripts under report/scripts/). Do not use pkill -f.
Reply with: words written, figures/tables made, anything unverifiable.
