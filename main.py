from fastapi import FastAPI
from database import engine, Base
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# יצירת טבלאות (למרות שאנחנו משתמשים ב-Alembic, זה לא מזיק)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. הגדרת CORS - מאפשר לפרונטאנד לדבר עם ה-Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. הכללת הראוטרים הקיימים שלך
app.include_router(auth.router)

# --- בדיקות תקינות (Health Checks) ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}

# --- הגשת הפרונטאנד (Static Files) ---

# בודק אם תיקיית static קיימת ומחבר אותה
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    index_path = os.path.join(os.getcwd(), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # אם הגעת לכאן, הקוד יגיד לך מה הוא רואה בתיקייה שלו
    files_in_dir = os.listdir(os.getcwd())
    return {
        "error": "index.html not found",
        "current_directory": os.getcwd(),
        "files_found": files_in_dir
    }