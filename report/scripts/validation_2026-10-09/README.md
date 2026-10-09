# Validation and bug testing of 9 October 2026

Scripts v1 to v5 were written for this validation and were run with `python3 -I script.py <output-folder>`. They import the application from a hard-coded repository path (`REPO` at the top of each script); edit it before re-running elsewhere.

- `v1_output.txt`, `v2_output.txt`, `v3_output.txt`, `v4_output.txt`: first runs, on the code before the fixes F1 to F6. (The `v2_results.json` / `v4_results.json` files in this folder are the first-run data; compare with `after_fixes/`.)
- `after_fixes/`: the same scripts re-run on the fixed code. The probe of the CRC32 collision in `v4_edge.py` was changed to expect the refusal added by F5.
- `v1b_p90.py`, `v1c_p90_bias.py`, `v1d_ci.py`: follow-up checks of the two P90 differences (20-million-draw reference, bias over seeds, interval coverage).
- `pytest_run1.txt`: existing suite before the fixes (522 passed, 3 skipped). `pytest_v_final.txt`: after the fixes (554 passed, 3 skipped).
