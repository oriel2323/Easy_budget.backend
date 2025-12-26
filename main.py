from fastapi import FastAPI
from database import engine, Base
from routers import auth, business_profiles, products
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

#ניסויים
# יצירת טבלאות אם לא קיימות
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # מאפשר לכל אתר (כולל Vercel) לגשת
    allow_credentials=True,
    allow_methods=["*"],  # מאפשר את כל סוגי הבקשות (POST, GET וכו')
    allow_headers=["*"],  # מאפשר את כל סוגי ה-Headers
)

app.include_router(auth.router)
app.include_router(business_profiles.router)
app.include_router(products.router)

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

@app.get("/debug/db")
def debug_db():
    with engine.connect() as conn:
        db = conn.execute(text("select current_database()")).scalar()
        schema = conn.execute(text("select current_schema()")).scalar()
        cnt = conn.execute(text("select count(*) from users")).scalar()
    return {"database": db, "schema": schema, "users_count": cnt}

