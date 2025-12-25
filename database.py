from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# קבלת הכתובת ממשתני הסביבה (ב-Railway)
# או ברירת מחדל ל-SQLite (במחשב המקומי)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./easybudget.db")

# תיקון קטן שנדרש לפעמים ב-Railway/Heroku (הם שולחים postgres:// וצריך postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread נחוץ רק ל-SQLite וגורם לקריסה ב-Postgres
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()