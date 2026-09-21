"""
Database connection and session management
Phase 4: PostgreSQL support with connection pooling
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from dotenv import load_dotenv

from .models import Base

load_dotenv()

# Determine database type
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    # PostgreSQL (Production)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core"
    )
    # Connection pooling configuration
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_pre_ping=True,  # Verify connections before using
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )
else:
    # SQLite (Development)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sih26155.db")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print(f"Initializing database...")
    print(f"Database type: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] Database initialized successfully")


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


def check_database_health() -> dict:
    """
    Check database connectivity and health
    
    Returns:
        Health status dictionary
    """
    try:
        db = SessionLocal()
        # Simple query to verify connection
        db.execute("SELECT 1")
        db.close()
        return {
            "status": "healthy",
            "database": "PostgreSQL" if USE_POSTGRES else "SQLite",
            "connection_pool": {
                "size": engine.pool.size() if hasattr(engine.pool, 'size') else None,
                "checked_in": engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else None,
                "checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else None,
            } if USE_POSTGRES else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "PostgreSQL" if USE_POSTGRES else "SQLite"
        }
