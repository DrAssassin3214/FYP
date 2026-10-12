"""Substitutes {{T:file}} placeholders in report/scripts/tpl/*.tpl.md with generated tables and writes report/chapters/03_*.md, 04_*.md.
Run ch34_build.py and ch4_tables.py first."""
import re, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]
OUT = R / "scripts" / "out"; TPL = R / "scripts" / "tpl"; CH = R / "chapters"
tiers = (OUT / "tiers.md").read_text(encoding="utf-8").splitlines()
keep = tiers[:2] + [l for l in tiers[2:] if not l.rstrip().endswith("| unresolved |")]
(OUT / "tiers_compact.md").write_text("\n".join(keep) + "\n", encoding="utf-8")
for tpl, name in (("03_methodology.tpl.md", "03_methodology.md"), ("04_secondary_analysis.tpl.md", "04_secondary_analysis.md")):
    t = (TPL / tpl).read_text(encoding="utf-8")
    t = re.sub(r"\{\{T:([^}]+)\}\}", lambda m: (OUT / m.group(1)).read_text(encoding="utf-8").rstrip("\n") + "\n", t)
    assert "{{" not in t
    (CH / name).write_text(t, encoding="utf-8")
    print(name, len(t.split()), "words")
