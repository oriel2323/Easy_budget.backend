import google.generativeai as genai
import os

# הגדרת המפתח בצורה מאובטחת עבור Railway
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_ai_recommendations(pnl_report: dict):
    """
    מקבל דוח רווח והפסד שנתי ומחזיר המלצות פיננסיות מבוססות AI.
    """
    try:
        # שליפת הסיכום השנתי מתוך הדוח שהופק ב-reporting.py
        summary = pnl_report.get("table_yearly_summary", [])
        
        # טיפול במקרה שבו אין נתונים ב-DB עבור המשתמש
        if not summary:
            return "לא נמצאו נתונים כספיים לניתוח. נא לוודא שהוזנו מוצרים והוצאות במערכת."

        # המרת נתוני הדוח לטקסט קריא עבור המודל
        data_str = "\n".join([f"{item['label']}: {str(item['value'])}" for item in summary])
        
        # אתחול המודל שנמצא זמין בבדיקה (גרסה 2.5 העדכנית)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # בניית הפרומפט בעברית
        prompt = f"""
        אתה יועץ פיננסי מקצועי לעסקים. ניתח את נתוני הרווח והפסד השנתיים הבאים:
        {data_str}
        
        בהתבסס על הנתונים, ספק 3 המלצות מעשיות, קצרות ומקצועיות לשיפור הרווחיות בעברית.
        """
        
        # שליחת הבקשה לגוגל וקבלת התשובה
        response = model.generate_content(prompt)
        
        return response.text

    except Exception as e:
        # הדפסת השגיאה ללוגים של השרת לצורך ניפוי שגיאות (Debug)
        print(f"AI Service Error: {str(e)}")
        return f"מצטערים, חלה שגיאה בתהליך ניתוח הנתונים: {str(e)}"