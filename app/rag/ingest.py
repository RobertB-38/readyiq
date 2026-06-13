"""SEC EDGAR ingestion -> labelled passages ready for indexing."""
from __future__ import annotations
import glob
import os
import re
from typing import List

from app.models import Passage

# Rough markers for the sections that matter most in a debate.
SECTIONS = [
    ("Risk Factors", r"item\s*1a"),
    ("MD&A", r"item\s*7[^a]"),
    ("Business", r"item\s*1[^0-9a]"),
    ("Financials", r"item\s*8"),
]


def clean_html(raw: str) -> str:
    """Strip HTML tags/whitespace from a filing."""
    from bs4 import BeautifulSoup
    text = BeautifulSoup(raw, "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def download_filings(ticker: str, dest: str = "data/filings") -> None:
    """Fetch the latest 10-K and 10-Q from EDGAR."""
    from sec_edgar_downloader import Downloader
    dl = Downloader("TribunalHackathon", "robert.borkar38@gmail.com", dest)
    for form in ("10-K", "10-Q"):
        dl.get(form, ticker, limit=1, download_details=True)


def _primary_docs(ticker: str, dest: str = "data/filings") -> List[str]:
    pat = os.path.join(dest, "sec-edgar-filings", ticker, "*", "*", "primary-document.html")
    return glob.glob(pat)


def load_and_chunk(ticker: str, dest: str = "data/filings",
                   size: int = 1200, overlap: int = 150) -> List[Passage]:
    """Read downloaded filings -> overlapping, section-tagged passages."""
    passages: List[Passage] = []
    for path in _primary_docs(ticker, dest):
        filing = "10-K" if f"{os.sep}10-K{os.sep}" in path else "10-Q"
        text = clean_html(open(path, encoding="utf-8", errors="ignore").read())
        current, start, idx = "General", 0, 0
        while start < len(text):
            body = text[start:start + size]
            low = body.lower()
            for name, pat in SECTIONS:
                if re.search(pat, low):
                    current = name
            idx += 1
            pid = f"{ticker}-{filing}-{current}-p{idx}".replace(" ", "_")
            passages.append(Passage(id=pid, text=body, filing=filing,
                                    section=current, company=ticker,
                                    url="https://www.sec.gov/edgar"))
            start += size - overlap
    return passages
