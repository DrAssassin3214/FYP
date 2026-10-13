# Corpus audit: what the tool cites and what it leaves unused

Date 2026-10-13. Read-only. Nothing in `data/` was changed. Reproduce with
`python scripts/audit_corpus.py --db <literature.db>` (the database lives only on the laptop). Labels: [Certain] counted from a file, [Likely] inference, [Guessing] gap-filling.

## 1. Counts

| Layer | Records | Cited by the tool | Unused |
|---|---:|---:|---:|
| OpenAlex database `literature.db` (laptop only), `work` table | 4,736 | 0 by work id [Certain] | 4,736 by id; about 14 overlap by DOI/title with cited papers [Likely: heuristic match] |
| of which kept after title/abstract review (`review.decision = K`) | 3,975 | 0 | 3,975 |
| Rows screened out, `screening` table | 21,023 total, 16,287 excluded | n/a | n/a |
| Curated records in the repo (workbook, 9 notes files, P1/P2/P3 JSON, registries, 27 full-text notes) | 472 | 53 | 419 |
| Seed studies in `literature_seed.json` | 11 (5 seed, 6 held out) | 11 | 0 |
| **Distinct paper ids cited anywhere in the tool** | **54** | | |

Read the 419 with care: they are not 419 papers. They include 27 `FT-Pnn` plus 27 `FT-Pnn-N` records (one note per PDF, two records each), 46+ P2/P3 modifier and norm rows, and 65 F-, 57 E-, 27 B-, 27 C-records from the method notes. Eight full-text notes belong to seed studies (P13=M10, P15=M14, P20=M15, P22=M06, P23=M01, P25=A10, P26=A14, P27=A21) but are cited under the M/A id, not the FT id. A paper-level count would need a de-duplication table that does not exist yet.

Four corpus sizes now exist: 21,902/5,214, 17,788/3,975, 11,599/3,550 (documents) and 4,736 works / 3,975 kept (the laptop database). The 3,975 matches the second figure only as the "kept" count. The report must pick one; this is still a human decision.

Review depth of the 4,981 reviewed works: all "title + abstract snippet (not full text)". Only 388 have a saved PDF. [Certain]

## 2. Is every risk traceable to a paper?

Yes at the data level. All 46 risks in `risk_library_masonry.json` carry at least one id in `existence_evidence`, and every id resolves to a record in the repo (zero unresolved). [Certain]

Weak spots:
- 7 risks rest on one paper: R-STR, R-SCP, R-CST, R-SOC (all M06, a general-industry survey), R-WAT (A02), R-GOV (M10), R-FIN (A21). [Certain]
- 4 of the 182 seed rows map to no risk. [Certain]
- Citation is shown in the register as ids only; no screen lists "paper → risks it supports". The reverse index is the CSV below.
- 54 papers support between 1 and 21 risks; 12+ papers support exactly one. 

Matrix: `docs/audit/citation_matrix.csv` has 386 edges (risk, paper, channel). Channels: library existence evidence 97, rules 34, mitigation catalogue 117, seed rows direct 108, seed rows related 30. Every edge was copied from a data file; none was inferred.

## 3. Which uncited papers could become seed studies?

The existing rule (`literature_seed.json`, `seed_rule`): an RII survey from India or Sri Lanka, factor table with printed values read from the paper, and a direct mapping to a tool risk. Held to that rule:

| Paper | Verdict | Reason |
|---|---|---|
| P19 Gupta, Hasan, Jain & Jha (2018), J. Constr. Eng. Manage. 144(11) | **Qualifies on method, narrow scope** [Likely] | Full text read. India, RII formula printed, 5-point scale, n = 151 (81 engineers, 70 supervisors), 38 items with RII and rank. Covers site amenities and welfare only, so it can inform a few labour risks, not the whole list. Needs mapping rows, and a second coder to check them. |
| P14 Mahamid 2021, P18 Mahamid 2022, P21 Mahamid | Do not qualify [Certain] | Palestine / Saudi Arabia; mean severity or importance index, not RII (P14, P21 say so themselves). Method precedents only. |
| A11 Soundarya 2025 | Already excluded | Frequency × severity index. |
| P1-23 Karthik & Rao 2019b (masonry labour productivity, India, 38 factors) | Not usable yet | Only the abstract is held. May be the same survey as M01. Needs the PDF. It is the most on-topic RII paper found. |
| W2902417360, W3186524437, W2469417253, W4318224809 (PDFs archived on the laptop) | Possible, unread | Abstracts state RII with Indian or Sri Lankan respondents, but item tables have not been read. |
| W4296838640, W4413884077, W3112920384 (no PDF) | Possible, unread | Indian or Sri Lankan labour-productivity surveys with RII in the abstract. |

The abstract screen (RII + India/Sri Lanka + productivity/delay in title or abstract) returned 53 hits in the database, including 3 already in the seed. This is [Guessing] about fit: an abstract cannot confirm that a table of item values, a scale or a sample size exists. I did not read any of the 53. **I propose only P19 now, and a reading list for the rest.** Adding any study changes the supervisor-owned seed and shifts the rankings, so it needs sign-off and a second-coder check first.

## 4. Plan to use the data in the tool

1. Add `data/citation_map.json` generated from the matrix, plus a test that fails if a risk has no paper or a paper id does not resolve.
2. Add a "Evidence" screen: risk → papers, and paper → risks, from that file.
3. Add a paper-level table (one row per paper, aliases for FT/P/M ids) so counts stop mixing records and papers.
4. Read the PDFs of the 5 archived candidates; for any that pass, add rows as a proposal for the supervisor.
5. Treat the 3,975 title/abstract-reviewed works as a background library: searchable in the Evidence browser (already loaded as `OA-` records when the file is present), but never counted as "cited" unless a risk or rule names them. Do not map works to risks by keyword match; that would manufacture citations.

## 5. Not done / open

- Corpus size to quote in the report.
- Which candidate papers the supervisor accepts.
- The 8 evidence ids that are absent from the workbook resolve only through the notes files.
