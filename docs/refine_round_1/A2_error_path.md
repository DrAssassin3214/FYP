# Lead A, worker A2: error-path audit (round 1)

Source: worker report relayed to the root on 2026-10-12 (a Sonnet worker; scratch scripts in `C:\Users\Omkar\AppData\Local\Temp\claude\refine_round_1\A2\`, not in the project). All calls were in-process or through the Flask test client; no server, no network or AI calls. **These are worker findings, not yet re-run by the root** (UNVERIFIED unless noted); the root re-runs each before fixing.

About 410 mutated register cases through all 9 POST routes produced no 500s and no tracebacks; NaN, inf and booleans in p, delay, duration and edges are rejected with field-named messages (earlier items M1, M2, L4, M9 are fixed).

| ID | Sev | Input | What happens | Proposed fix |
|---|---|---|---|---|
| A2-01 | med | analysis case with `simulation.n` 1 to 9 (documented range 1 to 200000) | `IndexError: index -1 is out of bounds` (API 422 with that text; CLI traceback); n=10 works | validate n >= 10 (or handle small n) with a clear message |
| A2-02 | med | `python -m app.cli analyze` with a missing/invalid/empty/UTF-16 file, a folder, `--out` pointing at a file, `simulation:"x"` | raw traceback each time; `run` handles all of these | give `analyze` the same `_load_case` and error handling as `run` |
| A2-03 | med | analysis case with a wrong-type block (`mitigations:5`, `options:5`, `simulation:5`, `constraints:"x"`, bad `evidence_ids`, list as dict key) | TypeError/AttributeError; API 422 with a message that does not name the field | validate block types and name the field (analysis side of known M6) |
| A2-04 | med | register case with `evidence_ids:5` (or `[["a"]]`) inside an incomplete p or delay | TypeError in `run_case`; API 422 without a field name | validate evidence_ids for incomplete blocks too |
| A2-05 | med | `mitigations[0].evidence_ids="D03"` (bare string) | accepted and split into characters `['D','0','3']`; warnings "unknown evidence id 'M'" etc. | reject a bare string like the register path does |
| A2-06 | med | `constraints` with NaN (CLI/Python only) | constraint silently dropped, command AUTHORIZE MITIGATION, no warning | `isfinite` check in `_opt_number` |
| A2-07 | med | `time_to_implement_days` NaN or inf (CLI/Python only) | accepted; `analysis.json` gets bare `NaN`/`Infinity` (invalid JSON) | reject non-finite numbers at parse |
| A2-08 | med | `ld_per_day_after_deadline` 1e308, or delay b=m=1e300 | result holds inf; API turns inf into null with HTTP 200 and command ACCEPT RISK; markdown prints "inf INR" | reject values that overflow, or warn and refuse a command |
| A2-09 | low | analysis `planned_duration_days` 1e308 | analysis: raw numpy ValueError "Too many bins"; register: accepted, all risks Low, no warning | upper bound on planned duration |
| A2-10 | low | register delay with b=m=1e308 | ValueError "expected delay must be a finite number" without the field name | check at parse and name the field |
| A2-11 | low | `direct_cost_if_occurs=5` (bare number), `delay_after=5`, bare `p_after` | silently ignored, no warning | warn that the value was ignored |
| A2-12 | low | `strategy` / `simulation.criterion` set to 0, None, "" | silently replaced by the default | reject or warn |
| A2-13 | low | `cli run` with every risk incomplete and seeded | stdout "7 on the matrix: " with nothing after the colon | print the seeded count / a message |
| A2-14 | low | `POST /api/validate` with `{"case":[1]}`, `null`, `"x"` | HTTP 200, the wrapper is ignored and the whole body is used as the case | reject a non-object `case` |
| A2-15 | low | `facts.required_workers="six"` (known M5) | no warning; appears only in `result.rules.not_evaluable`, not in CLI/exports | surface non-evaluable rules in the exports |
| A2-16 | low | unknown risk id `NOPE-1`, ids differing by case/space (`r-mat`, ` R-MAT`) | accepted as distinct risks; rule flags say R-MAT not in register | normalise or warn on near-duplicate ids |
| A2-17 | low | `p.value` as Arabic-Indic or fullwidth digits, `" 0.5\n"`, `"+0.5"`, `"1_0"` | accepted via `float()` | accept plain ASCII decimals only |
| A2-18 | low | project name with `\r\n## Heading` (known L7) | Markdown heading injected; `impact_bin_edges_source.note` printed raw | strip `\r`/newlines in single-line fields |
| A2-19 | info | `gui/static/js/markdown.js` `cells()` splits on every `|` including `\|` | a cell with a pipe splits in the GUI preview (not verified in a browser) | respect escaped pipes |
| A2-20 | info | JSON number with 4,301+ digits | reported as "not valid JSON" (Python int-digit limit) | clearer message |

Checked and not reproducible: CSV formula injection (common prefixes are neutralised; NBSP/newline/BOM prefixes are not, not tested in Excel), HTML/SVG escaping, duplicate ids, `use_literature_seed` type, impact edges validation, duration 0/negative/NaN, scale (10k risks 1.7 s; 21 MB body 413), path traversal, host-header check. Not tested: browser GUI, `/api/settings` writes, thread safety.

Items 3, 5 and 11 matter for the evidence-integrity rules: input is dropped or mangled silently instead of rejected.
