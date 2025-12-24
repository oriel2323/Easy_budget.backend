from fastapi import FastAPI
from database import engine, Base
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# יצירת טבלאות (למקרה ש-Alembic לא הריץ הכל)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. הגדרת CORS - חשוב מאוד כדי שהדפדפן יאפשר לאתר לדבר עם ה-Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. הכללת הראוטרים שלך (כמו ה-Auth)
app.include_router(auth.router)

# --- Endpoints של ה-Backend ---

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    # בדיקה שהחיבור לדאטהבייס תקין
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}

# --- ניהול הפרונטאנד (Static Files) ---

# מוצאים את הנתיב המלא לתיקיית static
static_path = os.path.join(os.getcwd(), "static")

# אם התיקייה קיימת, אנחנו "מחברים" אותה לשרת
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# הנתיב הראשי - זה מה שפותח את האתר כשנכנסים ללינק של Railway
@app.get("/")
def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    
    # הודעת שגיאה מפורטת למקרה שהקובץ חסר ב-Railway
    return {
        "status": "backend working", 
        "message": "Frontend file (static/index.html) not found",
        "debug_info": {
            "current_dir": os.getcwd(),
            "static_folder_exists": os.path.exists(static_path),
            "files_in_root": os.listdir(os.getcwd())
        }
    }