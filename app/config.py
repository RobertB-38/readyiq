"""Central config. Reads env, picks the model based on APP_MODE.

dev  -> gpt-4o-mini (cheap, for iteration)
demo -> gpt-4o      (highest quality, for the recorded demo)
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_mode: str = os.getenv("APP_MODE", "dev")

    azure_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    deployment_prod: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_PROD", "gpt-4o")
    deployment_dev: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_DEV", "gpt-4o-mini")
    embed_deployment: str = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")

    # Foundry IQ = an Azure AI Search knowledge base. We query its retrieve endpoint.
    search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    search_key: str = os.getenv("AZURE_SEARCH_KEY", "")
    kb_name: str = os.getenv("FOUNDRY_KB_NAME", "sec-filings-kb")
    search_api_version: str = os.getenv("AZURE_SEARCH_API_VERSION", "2025-11-01-preview")

    @property
    def deployment(self) -> str:
        """Model deployment to use for this run."""
        return self.deployment_prod if self.app_mode == "demo" else self.deployment_dev

    @property
    def has_azure(self) -> bool:
        return bool(self.azure_endpoint and self.azure_key)

    @property
    def has_foundry_iq(self) -> bool:
        return bool(self.search_endpoint and self.search_key)


settings = Settings()
