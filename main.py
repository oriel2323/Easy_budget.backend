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


@app.get("/debug/db")
def debug_db():
    with engine.connect() as conn:
        db = conn.execute(text("select current_database()")).scalar()
        schema = conn.execute(text("select current_schema()")).scalar()
        cnt = conn.execute(text("select count(*) from users")).scalar()
    return {"database": db, "schema": schema, "users_count": cnt}

