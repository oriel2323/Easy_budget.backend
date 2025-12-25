import os  # תוודא שהשורה הזו קיימת למעלה
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# במקום לרשום את הקישור כאן, אנחנו אומרים לקוד:
# "קח את מה שרשום ב-Variables של Railway תחת השם DATABASE_URL"
DATABASE_URL = os.getenv("DATABASE_URL")

# אם אנחנו במחשב שלך ואין DATABASE_URL, הוא ישתמש ב-SQLite כגיבוי
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./easybudget.db"

# תיקון פורמט עבור Postgres (Railway משתמש ב-postgres:// אבל SQLAlchemy צריכה postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# יצירת המנוע
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()