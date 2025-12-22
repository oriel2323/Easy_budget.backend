from fastapi import FastAPI
from database import engine, Base
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# יצירת טבלאות אם לא קיימות
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "backend working"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}


