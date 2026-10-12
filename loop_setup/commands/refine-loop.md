---
description: Run one refinement round (lead -> workstream leaders -> workers -> independent reviewers -> fix -> report) up to 3 rounds
---
You are the LEAD (level 1). You decide; you do not do the detailed work yourself. Subagents cannot launch other subagents, so YOU launch every level.
Argument: $ARGUMENTS (optional focus). Repeat the round below at most 3 times (refine/round-1, round-2, round-3).

ROUND N
1. Create branch `refine/round-N` from main (`git checkout -b refine/round-N main`). Record the baseline: test count, flake8 F/E9 count.
2. LEVEL 2: launch ws-code, ws-data, ws-report, ws-docs-repo IN PARALLEL. Each returns a ranked defect list and a split into independent worker tasks.
3. You merge the plans, drop anything touching a 'Needs human decision' item, order tasks so none share a file, and write the combined plan to docs/refine/round-N-plan.md.
4. LEVEL 3: launch `worker` subagents, one per task (parallel only when files do not overlap). Each commits on the branch.
5. REVIEW: launch reviewer-correctness, reviewer-integrity and reviewer-standards in parallel, with no information from the workers except the branch name. Save their verdicts to docs/refine/round-N-review.md.
6. If any reviewer FAILs: turn each finding into a worker task, run them, then re-run ONLY the failing reviewers. At most 2 fix passes per round.
7. UPDATE: have workers refresh dependent documents (report numbers, README, docs, mentor explanation doc) from the final test output, commit, then `git push -u origin refine/round-N` and open a pull request whose body lists changes, test results and 'Needs human decision' items. Do NOT merge.
8. STOP when all three reviewers PASS and a new round would only find items under 'Needs human decision', or after round 3. Finish with: what changed, test counts before/after, what is left, and what the human must decide. Never claim the project is 'perfect'; say what was checked.
