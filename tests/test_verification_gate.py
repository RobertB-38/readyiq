"""The gate is the Reliability & Safety core — test it hardest."""
from app.models import Claim, Passage
from app.trace.tracer import verify_claims


def _passage(pid):
    return Passage(id=pid, text="x", filing="10-K", section="MD&A", company="NVDA")


def test_grounded_claim_passes():
    ev = [_passage("A")]
    grounded, ungrounded = verify_claims([Claim(text="t", citation_id="A")], ev)
    assert len(grounded) == 1 and not ungrounded


def test_ungrounded_claim_is_rejected():
    ev = [_passage("A")]
    grounded, ungrounded = verify_claims([Claim(text="t", citation_id="GHOST")], ev)
    assert not grounded and len(ungrounded) == 1


def test_mixed_claims_split_correctly():
    ev = [_passage("A"), _passage("B")]
    claims = [Claim(text="1", citation_id="A"), Claim(text="2", citation_id="ZZ")]
    grounded, ungrounded = verify_claims(claims, ev)
    assert {c.citation_id for c in grounded} == {"A"}
    assert {c.citation_id for c in ungrounded} == {"ZZ"}
