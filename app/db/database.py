"""Database utilities for database."""

# /story_app/app/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import SQLALCHEMY_DATABASE_URI

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False,
    pool_size=10,
    max_overflow=5,
    pool_timeout=60,
    pool_recycle=1800
)

async_session_local = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    """Handle init db."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")
