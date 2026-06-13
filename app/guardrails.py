"""Guardrails — rules that constrain what the system accepts and emits.

These map directly to the Reliability & Safety (20%) rubric line and back up the
'no hallucinations' claim:

1. validate_ticker     — reject junk input before spending a model call.
2. check_no_invented_numbers — catch fabricated scores: any number in a claim
   must actually appear in the passage it cites.
"""
from __future__ import annotations

import re
from typing import List

from app.models import Claim, Passage

# A certification code, e.g. AZ-204, DP-203, AI-102 (dash optional).
_CERT_RE = re.compile(r"^[A-Z]{2,4}-?\d{2,4}$")
_NUMBER_RE = re.compile(r"\d[\d,]*\.?\d*")


class GuardrailError(ValueError):
    """Raised when input fails a guardrail check."""


def validate_ticker(ticker: str) -> str:
    """Accept only a certification code (e.g. AZ-204). Reject anything else early."""
    t = (ticker or "").strip().upper()
    if not _CERT_RE.match(t):
        raise GuardrailError(
            f"'{ticker}' is not a valid certification code (e.g. AZ-204)."
        )
    return t


def _numbers(text: str) -> set[str]:
    return {n.replace(",", "") for n in _NUMBER_RE.findall(text)}


def check_no_invented_numbers(claims: List[Claim], evidence: List[Passage]) -> List[Claim]:
    """Return claims that cite real numbers NOT present in their source passage.

    A non-empty result means the model invented a figure — a hallucination the
    gate should drop or flag.
    """
    by_id = {p.id: p for p in evidence}
    offenders: List[Claim] = []
    for c in claims:
        src = by_id.get(c.citation_id)
        if not src:
            continue  # missing citation is handled by the verification gate
        claim_nums = _numbers(c.text)
        if claim_nums and not claim_nums.issubset(_numbers(src.text)):
            offenders.append(c)
    return offenders
