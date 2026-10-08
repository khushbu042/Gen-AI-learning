# app/embeddings/factory.py
"""
Embedding Provider Factory

Reads EMBEDDING_PROVIDER from settings and returns
the correct provider implementation.

To switch from Gemini to Bedrock Titan:
  Change EMBEDDING_PROVIDER=bedrock in .env
  Zero code changes needed.
"""
from app.embeddings.base import EmbeddingProvider
from app.config.settings import get_settings
import structlog

logger = structlog.get_logger()


def create_embedding_provider() -> EmbeddingProvider:
    """
    Factory function that creates the configured embedding provider.
    Called once at application startup.
    """
    settings = get_settings()
    provider_name = settings.embedding_provider

    logger.info("Creating embedding provider", provider=provider_name)

    if provider_name == "gemini":
        from app.embeddings.providers.gemini_embeddings import (
            GeminiEmbeddingProvider,
        )
        return GeminiEmbeddingProvider()

    elif provider_name == "bedrock":
        # Will be implemented in Phase 7 (AWS deployment)
        raise NotImplementedError(
            "Bedrock embedding provider will be added in Phase 7. "
            "Use EMBEDDING_PROVIDER=gemini for now."
        )

    else:
        raise ValueError(
            f"Unknown embedding provider: '{provider_name}'. "
            f"Supported: ['gemini', 'bedrock']"
        )