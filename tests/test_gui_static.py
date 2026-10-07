"""Static-content checks for the GUI front end (no browser needed)."""
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "gui" / "static"
MOJIBAKE = ("Â", "â€", "Ã")


def test_static_files_are_utf8_without_mojibake():
    for f in STATIC.rglob("*"):
        if f.suffix in (".js", ".css", ".html"):
            text = f.read_bytes().decode("utf-8")
            assert not any(m in text for m in MOJIBAKE), f
    assert '<meta charset="utf-8">' in (STATIC / "index.html").read_text(encoding="utf-8")


def test_load_case_does_not_auto_add_risks():
    js = (STATIC / "js" / "app.js").read_text(encoding="utf-8")
    assert "autoAddPending = true" in js  # explicit fact edits still set it
    load = js[js.index("function loadCase"):js.index("async function downloadFrom")]
    assert "autoAddPending = false" in load and "autoAddPending = true" not in load


def test_honest_wording_in_live_screens():
    live = "".join((STATIC / "js" / n).read_text(encoding="utf-8") for n in
                   ("app.js", "screens/matrix.js", "screens/risks.js", "screens/evidence.js", "screens/report.js"))
    low = live.lower()
    assert "held out for validation" not in low and "predict" not in low
    assert "not a probability" in low and "same rii class is used for both" in low
    assert "raises the probability class by 1" in low
