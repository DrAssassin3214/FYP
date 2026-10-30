import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("corpus_scope", Path(__file__).resolve().parent.parent / "scripts" / "corpus_scope.py")
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)


def test_ai_title_terms_are_out_of_scope():
    assert cs.AI_TITLE.search("Predicting delay with a hybrid machine learning approach")
    assert cs.AI_TITLE.search("Artificial intelligence in construction management")
    assert not cs.AI_TITLE.search("Causes of delay in brick masonry work in India")


def test_paper_type_rules_first_match_wins():
    assert cs.classify("A systematic literature review of delay causes") == "Literature review"
    assert cs.classify("Questionnaire survey of masonry labour productivity") == "Questionnaire / RII survey"
    assert cs.classify("Time and motion study of bricklaying") == "Field / time study"
    assert cs.classify("Monte Carlo simulation of schedule risk") == "Model / simulation"
    assert cs.classify("Delays in a hospital project") == "Other / not classified"
