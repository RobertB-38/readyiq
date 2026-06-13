"""The adversarial debate pipeline.

Two entry points share the same nodes:
  - build_graph()   : a LangGraph StateGraph (resume line: agent orchestration).
  - run_pipeline()  : a plain sequential runner with the same logic, used by the
                      API and tests so they don't require a langgraph install.

Flow:  retrieve -> bull + bear -> verification gate -> judge
The gate drops ungrounded claims; if a side is left empty it triggers one
re-grounding pass (bounded to avoid loops).
"""
from __future__ import annotations

from typing import Optional

from app.agents.base import LLM, run_rebuttal
from app.agents.bear import run_bear
from app.agents.bull import run_bull
from app.agents.judge import run_judge
from app.guardrails import check_no_invented_numbers, validate_ticker
from app.models import AnalysisResult, Claim, Passage
from app.rag.retriever import Retriever, default_retriever
from app.trace.tracer import Tracer, verify_claims

# Each side fishes its own pond. Queries are written as full SENTENCES, not
# keyword lists — embeddings match similar prose, so a query phrased like the
# answer it seeks retrieves the right passages.
ADVOCATE_QUERY = (
    "The candidate's practice scores are strong across the exam domains, they have "
    "completed the recommended study hours and hands-on labs, and they meet or exceed "
    "the readiness thresholds for this certification."
)
EXAMINER_QUERY = (
    "The candidate has weak practice scores in heavily weighted exam domains, has not "
    "completed key hands-on labs, falls below the readiness threshold or recommended "
    "study hours, and has gaps in the required exam objectives."
)


def _dedupe(passages: list[Passage]) -> list[Passage]:
    """Merge two evidence baskets into one pool, keeping first occurrence by id."""
    seen, out = set(), []
    for p in passages:
        if p.id not in seen:
            seen.add(p.id)
            out.append(p)
    return out


def _gatekeep(claims: list[Claim], evidence: list[Passage], tracer: Tracer, label: str) -> list[Claim]:
    """Apply citation gate + number guardrail to a set of claims (one round, one side)."""
    grounded, uncited = verify_claims(claims, evidence)
    if uncited:
        tracer.log("gate", f"dropped {len(uncited)} uncited claims [{label}]",
                   dropped=[c.text for c in uncited])
    invented = check_no_invented_numbers(grounded, evidence)
    if invented:
        tracer.log("guardrail", f"dropped {len(invented)} invented-number claims [{label}]",
                   dropped=[c.text for c in invented])
        grounded = [c for c in grounded if c not in invented]
    return grounded


def run_pipeline(ticker: str, *, retriever: Optional[Retriever] = None,
                 llm: Optional[LLM] = None) -> AnalysisResult:
    """Run the full tribunal end to end."""
    retriever = retriever or default_retriever()
    tracer = Tracer()

    # Guardrail: reject junk input (must look like a certification code).
    ticker = validate_ticker(ticker)

    # 0. Cache check — make sure this certification is indexed.
    if not retriever.ensure_indexed(ticker):
        raise ValueError(f"No content available for {ticker}.")
    tracer.log("cache", f"{ticker} is indexed and ready")

    # 1. Retrieve — each side fishes its own pond (strengths vs gaps), then we
    #    pool the evidence so the gate, rebuttals, and Judge share one basket.
    advocate_evidence = retriever.retrieve(ticker, query=ADVOCATE_QUERY)
    examiner_evidence = retriever.retrieve(ticker, query=EXAMINER_QUERY)
    evidence = _dedupe(advocate_evidence + examiner_evidence)
    tracer.log("retrieve", "per-agent retrieval",
               advocate=len(advocate_evidence), examiner=len(examiner_evidence),
               pooled=len(evidence))
    if not evidence:
        raise ValueError(f"No content indexed for {ticker}.")

    # 2. ROUND 1 — opening cases (each argues from its own retrieved evidence)
    advocate = run_bull(ticker, advocate_evidence, llm=llm)
    examiner = run_bear(ticker, examiner_evidence, llm=llm)
    advocate.claims = _gatekeep(advocate.claims, evidence, tracer, "advocate/opening")
    examiner.claims = _gatekeep(examiner.claims, evidence, tracer, "examiner/opening")
    tracer.log("round1", "opening cases filed",
               advocate_claims=len(advocate.claims), examiner_claims=len(examiner.claims))

    # 3. ROUND 2 — rebuttals (each agent sees the other's case and responds).
    #    This is the multi-step reasoning core: argument -> counter-argument.
    advocate.rebuttal_summary, adv_reb = run_rebuttal("advocate", ticker, evidence, advocate, examiner, llm=llm)
    examiner.rebuttal_summary, exm_reb = run_rebuttal("examiner", ticker, evidence, examiner, advocate, llm=llm)
    advocate.rebuttal_claims = _gatekeep(adv_reb, evidence, tracer, "advocate/rebuttal")
    examiner.rebuttal_claims = _gatekeep(exm_reb, evidence, tracer, "examiner/rebuttal")
    tracer.log("round2", "rebuttals filed",
               advocate_reb=len(advocate.rebuttal_claims), examiner_reb=len(examiner.rebuttal_claims))

    # 4. Judge weighs the full transcript (opening + rebuttals)
    verdict = run_judge(ticker, advocate, examiner, llm=llm)
    tracer.log("judge", f"{verdict.decision} (conf {verdict.confidence:.2f})")

    return AnalysisResult(
        ticker=ticker, advocate=advocate, examiner=examiner, verdict=verdict,
        evidence=evidence, trace=tracer.dump(),
    )


def build_graph():
    """Construct the LangGraph StateGraph. Imported lazily so the rest of the
    app (and tests) don't require langgraph to be installed."""
    from langgraph.graph import END, StateGraph

    from app.orchestration.state import DebateState

    retriever = default_retriever()
    g = StateGraph(DebateState)

    def n_retrieve(s: DebateState) -> DebateState:
        retriever.ensure_indexed(s["ticker"])   # ingest on demand if missing
        ev = retriever.retrieve(s["ticker"], query=f"{s['ticker']} outlook and risks")
        return {"evidence": ev, "trace": [{"node": "retrieve", "count": len(ev)}]}

    def n_bull(s: DebateState) -> DebateState:
        return {"bull": run_bull(s["ticker"], s["evidence"])}

    def n_bear(s: DebateState) -> DebateState:
        return {"bear": run_bear(s["ticker"], s["evidence"])}

    def n_gate(s: DebateState) -> DebateState:
        for case in (s["bull"], s["bear"]):
            case.claims, _ = verify_claims(case.claims, s["evidence"])
        return {"bull": s["bull"], "bear": s["bear"]}

    def n_rebut(s: DebateState) -> DebateState:
        bull, bear, ev = s["bull"], s["bear"], s["evidence"]
        bull.rebuttal_summary, bull_reb = run_rebuttal("bull", s["ticker"], ev, bull, bear)
        bear.rebuttal_summary, bear_reb = run_rebuttal("bear", s["ticker"], ev, bear, bull)
        bull.rebuttal_claims, _ = verify_claims(bull_reb, ev)
        bear.rebuttal_claims, _ = verify_claims(bear_reb, ev)
        return {"bull": bull, "bear": bear}

    def n_judge(s: DebateState) -> DebateState:
        return {"verdict": run_judge(s["ticker"], s["bull"], s["bear"])}

    g.add_node("retrieve", n_retrieve)
    g.add_node("bull", n_bull)
    g.add_node("bear", n_bear)
    g.add_node("gate", n_gate)
    g.add_node("rebut", n_rebut)
    g.add_node("judge", n_judge)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "bull")
    g.add_edge("retrieve", "bear")
    g.add_edge("bull", "gate")
    g.add_edge("bear", "gate")
    g.add_edge("gate", "rebut")
    g.add_edge("rebut", "judge")
    g.add_edge("judge", END)
    return g.compile()
