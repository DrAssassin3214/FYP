#!/usr/bin/env python3
"""Assemble report/chapters/99_references.md from every report/refs_used_*.txt.

Rules: header lines (not starting with a capital letter followed by an author-year pattern) are skipped; entries are
de-duplicated on (first-author surname, year, first 30 letters of the title); of duplicates the longest entry without an
[INCOMPLETE] marker wins; sorted alphabetically by surname (accents folded) then year; entries flagged [INCOMPLETE] by any
writer get a dagger. No bibliographic detail is added or guessed here.
"""
import re
import unicodedata
from pathlib import Path

REP = Path(__file__).resolve().parents[1]
files = sorted(REP.glob("refs_used_*.txt"))
YEAR = re.compile(r"\((\d{4}[a-z]?|n\.d\.)(?:, [^)]*)?\)")


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


entries = {}
stats = {}
for f in files:
    n = 0
    for raw in f.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        m = YEAR.search(line)
        if not line or not m or line.startswith(("References used", "Entries marked")):
            continue
        n += 1
        inc = "[INCOMPLETE]" in line or "not recorded" in line
        clean = line.replace("[INCOMPLETE]", "").strip()
        first = fold(re.split(r"[,&(]", clean, maxsplit=1)[0]).strip()
        sur = re.sub(r"[^a-z]", "", first.split()[0] if first else "")
        after = fold(clean[m.end():])
        title = re.sub(r"[^a-z]", "", after)[:30]
        key = (sur, m.group(1)[:4], title[:18])
        cur = entries.get(key)
        cand = dict(text=clean, inc=inc, src=[f.name])
        if cur is None:
            entries[key] = cand
        else:
            cur["src"].append(f.name)
            cur["inc"] = cur["inc"] and inc  # complete if any writer had it complete
            if (len(clean) > len(cur["text"]) and (not inc or cur["inc"])) or (cur["inc"] and not inc):
                cur["text"] = clean
    stats[f.name] = n

# second-pass merge of near duplicates: same surname+year, and one title is a prefix of the other
keys = sorted(entries)
for i, k in enumerate(keys):
    for k2 in keys[i + 1:]:
        if k in entries and k2 in entries and k[:2] == k2[:2] and (k[2].startswith(k2[2][:10]) or k2[2].startswith(k[2][:10])):
            a, b = entries[k], entries[k2]
            keep, drop = (a, b) if len(a["text"]) >= len(b["text"]) else (b, a)
            keep["src"] += drop["src"]
            keep["inc"] = keep["inc"] and drop["inc"]
            entries[k] = keep
            del entries[k2]

ordered = sorted(entries.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[1]["text"]))
body = ["# References", "",
        "References are in APA 7th edition author-date style, assembled from the lists kept by each chapter writer. Only works that appear in the repository evidence corpus or in the project's methods notes are listed. Where a bibliographic detail (author initials, volume, pages, DOI, edition) is not recorded in the repository it has been left out and not guessed; such entries are marked with a dagger (†) and itemised in `report/references_unverified.txt`. Standards are listed without an edition year where the year is not recorded.", ""]
for k, e in ordered:
    body.append(e["text"] + (" †" if e["inc"] else "") + "")
    body.append("")
(REP / "chapters" / "99_references.md").write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
unv = sum(1 for _, e in ordered if e["inc"])
print(f"files: {stats}\nentries: {len(ordered)} (marked incomplete: {unv}); duplicates merged: {sum(stats.values()) - len(ordered)}")
