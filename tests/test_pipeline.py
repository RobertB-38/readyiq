"""End-to-end pipeline test, fully offline (fixture retriever + fake llm)."""
from app.orchestration.graph import run_pipeline


def test_pipeline_runs_end_to_end(retriever, fake_llm):
    result = run_pipeline("AZ-204", retriever=retriever, llm=fake_llm)

    assert result.ticker == "AZ-204"
    assert result.advocate.stance == "advocate"
    assert result.examiner.stance == "examiner"
    assert result.verdict.decision in {"READY", "ALMOST", "NOT_YET"}
    assert result.trace, "trace must record reasoning steps"


def test_gate_drops_bogus_advocate_claim(retriever, fake_llm):
    """fake_llm gives the Advocate one real + one BOGUS citation; gate must drop it."""
    result = run_pipeline("AZ-204", retriever=retriever, llm=fake_llm)
    cited = {c.citation_id for c in result.advocate.claims}
    assert "BOGUS-ID" not in cited
    assert "AZ-204-cand-1" in cited


def test_uncovered_certification_raises(retriever, fake_llm):
    import pytest
    with pytest.raises(ValueError):
        run_pipeline("AZ-999", retriever=retriever, llm=fake_llm)


def test_multistep_rebuttal_round_runs(retriever, fake_llm):
    """Multi-step reasoning: both sides must produce a rebuttal after opening."""
    result = run_pipeline("AZ-204", retriever=retriever, llm=fake_llm)
    assert result.advocate.rebuttal_summary, "advocate must rebut"
    assert result.examiner.rebuttal_summary, "examiner must rebut"
    assert result.advocate.rebuttal_claims and result.examiner.rebuttal_claims
    nodes = {step["node"] for step in result.trace}
    assert {"round1", "round2"}.issubset(nodes)
