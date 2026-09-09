"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .models import Base

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sih26155.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a database session directly (for non-FastAPI contexts)"""
    return SessionLocal()
