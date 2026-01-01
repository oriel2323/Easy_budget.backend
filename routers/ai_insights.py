from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from services.reporting import build_pnl_report # הלוגיקה הקיימת שלך
from services.ai_service import get_ai_recommendations

# כאן השורה הקריטית - וודא שהיא קיימת!
router = APIRouter(prefix="/ai", tags=["AI"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    # 1. מפיקים את הדוח הכספי מהלוגיקה שלך
    pnl_data = build_pnl_report(db, user_id)
    
    # 2. שולחים את הדוח ל-AI לקבלת המלצות
    advice = get_ai_recommendations(pnl_data)
    
    return {"recommendations": advice}