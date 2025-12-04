from fastapi import FastAPI
from database import engine, Base
from routers import auth

# יצירת טבלאות אם לא קיימות
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "backend working"}
