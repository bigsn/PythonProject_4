"""Database engine, session, and initialization."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pythonproject_4.config import get_settings
from pythonproject_4.models import Base

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency: yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (for development / Alembic migration)."""
    Base.metadata.create_all(bind=engine)
