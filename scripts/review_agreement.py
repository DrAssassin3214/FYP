"""Second-reviewer sample and agreement (Cohen's kappa) for the relevance review.

Why at review time: works judged D are removed from the `work` table, so their title + abstract text is no longer stored. The second
review therefore has to be drawn from works that are still pending (no row in `review` yet), before the first decisions are applied.

  python scripts/review_agreement.py --draw OUTDIR [--share 0.10]
      writes OUTDIR/second_sample.txt (same line format as the review batches, W-id first) and OUTDIR/second_sample_ids.txt
  python scripts/review_agreement.py --score SECOND.tsv FIRST.tsv [--out docs/review_agreement.json]
      SECOND.tsv / FIRST.tsv: `W<id><TAB>K|D<TAB>reason` lines (FIRST may also be data/review_decisions.tsv with a header row).
      prints n, percent agreement, Cohen's kappa with a bootstrap 95% interval, the confusion matrix and the disagreements.
"""
from __future__ import annotations

import argparse
import json
import random
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def read_decisions(path: Path) -> dict[str, str]:
    out = {}
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2 and p[0].startswith("W") and p[1].strip() in ("K", "D"):
            out[p[0]] = p[1].strip()
    return out


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a == "K" for a, _ in pairs) / n
    pb = sum(b == "K" for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def draw(outdir: Path, share: float) -> None:
    import build_literature_db as b
    db = sqlite3.connect(ROOT / "data" / "literature.db")
    pend = db.execute("SELECT w.work_id, w.tier, w.title, w.abstract FROM work w LEFT JOIN review r USING(work_id) "
                      "WHERE r.work_id IS NULL ORDER BY w.work_id").fetchall()
    if not pend:
        print("no pending works")
        return
    k = max(10, round(share * len(pend)))
    pick = sorted(random.Random(20261012).sample(pend, min(k, len(pend))))
    rx = list(b.STRONG_RX.values())
    lines = []
    for w, tier, title, ab in pick:
        if tier == 1:
            lines.append(f"{w}|{title[:115]}")
        else:
            sn = ""
            for r in rx:
                m = r.search(ab)
                if m:
                    sn = ab[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                    break
            lines.append(f"{w}|T2|{title[:100]}|..{sn}..")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "second_sample.txt").write_text("\n".join(lines), encoding="utf-8")
    (outdir / "second_sample_ids.txt").write_text("\n".join(p[0] for p in pick), encoding="utf-8")
    print(f"drew {len(pick)} of {len(pend)} pending works ({share:.0%}) to {outdir}")


def score(second: Path, first: Path, out: Path | None) -> None:
    a, b = read_decisions(first), read_decisions(second)
    ids = sorted(set(a) & set(b))
    if len(ids) < 10:
        print("fewer than 10 works judged by both reviewers; no kappa reported")
        return
    pairs = [(a[i], b[i]) for i in ids]
    k = kappa(pairs)
    rng = random.Random(20261012)
    boots = sorted(kappa([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(2000))
    cm = {f"{x}->{y}": sum(1 for p in pairs if p == (x, y)) for x in "KD" for y in "KD"}
    res = {"n": len(ids), "agreement": sum(x == y for x, y in pairs) / len(pairs), "kappa": k,
           "kappa_ci95": [boots[50], boots[1949]], "first_vs_second": cm,
           "disagreements": [i for i in ids if a[i] != b[i]]}
    print(json.dumps({k_: v for k_, v in res.items() if k_ != "disagreements"}, indent=1), f"\n{len(res['disagreements'])} disagreements")
    if out:
        out.write_text(json.dumps(res, indent=1), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draw")
    ap.add_argument("--share", type=float, default=0.10)
    ap.add_argument("--score", nargs=2, metavar=("SECOND", "FIRST"))
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.draw:
        draw(Path(a.draw), a.share)
    if a.score:
        score(Path(a.score[0]), Path(a.score[1]), Path(a.out) if a.out else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
