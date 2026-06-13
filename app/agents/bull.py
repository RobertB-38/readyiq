"""Advocate agent — strongest evidence-based case that the candidate is READY."""
from __future__ import annotations

from typing import List, Optional

from app.agents.base import LLM, _default_llm, format_evidence, parse_json
from app.models import AgentCase, Claim, Passage

SYSTEM = (
    "You are the ADVOCATE in a certification-readiness tribunal (ReadyIQ). Your ROLE is "
    "to argue, as persuasively and honestly as the evidence allows, that the candidate IS "
    "READY to sit the exam. ALWAYS lead with their strongest evidence: high domain scores, "
    "covered objectives, completed study, and met thresholds. You MAY acknowledge a "
    "weakness only to put it in context or argue it is surmountable before exam day — you "
    "must NEVER conclude the candidate is 'not ready'; deciding the verdict is the Judge's "
    "job, not yours. Stay in role. You may ONLY make claims supported by the provided "
    "passages (exam objectives and the candidate's practice record), and every claim MUST "
    "cite the passage id it relies on. Never invent scores or objectives. "
    'Respond as JSON: {"summary": str, "claims": [{"text": str, "citation_id": str}]}'
)


def run_bull(ticker: str, evidence: List[Passage], llm: Optional[LLM] = None) -> AgentCase:
    """Run the Advocate. (Function name kept as run_bull for orchestration stability.)"""
    llm = llm or _default_llm
    user = f"Certification: {ticker}\n\nEvidence:\n{format_evidence(evidence)}"
    data = parse_json(llm(SYSTEM, user))
    return AgentCase(
        stance="advocate",
        summary=data.get("summary", ""),
        claims=[Claim(**c) for c in data.get("claims", [])],
    )
