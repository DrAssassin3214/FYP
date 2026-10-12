# Quality bar for the refinement loop

A round passes only when ALL of these hold. Reviewers mark each PASS/FAIL with evidence.

1. `pytest tests -q`: no failures; no test weakened, deleted or skipped to pass.
2. `flake8 --select=F,E9 app gui tests`: no new findings; no syntax errors.
3. Same input and seed give identical outputs for the engine (golden hash, excluding audit timestamp) unless the change is explained.
4. Every number in the report, README and docs matches a repo file or a command run in this round (test counts, risk/rule/row counts).
5. Withdrawn wording ('validated', 'predicts', 'optimal') does not appear; Source labels present; example marked ILLUSTRATIVE.
6. No invented papers, authors, results or site data; citations only from the evidence corpus; unknowns listed in report/references_unverified.txt.
7. Online data pack: offline falls back to bundled data; a bad download is rejected; the version is recorded in results.
8. Changes are on a refine/round-N branch with a pull request; nothing pushed to main.
9. Open questions for the supervisor are listed, not decided by agents.
10. The mentor explanation document still matches the code.
