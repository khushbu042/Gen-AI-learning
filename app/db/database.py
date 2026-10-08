# app/db/database.py
"""
PostgreSQL database connection using SQLAlchemy async engine.

We use async SQLAlchemy so database queries never block the event loop.
This is critical for a FastAPI application that needs to handle
many concurrent requests.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import structlog

from app.config.settings import get_settings

logger = structlog.get_logger()

# ── Base class for all database models ───────────────────────
class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this.
    Gives us .metadata for creating/dropping tables.
    """
    pass


# ── Module-level engine and session factory ───────────────────
# These are created once and reused for all requests
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


def get_engine() -> AsyncEngine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            # Connection pool settings
            pool_size=5,          # Keep 5 connections ready
            max_overflow=10,      # Allow 10 more if needed
            pool_timeout=30,      # Wait max 30s for a connection
            pool_recycle=1800,    # Recycle connections every 30 min
            echo=settings.debug,  # Log SQL in debug mode
        )
        logger.info("Database engine created")
    return _engine


def get_session_factory() -> async_sessionmaker:
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


async def check_database_connection() -> tuple[bool, str]:
    """
    Test database connectivity.
    Returns (is_healthy, detail_message)
    Used by the readiness check endpoint.
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "Connected successfully"
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False, str(e)


async def create_all_tables() -> None:
    """
    Create all database tables if they don't exist.
    Called at application startup.
    Safe to call multiple times - won't recreate existing tables.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")


async def close_database() -> None:
    """
    Close database connections gracefully.
    Called at application shutdown.
    """
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")