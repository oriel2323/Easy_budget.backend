import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.business_profile import BusinessProfile
from schemas.reports import PnLReportOut
from services.reporting import build_pnl_report, generate_email_html

router = APIRouter(prefix="/reports", tags=["Reports"])

# --- Email Configuration ---
SMTP_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("MAIL_PORT", 587))
SMTP_USERNAME = os.getenv("MAIL_USERNAME")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM", SMTP_USERNAME)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_email_background(to_email: str, subject: str, html_content: str):
    """Function to be run in background to send email via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Budget AI <{MAIL_FROM}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(MAIL_FROM, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


@router.get("/pnl/{user_id}", response_model=PnLReportOut)
def get_pnl_report(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return build_pnl_report(db, user_id)


@router.post("/pnl/{user_id}/email")
def send_report_email(user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Fetch User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Fetch Profile (for business name in email)
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    
    # 3. Generate Report Data
    try:
        report_data = build_pnl_report(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report data: {str(e)}")

    # 4. Generate HTML
    try:
        # We pass the profile object (or None)
        html_content = generate_email_html(report_data, profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating HTML: {str(e)}")

    # 5. Check Creds & Queue Email
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("WARNING: Email credentials not configured in environment variables.")
        return {"success": True, "message": "Email simulation (creds missing)"}

    subject = f"הדוח הכספי שלך - {profile.business_name if profile else 'Budget AI'}"
    background_tasks.add_task(send_email_background, user.email, subject, html_content)

    return {"success": True, "message": "Email queued for sending"}