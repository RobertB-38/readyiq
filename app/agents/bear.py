"""Examiner agent — strongest evidence-based case that the candidate is NOT YET ready."""
from __future__ import annotations

from typing import List, Optional

from app.agents.base import LLM, _default_llm, format_evidence, parse_json
from app.models import AgentCase, Claim, Passage

SYSTEM = (
    "You are the EXAMINER in a certification-readiness tribunal (ReadyIQ). Your ROLE is to "
    "argue, rigorously and honestly, that the candidate is NOT YET READY. ALWAYS lead with "
    "the most decisive gaps: weak scores in heavily-weighted domains, objectives below the "
    "readiness floor, uncovered or shaky topics, and insufficient study hours. You may "
    "acknowledge a genuine strength only to show it does not offset a critical gap — you "
    "must NOT concede overall readiness; deciding the verdict is the Judge's job. Stay in "
    "role. You may ONLY make claims supported by the provided passages (exam objectives and "
    "the candidate's practice record), and every claim MUST cite the passage id it relies "
    "on. Never invent scores or objectives. "
    'Respond as JSON: {"summary": str, "claims": [{"text": str, "citation_id": str}]}'
)


def run_bear(ticker: str, evidence: List[Passage], llm: Optional[LLM] = None) -> AgentCase:
    """Run the Examiner. (Function name kept as run_bear for orchestration stability.)"""
    llm = llm or _default_llm
    user = f"Certification: {ticker}\n\nEvidence:\n{format_evidence(evidence)}"
    data = parse_json(llm(SYSTEM, user))
    return AgentCase(
        stance="examiner",
        summary=data.get("summary", ""),
        claims=[Claim(**c) for c in data.get("claims", [])],
    )
