import json

from app.ai_layer.explain import check_numbers, numbers_in
from app.ai_layer.guard import StubLLM
from app.service import suggest_risks


def test_number_extraction_ignores_ids():
    nums = [raw for raw, _ in numbers_in("Option O-A with evidence M01 and R08 gives 12.5 days (56%).")]
    assert nums == ["12.5", "56%"]






def test_percent_and_fraction_forms_match():
    trace = {"p": 0.565}
    assert check_numbers("There is a 56.5% chance.", trace) == []
    assert check_numbers("There is a 60% chance.", trace) == ["60%"]




def test_service_suggest_offline_returns_library_and_evidence():
    sug = suggest_risks("Brick masonry", "material shortage brick wall")
    assert sug["mode"] == "offline-retrieval" and sug["evidence"] and any(r["id"] == "R-MAT" for r in sug["library_risks"])


def test_offline_suggest_reaches_the_full_expanded_corpus():
    from pathlib import Path

    if not (Path(__file__).resolve().parents[1] / "Research_Notes" / "A_masonry_india.md").exists():
        return  # research notes not present in this checkout; nothing to assert
    sug = suggest_risks("Brick masonry", "CPWD IS 7272 labour constant mason")
    ids = {r["id"] for r in sug["evidence"]}
    assert ids & {"IS7272-1brick", "CPWD-FPS-superstructure-1brick", "CPWD-FPS-foundation-1brick"}
    lean = suggest_risks("Brick masonry", "lean last planner percent plan complete")
    assert lean["evidence"]


def test_service_suggest_with_llm_is_guarded():
    out = json.dumps({"risks": [{"name": "Brick shortage", "category": "Material", "mechanism": "stock-out",
                                 "evidence_ids": ["M01", "Z9"], "probability": 0.4}]})
    sug = suggest_risks("Brick masonry", "brick material shortage", client=StubLLM(out))
    c = sug["candidates"][0]
    assert sug["mode"] == "llm" and c["status"] == "AI-suggested-unverified"
    assert c["rejected_numeric_fields"] == {"probability": 0.4} and "M01" not in ["Z9"]
    assert sug["audit"]["raw_output"] == out
