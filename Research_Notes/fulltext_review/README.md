# Full-text reviews of the 24 curated PDFs (2026-10-07)

One note per PDF in `Research_Papers/` (P01-P24), written by a reviewer agent that read the whole text layer (extracted with a PDF text library, because the PDF renderer was not installed on this machine). What this does and does not mean:

* **Read:** every page's text, tables included. **Not read:** figures and charts (marked NC in each note), supplementary files hosted elsewhere, and a few garbled equations.
* The notes copy numbers as printed and list the papers' own inconsistencies (section 6 of each note) without correcting them.
* The notes are agent output. Numbers were not independently re-keyed by a person; the seed check below is the only cross-check made.
* The app loads each note as two evidence records (`FT-Pnn`, `FT-Pnn-N`) with the depth "full text (text layer read; figures not viewed)".

## Seed check (data/literature_seed.json against the paper's own tables)

| Study id | Paper note | Rows checked | Match | Mismatch | Not found |
|---|---|---:|---:|---:|---:|
| M01 | P23 | 28 | 28 | 0 | 0 |
| M06 | P22 | 40 | 40 | 0 | 0 |
| M10 | P13 | 33 | 33 | 0 | 0 |
| M14 | P15 | 23 | 23 | 0 | 0 |
| M15 | P20 | 24 | 24 | 0 | 0 |

Added later the same day (open-access PDFs downloaded with the user's approval, CC BY per OpenAlex, saved in `Research_Papers/6_Ranking_Studies_OpenAccess/`): A10 (P25) 6/6 rows match, A14 (P26) 5/5, A21 (P27) 2/2. The seed metadata for these three said scale "Not recorded"; the papers print 1-5 scales, and A21's respondents (380) were missing from n; `literature_seed.json` was corrected from the papers.

Not covered: A02, A15 and HAS25 could not be downloaded (the publishers' servers answered 403/403/503; no workaround was attempted), so their rows rest on the earlier research notes. M10's two factors without a printed RII in its Table 7 are not in the seed.

## What the 24 papers contain

Besides the five seed-checked papers, P14, P18, P19 and P21 also print factor tables (P19 with RII values); they are not in the seed dataset. Most of the method papers (P01-P12) are about delay prediction models, cost-overrun risk or risk-register methods and contain no masonry or RII data; they are evidence for method design, not for risk probabilities or delays.
