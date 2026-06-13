"""Judge agent — weighs both cases and renders a readiness verdict."""
from __future__ import annotations

from typing import Optional

from app.agents.base import LLM, _default_llm, parse_json
from app.models import AgentCase, Claim, Verdict

SYSTEM = (
    "You are the JUDGE in a certification-readiness tribunal (ReadyIQ). You receive an "
    "ADVOCATE case (the candidate is ready) and an EXAMINER case (the candidate is not "
    "yet ready), each containing only verified, source-cited claims drawn from the exam "
    "objectives and the candidate's practice record. Weigh both sides honestly. A weak "
    "score in a heavily-weighted domain, or a domain below the stated readiness floor, "
    "should outweigh several minor strengths. Return a verdict and a single concrete "
    "next step. Respond as JSON: "
    '{"decision": "READY"|"ALMOST"|"NOT_YET", "confidence": 0..1, "rationale": str, '
    '"next_step": str, '
    '"key_advocate_claims": [{"text": str, "citation_id": str}], '
    '"key_examiner_claims": [{"text": str, "citation_id": str}]}'
)


def run_judge(ticker: str, advocate: AgentCase, examiner: AgentCase,
              llm: Optional[LLM] = None) -> Verdict:
    llm = llm or _default_llm
    user = (
        f"Certification: {ticker}\n\n"
        f"=== ADVOCATE (ready) ===\n"
        f"Opening: {advocate.summary}\nClaims: {[ (c.text, c.citation_id) for c in advocate.claims ]}\n"
        f"Rebuttal: {advocate.rebuttal_summary}\nRebuttal claims: "
        f"{[ (c.text, c.citation_id) for c in advocate.rebuttal_claims ]}\n\n"
        f"=== EXAMINER (not yet) ===\n"
        f"Opening: {examiner.summary}\nClaims: {[ (c.text, c.citation_id) for c in examiner.claims ]}\n"
        f"Rebuttal: {examiner.rebuttal_summary}\nRebuttal claims: "
        f"{[ (c.text, c.citation_id) for c in examiner.rebuttal_claims ]}"
    )
    data = parse_json(llm(SYSTEM, user))
    return Verdict(
        decision=data["decision"],
        confidence=float(data.get("confidence", 0.5)),
        rationale=data.get("rationale", ""),
        next_step=data.get("next_step", ""),
        key_advocate_claims=[Claim(**c) for c in data.get("key_advocate_claims", [])],
        key_examiner_claims=[Claim(**c) for c in data.get("key_examiner_claims", [])],
    )
