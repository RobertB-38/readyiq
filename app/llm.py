"""Foundry-hosted model client.

The client is created lazily so importing this module never requires live keys
(tests run offline). Call `chat()` to get a completion.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=1)
def _client():
    """Lazily build the Azure OpenAI (Foundry) client."""
    if not settings.has_azure:
        raise RuntimeError(
            "Azure Foundry credentials missing. Set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_API_KEY in .env, or inject a fake llm in tests."
        )
    from openai import AzureOpenAI

    return AzureOpenAI(
        azure_endpoint=settings.azure_endpoint,
        api_key=settings.azure_key,
        api_version=settings.azure_api_version,
    )


def chat(system: str, user: str, temperature: float = 0.2) -> str:
    """Single-turn completion against the Foundry-hosted model."""
    resp = _client().chat.completions.create(
        model=settings.deployment,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""
