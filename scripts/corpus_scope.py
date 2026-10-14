"""Scope the literature database to construction delay / risk / productivity evidence and count it by paper type.

Read-only on the database.  Writes docs/audit/corpus_scope.csv (one row per work: scope decision, reason, paper type, themes),
docs/audit/corpus_scope.json (counts) and prints the counts.

Two derived judgements, both made by regular expressions on the TITLE and the stored abstract text, NOT by reading the papers:
  * scope: a work is OUT of scope when it is about AI / machine-learning / data-science METHODS (an AI term in the title, or its
    only theme is the 'expert_rule_ai' theme).  It stays IN scope otherwise.  The database already holds only construction works
    (non-construction records were removed at screening).
  * paper type: first matching rule wins (review, field/time study, questionnaire survey, model or simulation, case study, other).
The counts are indicative.  A work whose type the rules cannot see is 'Other / not classified', not guessed.

    python scripts/corpus_scope.py --db <literature.db>
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AI_TITLE = re.compile(r"\b(machine[- ]learning|deep[- ]learning|neural network\w*|artificial intelligence|\bAI\b|\bML\b|large language model\w*|"
                      r"\bLLMs?\b|generative|random forest|support vector|gradient boost\w*|XGBoost|reinforcement learning|data[- ]driven|"
                      r"big data|data mining|natural language processing|computer vision|digital twin|transfer learning|ensemble learning|"
                      r"genetic algorithm|swarm|metaheuristic)", re.I)
TYPES = [
    ("Literature review", re.compile(r"(systematic|critical|literature|scoping|bibliometric|comprehensive|state[- ]of[- ]the[- ]art)\s+(literature\s+)?(review|survey of the literature|analysis of the literature)|\bmeta[- ]analysis\b|\breview of\b|\ba review\b|\breview paper\b", re.I)),
    ("Field / time study", re.compile(r"time[- ]and[- ]motion|work study|work sampling|activity sampling|productivity measurement|field (study|observation|measurement)|site observation|stopwatch|direct observation", re.I)),
    ("Questionnaire / RII survey", re.compile(r"questionnaire|\bsurvey\b|relative importance|\bRII\b|likert|respondents|interview|perception", re.I)),
    ("Model / simulation", re.compile(r"monte carlo|simulation|stochastic|bayesian|system dynamics|\bPERT\b|fuzzy|\bAHP\b|\bTOPSIS\b|decision support|expert system|framework|\bmodel(l)?ing\b|\bmodel\b|optimi[sz]ation", re.I)),
    ("Case study", re.compile(r"case stud(y|ies)|\bcase of\b|a case\b|project[- ]specific|empirical stud", re.I)),
]


def classify(text: str) -> str:
    for name, pat in TYPES:
        if pat.search(text):
            return name
    return "Other / not classified"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", default=str(ROOT / "docs" / "audit"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    themes: dict[str, set] = {}
    for wid, th in c.execute("select work_id, theme_id from work_theme"):
        themes.setdefault(wid, set()).add(th)
    rows = []
    for wid, doi, title, year, abs_, tier in c.execute("select work_id, doi, title, year, abstract, tier from work order by work_id"):
        th = themes.get(wid, set())
        reason = ""
        if AI_TITLE.search(title or ""):
            reason = "AI / machine-learning method in the title"
        elif th == {"expert_rule_ai"}:
            reason = "only theme is rule-based / expert-system / AI tools"
        text = f"{title or ''}. {abs_ or ''}"
        rows.append({"work_id": wid, "doi": doi or "", "year": year or "", "title": title, "tier": tier, "themes": ";".join(sorted(th)),
                     "scope": "out" if reason else "in", "reason": reason, "paper_type": classify(text)})
    with open(out / "corpus_scope.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    inn = [r for r in rows if r["scope"] == "in"]
    res = {
        "database_works": len(rows), "in_scope": len(inn), "out_of_scope_ai_ml": len(rows) - len(inn),
        "out_reasons": dict(Counter(r["reason"] for r in rows if r["scope"] == "out")),
        "in_scope_by_type": dict(Counter(r["paper_type"] for r in inn).most_common()),
        "in_scope_by_theme": dict(Counter(t for r in inn for t in r["themes"].split(";") if t).most_common()),
        "in_scope_by_year_band": dict(sorted(Counter(("<=2009" if (r["year"] or 0) <= 2009 else "2010-2019" if r["year"] <= 2019 else "2020-2026") for r in inn if r["year"]).items())),
        "method_note": "Scope and paper type are regular-expression judgements on title and abstract, not readings of the papers.",
    }
    (out / "corpus_scope.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
