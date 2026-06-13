"""Retrieval over the approved certification knowledge base.

Primary backend: Foundry IQ (targets the 'Best use of IQ tools' prize).
Dev fallback: local fixtures so the graph runs end-to-end offline.

The Retriever protocol lets the orchestrator stay backend-agnostic and lets
tests inject a fake.
"""
from __future__ import annotations

from typing import List, Protocol

from app.models import Passage


class Retriever(Protocol):
    def ensure_indexed(self, ticker: str) -> bool:
        """Make sure this certification is in the index.
        Returns True if it is available to query afterwards."""
        ...

    def retrieve(self, ticker: str, query: str, k: int = 6) -> List[Passage]:
        ...


def _doc_kind(fname: str) -> str:
    """Classify a source file as exam objectives vs the candidate's record."""
    f = (fname or "").lower()
    if "objective" in f:
        return "Exam objectives"
    if "candidate" in f:
        return "Candidate record"
    return "Source"


class FoundryIQRetriever:
    """Queries a Foundry IQ knowledge base (Azure AI Search agentic retrieval).

    Calls the knowledge base `retrieve` action with a semantic intent (Minimal
    reasoning effort = direct semantic search, no LLM planning). Maps the
    extracted chunks back into our Passage model so the rest of the pipeline
    (gate, agents, judge, UI) is unchanged.
    """

    def __init__(self) -> None:
        from app.config import settings
        self._endpoint = settings.search_endpoint.rstrip("/")
        self._key = settings.search_key
        self._kb = settings.kb_name
        self._api_version = settings.search_api_version

    def ensure_indexed(self, ticker: str) -> bool:
        # Option A: filings are pre-indexed in the knowledge base via the portal.
        # We can't cheaply per-ticker check, so assume present; retrieve() returns
        # [] if nothing matches, and the pipeline handles that.
        return True

    def retrieve(self, ticker: str, query: str, k: int = 6) -> List[Passage]:
        import json
        import requests

        import time

        url = (f"{self._endpoint}/knowledgebases/{self._kb}/retrieve"
               f"?api-version={self._api_version}")
        body = {"intents": [{"type": "semantic", "search": f"{ticker}: {query}"}]}
        headers = {"api-key": self._key, "Content-Type": "application/json"}

        # Retry on transient 5xx (e.g. 502 right after a reindex) so the demo is robust.
        resp = None
        for attempt in range(4):
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            if resp.status_code < 500:
                break
            time.sleep(2 * (attempt + 1))
        resp.raise_for_status()
        data = resp.json()

        import hashlib

        # references map each chunk's ref_id -> its source file (blobUrl),
        # which tells us whether it's the exam objectives or the candidate record.
        ref_url = {str(r.get("id")): r.get("blobUrl", "")
                   for r in data.get("references", [])}

        passages: List[Passage] = []
        for msg in data.get("response", []):
            for chunk in msg.get("content", []):
                if chunk.get("type") != "text":
                    continue
                try:
                    items = json.loads(chunk["text"])
                except (ValueError, KeyError):
                    continue
                for it in items:
                    content = it.get("content", "")
                    fname = ref_url.get(str(it.get("ref_id", "")), "").rsplit("/", 1)[-1]
                    # Certification scoping: only keep passages whose source file
                    # belongs to the requested cert. Without this, a cert with no
                    # content would return another cert's material mislabeled.
                    if ticker.upper() not in fname.upper():
                        continue
                    # Content-hash id: globally unique + dedupes true duplicates,
                    # so pooling Advocate/Examiner evidence never collides on ref_id.
                    pid = f"{ticker.upper()}-{hashlib.sha1(content.encode()).hexdigest()[:8]}"
                    passages.append(Passage(
                        id=pid,
                        text=content,
                        filing=ticker.upper(),
                        section=_doc_kind(fname),
                        company=ticker.upper(),
                        url="",
                    ))
        return passages[:k]


class FixtureRetriever:
    """Offline retriever with canned AZ-204 passages — for dev/tests/demo dry-runs."""

    _FIXTURES = {
        "AZ-204": [
            Passage(id="AZ-204-obj-1", company="AZ-204", filing="AZ-204",
                    section="Exam objectives",
                    text="AZ-204 readiness guidance: a ready candidate scores 75% or higher "
                         "across all five domains, with no domain below 60%.",
                    url=""),
            Passage(id="AZ-204-cand-1", company="AZ-204", filing="AZ-204",
                    section="Candidate record",
                    text="Candidate L-1001 scored 84% on compute and 83% on security, "
                         "exceeding the 75% readiness threshold, with 26 study hours.",
                    url=""),
            Passage(id="AZ-204-cand-2", company="AZ-204", filing="AZ-204",
                    section="Candidate record",
                    text="Candidate L-1001 scored 76% on monitoring, the weakest domain, "
                         "but still above the readiness threshold.",
                    url=""),
        ]
    }

    def ensure_indexed(self, ticker: str) -> bool:
        # Offline backend: a certification is "indexed" iff we have fixtures for it.
        return ticker.upper() in self._FIXTURES

    def retrieve(self, ticker: str, query: str, k: int = 6) -> List[Passage]:
        return self._FIXTURES.get(ticker.upper(), [])[:k]


def default_retriever() -> Retriever:
    """Pick the backend based on available config.

    Priority: Foundry IQ (required for the contest) -> local Chroma (dev fallback)
    -> Fixture (offline tests).
    """
    import os
    from app.config import settings

    if settings.has_foundry_iq:
        return FoundryIQRetriever()
    if os.getenv("USE_CHROMA") == "1":
        from app.rag.chroma_store import ChromaRetriever
        return ChromaRetriever()
    return FixtureRetriever()
