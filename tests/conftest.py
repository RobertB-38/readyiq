"""Shared fixtures. A fake LLM lets the whole pipeline run offline (no keys)."""
import json

import pytest

from app.rag.retriever import FixtureRetriever


@pytest.fixture
def retriever():
    return FixtureRetriever()


@pytest.fixture
def fake_llm():
    """Returns canned JSON depending on which agent is calling.

    Detects the agent from its system prompt, and cites a REAL fixture passage id
    plus one BOGUS id (to prove the verification gate drops ungrounded claims).
    """
    def _llm(system: str, user: str) -> str:
        if "REBUTTAL" in system:
            cite = "AZ-204-cand-2" if "EXAMINER" in system else "AZ-204-cand-1"
            return json.dumps({
                "summary": "Conceding one point but countering with cited evidence.",
                "claims": [{"text": "Counterpoint stands on the record.",
                            "citation_id": cite}],
            })
        if "JUDGE" in system:
            return json.dumps({
                "decision": "READY",
                "confidence": 0.8,
                "rationale": "All domains clear the readiness threshold.",
                "next_step": "Book the AZ-204 exam; do a light review of monitoring.",
                "key_advocate_claims": [
                    {"text": "Compute and security exceed threshold.",
                     "citation_id": "AZ-204-cand-1"}],
                "key_examiner_claims": [
                    {"text": "Monitoring is the weakest domain.",
                     "citation_id": "AZ-204-cand-2"}],
            })
        if "ADVOCATE" in system:
            return json.dumps({
                "summary": "Strong domain scores show the candidate is ready.",
                "claims": [
                    {"text": "Compute and security scores exceed the threshold.",
                     "citation_id": "AZ-204-cand-1"},
                    {"text": "Made-up perfect-score claim.", "citation_id": "BOGUS-ID"},
                ],
            })
        if "EXAMINER" in system:
            return json.dumps({
                "summary": "Monitoring is the weakest domain.",
                "claims": [
                    {"text": "Monitoring sits near the threshold.",
                     "citation_id": "AZ-204-cand-2"},
                ],
            })
        # Judge
        return json.dumps({
            "decision": "READY",
            "confidence": 0.8,
            "rationale": "All domains clear the readiness threshold.",
            "next_step": "Book the AZ-204 exam; do a light review of monitoring.",
            "key_advocate_claims": [
                {"text": "Compute and security exceed threshold.",
                 "citation_id": "AZ-204-cand-1"}],
            "key_examiner_claims": [
                {"text": "Monitoring is the weakest domain.",
                 "citation_id": "AZ-204-cand-2"}],
        })
    return _llm
