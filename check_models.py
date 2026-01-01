import google.generativeai as genai
import os

# תדביק כאן את המפתח שלך
genai.configure(api_key="AIzaSyBloq6CSJZSFoTyLy0sRoEYVT5la04PnsI") 

print("מציג רשימת מודלים זמינים...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
except Exception as e:
    print(f"שגיאה בשליפת המודלים: {e}")