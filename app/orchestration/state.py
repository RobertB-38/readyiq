"""Shared debate state carried through the LangGraph nodes."""
from __future__ import annotations

from typing import List, Optional, TypedDict

from app.models import AgentCase, Passage, Verdict


class DebateState(TypedDict, total=False):
    ticker: str
    evidence: List[Passage]
    bull: Optional[AgentCase]
    bear: Optional[AgentCase]
    verdict: Optional[Verdict]
    regroundings: int            # how many times the gate sent claims back
    trace: List[dict]
