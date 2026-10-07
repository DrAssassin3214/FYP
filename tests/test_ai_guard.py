import json
from pathlib import Path

import pytest

from app.ai_layer.evidence import EvidenceRecord, EvidenceStore
from app.ai_layer.guard import RiskCandidate, StubLLM, generate_candidates, parse_and_validate, promote
from app.engine.models import DelayDist, Param, RiskStatus, Source

STORE = EvidenceStore([
    EvidenceRecord("M01", "Karthik & Rao (2019). Loss of labour productivity in India", context="India",
                   text="Material shortage and tools delay were the most influential factors on the brick wall site."),
    EvidenceRecord("M03", "Mahamid (2020). Rework and labour productivity", context="Palestine",
                   text="Brick works average rework cost 4.51 percent and productivity 26.2 m2/day."),
    EvidenceRecord("R99", "Unrelated roofing paper", text="Roof truss fabrication."),
])


def llm_out(**over):
    item = {"name": "Material shortage", "category": "Material", "mechanism": "Stock-out halts crews",
            "evidence_ids": ["M01"], "quotes": {"M01": "Material shortage and tools delay were the most influential"}}
    item.update(over)
    return json.dumps({"risks": [item]})


def test_retrieval_is_offline_and_relevant():
    hits = STORE.retrieve("brick wall material shortage", k=2)
    assert hits[0].evidence_id == "M01" and all(h.evidence_id != "R99" for h in hits)
    assert STORE.retrieve("zzz nothing", k=3) == []


def test_valid_candidate_is_still_unverified():
    c = parse_and_validate(llm_out(), {"M01"}, STORE)[0]
    assert c.evidence_ids == ("M01",) and c.issues == [] and c.status == RiskStatus.AI_UNVERIFIED


def test_g1_citation_not_retrieved_or_not_in_store_is_dropped():
    c = parse_and_validate(llm_out(evidence_ids=["M01", "M03", "Z404"]), {"M01"}, STORE)[0]
    assert c.evidence_ids == ("M01",)
    text = " ".join(c.issues)
    assert "M03 was not in the retrieved" in text and "Z404 was not in the retrieved" in text
    c2 = parse_and_validate(llm_out(evidence_ids=["Z404"]), {"Z404"}, STORE)[0]
    assert c2.evidence_ids == () and any("no valid supporting evidence" in i for i in c2.issues)


def test_g2_numbers_from_llm_are_rejected():
    c = parse_and_validate(llm_out(probability=0.35, delay_days=4, cost=90000), {"M01"}, STORE)[0]
    assert set(c.rejected_numeric_fields) == {"probability", "delay_days", "cost"}
    assert any("G2" in i for i in c.issues)


def test_g3_fabricated_quote_flagged():
    c = parse_and_validate(llm_out(quotes={"M01": "Bricks caused 40 percent delay in Pune"}), {"M01"}, STORE)[0]
    assert any("G3" in i for i in c.issues)


def test_unparseable_output_is_reported_not_trusted():
    c = parse_and_validate("Sure! Here are some risks: ...", {"M01"}, STORE)
    assert len(c) == 1 and c[0].evidence_ids == () and "not valid JSON" in c[0].issues[0]


def test_pipeline_keeps_verbatim_audit():
    llm = StubLLM(llm_out())
    out = generate_candidates(llm, "Brick masonry", "brick material shortage", STORE)
    a = out["audit"]
    assert a["model_id"] == "stub-llm-v0" and a["raw_output"] == llm.output
    assert "Use ONLY the evidence below" in a["prompt"] and "M01" in a["retrieved_ids"]
    assert "Do NOT give probabilities" in a["prompt"]


def test_g4_promotion_rules():
    cand = RiskCandidate("Shortage", "Material", "x", ("M01",))
    p = Param(0.3, Source.EXPERT)
    d = DelayDist("pert", 1, 3, 8, source=Source.EXPERT)
    assert promote(cand, "R1", p, d).status == RiskStatus.AI_UNVERIFIED
    assert promote(cand, "R1", p, d, user_confirmed=True).status == RiskStatus.EXPERT_USER
    assert promote(cand, "R1", p, d, user_confirmed=True, literature_supported=True).status == RiskStatus.LITERATURE_SUPPORTED
    with pytest.raises(ValueError):
        promote(cand, "R1", Param(0.3, Source.DERIVED), d)
    with pytest.raises(ValueError):
        promote(RiskCandidate("x", "", "", ()), "R1", p, d, user_confirmed=True, literature_supported=True)


def test_store_rejects_duplicates_and_roundtrips(tmp_path: Path):
    with pytest.raises(ValueError):
        EvidenceStore([EvidenceRecord("A", "x"), EvidenceRecord("A", "y")])
    f = tmp_path / "e.json"
    STORE.to_json(f)
    again = EvidenceStore.from_json(f)
    assert len(again) == len(STORE) and again.get("M03").context == "Palestine"


def test_loads_project_workbook_if_present():
    wb = Path(__file__).resolve().parents[1] / "Literature_Evidence_Package.xlsx"
    if not wb.exists():
        pytest.skip("workbook not present")
    s = EvidenceStore.from_workbook(wb)
    assert "R18" in s and "M03" in s and len(s) >= 40
    assert s.get("M03").text
