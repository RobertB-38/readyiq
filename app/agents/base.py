"""Shared agent helpers.

Every agent is a function (ticker, evidence, llm) -> structured output.
`llm` defaults to the Foundry-backed chat() but can be injected in tests.
"""
from __future__ import annotations

import json
from typing import Callable, List

from app.models import Passage

# An llm is anything callable as (system, user) -> str.
LLM = Callable[[str, str], str]


def format_evidence(evidence: List[Passage]) -> str:
    """Render retrieved passages with their citation ids for the prompt."""
    return "\n".join(
        f"[{p.id}] ({p.filing} — {p.section}) {p.text}" for p in evidence
    )


def parse_json(raw: str) -> dict:
    """Tolerant JSON parse — models sometimes wrap output in ```json fences."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        raw = raw[4:] if raw.lstrip().startswith("json") else raw
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end + 1]
    return json.loads(raw)


def _default_llm(system: str, user: str) -> str:
    from app.llm import chat
    return chat(system, user)


REBUTTAL_SYSTEM = (
    "You are the {stance} in a certification-readiness tribunal (ReadyIQ), now in the "
    "REBUTTAL round. You have read the opposing side's case about whether the candidate "
    "is ready to sit the exam. Honestly concede any point you cannot refute, then counter "
    "their strongest claims using ONLY the provided passages (exam objectives and the "
    "candidate's practice record). Every claim MUST cite a passage id. Never invent "
    "scores or objectives. "
    'Respond as JSON: {"summary": str, "claims": [{"text": str, "citation_id": str}]}'
)


def run_rebuttal(stance, ticker, evidence, own_case, opponent_case, llm=None):
    """One agent's rebuttal after seeing the opponent's opening case.

    Returns (summary, claims). This is the step that makes the system genuine
    multi-step reasoning rather than two parallel opinions.
    """
    from app.models import Claim  # local import to avoid cycles

    llm = llm or _default_llm
    system = REBUTTAL_SYSTEM.replace("{stance}", stance.upper())
    user = (
        f"Certification: {ticker}\n\nEvidence:\n{format_evidence(evidence)}\n\n"
        f"YOUR opening case: {own_case.summary}\n\n"
        f"OPPONENT'S case: {opponent_case.summary}\n"
        f"OPPONENT'S claims: {[(c.text, c.citation_id) for c in opponent_case.claims]}"
    )
    data = parse_json(llm(system, user))
    return data.get("summary", ""), [Claim(**c) for c in data.get("claims", [])]
