"""FastAPI surface for TRIBUNAL."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.models import AnalysisResult
from app.orchestration.graph import run_pipeline

app = FastAPI(title="TRIBUNAL — Auditable Adversarial Investment Analyst", version="0.1.0")


class AnalyzeRequest(BaseModel):
    ticker: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/v1/analyze", response_model=AnalysisResult)
def analyze(req: AnalyzeRequest) -> AnalysisResult:
    try:
        return run_pipeline(req.ticker.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        # missing Azure creds, etc.
        raise HTTPException(status_code=503, detail=str(e))
