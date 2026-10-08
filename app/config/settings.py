# app/config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    """
    Central configuration for the entire application.
    All values come from environment variables or the .env file.
    Nothing is hardcoded.
    """

    # ── Application ───────────────────────────────────────────
    app_name: str = "Document AI Agent"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # ── LLM Provider Selection ────────────────────────────────
    llm_provider: Literal["gemini", "bedrock"] = "gemini"
    embedding_provider: Literal["gemini", "bedrock", "local"] = "gemini"

    # ── Gemini (Development) ──────────────────────────────────
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"

    # ── Amazon Bedrock (Production) ───────────────────────────
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"

    # ── Qdrant ────────────────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "company_documents"
    qdrant_vector_size: int = 768

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"
    session_ttl_seconds: int = 3600

    # ── PostgreSQL ────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://docai_user:docai_password@localhost:5432/docai_db",
        alias="DATABASE_URL",
    )

    # ── Document Processing ───────────────────────────────────
    max_file_size_mb: int = 50
    chunk_size: int = 512
    chunk_overlap: int = 128
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.7

    # ── Agent ─────────────────────────────────────────────────
    agent_max_iterations: int = 5
    agent_timeout_seconds: int = 30

    # ── Logging ───────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Feature Flags ─────────────────────────────────────────
    enable_streaming: bool = True
    enable_citations: bool = True
    enable_conversation_memory: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Created only once for the entire application lifetime.
    """
    return Settings()