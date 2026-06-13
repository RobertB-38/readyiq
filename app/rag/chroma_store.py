"""Local vector-store retriever (Chroma). Proves retrieval logic offline.

Same interface as the Foundry IQ backend, so swapping later is a one-line change.
On first use, Chroma downloads a small embedding model (~80 MB).
"""
from __future__ import annotations

from typing import List

from app.models import Passage


class ChromaRetriever:
    def __init__(self, persist_dir: str = "chroma_db", collection: str = "filings"):
        import chromadb
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._col = self._client.get_or_create_collection(collection)

    def is_indexed(self, ticker: str) -> bool:
        if self._col.count() == 0:
            return False
        hit = self._col.get(where={"company": ticker.upper()}, limit=1)
        return bool(hit["ids"])

    def ensure_indexed(self, ticker: str) -> bool:
        ticker = ticker.upper()
        if self.is_indexed(ticker):       # cache hit
            return True
        from app.rag.ingest import download_filings, load_and_chunk
        download_filings(ticker)
        passages = load_and_chunk(ticker)
        if not passages:
            return False
        self._col.upsert(
            ids=[p.id for p in passages],
            documents=[p.text for p in passages],
            metadatas=[{"company": p.company, "filing": p.filing,
                        "section": p.section, "url": p.url} for p in passages],
        )
        return True

    def retrieve(self, ticker: str, query: str, k: int = 6) -> List[Passage]:
        res = self._col.query(query_texts=[query], n_results=k,
                              where={"company": ticker.upper()})
        out: List[Passage] = []
        for pid, doc, meta in zip(res["ids"][0], res["documents"][0], res["metadatas"][0]):
            out.append(Passage(id=pid, text=doc, filing=meta["filing"],
                               section=meta["section"], company=meta["company"],
                               url=meta.get("url", "")))
        return out
