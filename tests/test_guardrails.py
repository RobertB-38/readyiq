"""Guardrails: input validation + invented-number detection (anti-hallucination)."""
import pytest

from app.guardrails import GuardrailError, check_no_invented_numbers, validate_ticker
from app.models import Claim, Passage


def test_valid_cert_normalised():
    assert validate_ticker(" az-204 ") == "AZ-204"


@pytest.mark.parametrize("bad", ["", "HELLO", "NVDA", "AZ", "azure", "12345"])
def test_invalid_cert_rejected(bad):
    with pytest.raises(GuardrailError):
        validate_ticker(bad)


def _passage(pid, text):
    return Passage(id=pid, text=text, filing="AZ-204", section="Candidate record",
                   company="AZ-204")


def test_invented_number_is_flagged():
    ev = [_passage("A", "Candidate scored 84% on compute.")]
    claims = [Claim(text="Candidate scored 99% on compute.", citation_id="A")]  # 99 not in source
    assert check_no_invented_numbers(claims, ev)


def test_grounded_number_passes():
    ev = [_passage("A", "Candidate scored 84% on compute.")]
    claims = [Claim(text="Compute score was 84%.", citation_id="A")]
    assert not check_no_invented_numbers(claims, ev)
