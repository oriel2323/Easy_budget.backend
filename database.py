# database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Read DATABASE_URL from environment (Railway/Prod) and allow local SQLite fallback.
DATABASE_URL = os.getenv("DATABASE_URL")

# Prevent silent fallback to SQLite in production-like environments.
# If Railway is running and DATABASE_URL is missing, crash fast with a clear error.
if not DATABASE_URL:
    is_production_like = bool(
        os.getenv("RAILWAY_ENVIRONMENT")  # usually exists on Railway
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("PORT")  # common on hosted envs
    )

    if is_production_like:
        raise RuntimeError(
            "DATABASE_URL is not set in the environment. "
            "Set DATABASE_URL in Railway Variables (use the Railway Postgres connection string)."
        )

    # Local development fallback
    DATABASE_URL = "sqlite:///./easybudget.db"

# Some platforms provide postgres:// but SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False, Postgres must NOT use it.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # helps prevent stale connections on cloud
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
