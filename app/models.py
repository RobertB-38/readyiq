"""Shared data models — the contract every layer agrees on.

ReadyIQ: a certification-readiness tribunal. An Advocate argues a candidate is
ready, an Examiner argues what's missing, a Judge renders a readiness verdict.
"""
from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field


class Passage(BaseModel):
    """A retrieved source passage from the approved knowledge base.

    For ReadyIQ a passage comes from either the exam objectives or the
    candidate's (synthetic) practice record.
    """
    id: str                       # stable citation id
    text: str
    filing: str                   # the certification, e.g. "AZ-204"
    section: str                  # "Exam objectives" | "Candidate record"
    company: str                  # the certification key (scopes retrieval)
    url: str = ""


class Claim(BaseModel):
    """A single assertion an agent makes, bound to its evidence."""
    text: str
    citation_id: str = Field(..., description="id of the Passage backing this claim")


class AgentCase(BaseModel):
    """One side's argument across the debate rounds."""
    stance: Literal["advocate", "examiner"]
    summary: str                       # opening round
    claims: List[Claim] = []           # opening round claims
    rebuttal_summary: str = ""         # rebuttal round (after seeing opponent)
    rebuttal_claims: List[Claim] = []  # rebuttal round claims

    @property
    def all_claims(self) -> List[Claim]:
        return self.claims + self.rebuttal_claims


class Verdict(BaseModel):
    decision: Literal["READY", "ALMOST", "NOT_YET"]
    confidence: float             # 0..1
    rationale: str
    next_step: str = ""           # recommended focus area or next certification
    key_advocate_claims: List[Claim] = []
    key_examiner_claims: List[Claim] = []


class AnalysisResult(BaseModel):
    ticker: str                   # the certification under review (e.g. "AZ-204")
    advocate: AgentCase
    examiner: AgentCase
    verdict: Verdict
    evidence: List[Passage] = []
    trace: List[dict] = []        # ordered reasoning steps
