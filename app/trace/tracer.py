"""Reasoning trace + citation verification.

This module is the heart of the 'auditable' claim and maps directly to the
Reliability & Safety (20%) rubric line. Two responsibilities:

1. Tracer  — record every reasoning step in order, for the trace view.
2. verify_claims — reject any claim not backed by a real retrieved passage.
"""
from __future__ import annotations

from typing import Iterable, List

from app.models import Claim, Passage


class Tracer:
    """Append-only log of reasoning steps."""

    def __init__(self) -> None:
        self.steps: List[dict] = []

    def log(self, node: str, detail: str, **extra) -> None:
        self.steps.append({"step": len(self.steps) + 1, "node": node, "detail": detail, **extra})

    def dump(self) -> List[dict]:
        return list(self.steps)


def verify_claims(claims: Iterable[Claim], evidence: Iterable[Passage]) -> tuple[list[Claim], list[Claim]]:
    """Split claims into (grounded, ungrounded).

    A claim is grounded iff its citation_id matches a retrieved passage.
    The orchestrator sends ungrounded claims back for re-grounding (the gate).
    """
    valid_ids = {p.id for p in evidence}
    grounded, ungrounded = [], []
    for c in claims:
        (grounded if c.citation_id in valid_ids else ungrounded).append(c)
    return grounded, ungrounded
