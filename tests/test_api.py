"""API smoke test — /health and /v1/analyze (fixture-backed, no live keys)."""
from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_analyze_unknown_ticker_404():
    r = client.post("/v1/analyze", json={"ticker": "ZZZZ"})
    assert r.status_code == 404
