from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any

from models.product import Product
from models.fixed_expense import FixedExpense
from models.fixed_expense_category import FixedExpenseCategory
from models.business_profile import BusinessProfile

MONTHS_HE = [
    "ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני",
    "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר",
]
COL_ANNUAL = "שנתי"


def _d(x) -> Decimal:
    # safe Decimal conversion
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))


def _money(x: Decimal) -> Decimal:
    # 2 decimal places
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _repeat_monthly_and_yearly(monthly: Decimal) -> list[Decimal]:
    m = _money(monthly)
    months = [m] * 12
    yearly = _money(m * Decimal(12))
    return months + [yearly]


def _repeat_qty_and_yearly(qty: int) -> list[Decimal]:
    m = Decimal(qty)
    months = [m] * 12
    yearly = m * Decimal(12)
    return months + [yearly]


def build_pnl_report(db: Session, user_id: int):
    # --- Products ---
    products: list[Product] = (
        db.query(Product)
        .filter(Product.user_id == user_id)
        .order_by(Product.id)
        .all()
    )

    # --- Fixed expense categories (always include all categories) ---
    categories: list[FixedExpenseCategory] = (
        db.query(FixedExpenseCategory)
        .order_by(FixedExpenseCategory.group, FixedExpenseCategory.sort_order, FixedExpenseCategory.id)
        .all()
    )

    # --- User fixed expenses (may be missing => 0) ---
    expenses: list[FixedExpense] = (
        db.query(FixedExpense)
        .filter(FixedExpense.user_id == user_id)
        .all()
    )
    expense_by_cat = {e.category_id: e for e in expenses}

    # ---------- Section 1: Quantities ----------
    qty_rows = []
    qty_total_monthly = Decimal(0)

    for p in products:
        qty = int(p.avg_monthly_qty)
        qty_total_monthly += Decimal(qty)
        qty_rows.append(
            {
                "key": f"product_{p.id}_qty",
                "label": p.name,
                "values": _repeat_qty_and_yearly(qty),
            }
        )

    qty_total_row = {
        "key": "total_qty",
        "label": 'סה"כ כמות מוצרים:',
        "values": _repeat_qty_and_yearly(int(qty_total_monthly)),
    }

    # ---------- Section 2: Revenues ----------
    rev_rows = []
    rev_total_monthly = Decimal(0)

    for p in products:
        price = _d(p.price)
        qty = Decimal(int(p.avg_monthly_qty))
        monthly_rev = price * qty
        rev_total_monthly += monthly_rev

        rev_rows.append(
            {
                "key": f"product_{p.id}_revenue",
                "label": p.name,
                "values": _repeat_monthly_and_yearly(monthly_rev),
            }
        )

    rev_total_row = {
        "key": "total_revenue",
        "label": 'סה"כ הכנסה חודשית:',
        "values": _repeat_monthly_and_yearly(rev_total_monthly),
    }

    # ---------- Section 3: Production costs (unit_cost * qty) ----------
    prod_cost_rows = []
    prod_cost_total_monthly = Decimal(0)

    for p in products:
        unit_cost = _d(p.unit_cost)  # allowed 0
        qty = Decimal(int(p.avg_monthly_qty))
        monthly_cost = unit_cost * qty
        prod_cost_total_monthly += monthly_cost

        prod_cost_rows.append(
            {
                "key": f"product_{p.id}_production_cost",
                "label": p.name,
                "values": _repeat_monthly_and_yearly(monthly_cost),
            }
        )

    prod_cost_total_row = {
        "key": "total_production_cost",
        "label": 'סה"כ עלויות ייצור:',
        "values": _repeat_monthly_and_yearly(prod_cost_total_monthly),
    }

    # ---------- Section 4: Fixed expenses - COGS ----------
    fixed_cogs_rows = []
    fixed_cogs_total_monthly = Decimal(0)

    for c in categories:
        if c.group != "cogs":
            continue
        v = expense_by_cat.get(c.id)
        monthly_amount = _d(v.monthly_amount) if v else Decimal(0)
        fixed_cogs_total_monthly += monthly_amount

        fixed_cogs_rows.append(
            {
                "key": c.code,
                "label": c.label,
                "values": _repeat_monthly_and_yearly(monthly_amount),
            }
        )

    fixed_cogs_total_row = {
        "key": "total_fixed_cogs",
        "label": 'סה"כ הוצאות קבועות (עלות המכר)',
        "values": _repeat_monthly_and_yearly(fixed_cogs_total_monthly),
    }

    # ---------- Gross profit ----------
    gross_profit_monthly = rev_total_monthly - (prod_cost_total_monthly + fixed_cogs_total_monthly)
    gross_profit_row = {
        "key": "gross_profit",
        "label": "רווח גולמי",
        "values": _repeat_monthly_and_yearly(gross_profit_monthly),
    }

    # ---------- Section 6: Fixed expenses - GA ----------
    fixed_ga_rows = []
    fixed_ga_total_monthly = Decimal(0)

    for c in categories:
        if c.group != "ga":
            continue
        v = expense_by_cat.get(c.id)
        monthly_amount = _d(v.monthly_amount) if v else Decimal(0)
        fixed_ga_total_monthly += monthly_amount

        fixed_ga_rows.append(
            {
                "key": c.code,
                "label": c.label,
                "values": _repeat_monthly_and_yearly(monthly_amount),
            }
        )

    fixed_ga_total_row = {
        "key": "total_fixed_ga",
        "label": 'סה"כ הנהלה וכלליות:',
        "values": _repeat_monthly_and_yearly(fixed_ga_total_monthly),
    }

    # ---------- Operating profit ----------
    operating_profit_monthly = gross_profit_monthly - fixed_ga_total_monthly
    operating_profit_row = {
        "key": "operating_profit",
        "label": "רווח תפעולי",
        "values": _repeat_monthly_and_yearly(operating_profit_monthly),
    }

    # ---------- Build response sections ----------
    columns = MONTHS_HE + [COL_ANNUAL]

    sections = [
        {"title": "כמות מכירות חודשית", "rows": qty_rows, "total_row": qty_total_row},
        {"title": "הכנסה חודשית", "rows": rev_rows, "total_row": rev_total_row},
        {"title": 'עלות ישירה - עלויות ייצור', "rows": prod_cost_rows, "total_row": prod_cost_total_row},
        {"title": "הוצאות קבועות - עלות המכר", "rows": fixed_cogs_rows, "total_row": fixed_cogs_total_row},
        {"title": "רווח גולמי", "rows": [gross_profit_row], "total_row": None},
        {"title": "הוצאות קבועות - הנהלה וכלליות", "rows": fixed_ga_rows, "total_row": fixed_ga_total_row},
        {"title": "רווח תפעולי", "rows": [operating_profit_row], "total_row": None},
    ]

    # ---------- Yearly summary (values are last column "שנתי") ----------
    yearly = {
        "revenue": _money(rev_total_monthly * Decimal(12)),
        "production_cost": _money(prod_cost_total_monthly * Decimal(12)),
        "fixed_cogs": _money(fixed_cogs_total_monthly * Decimal(12)),
        "gross_profit": _money(gross_profit_monthly * Decimal(12)),
        "fixed_ga": _money(fixed_ga_total_monthly * Decimal(12)),
        "operating_profit": _money(operating_profit_monthly * Decimal(12)),
    }

    yearly_summary = [
        {"key": "yearly_revenue", "label": 'סה"כ הכנסות שנתי', "value": yearly["revenue"]},
        {"key": "yearly_production_cost", "label": 'סה"כ עלויות ייצור שנתי', "value": yearly["production_cost"]},
        {"key": "yearly_fixed_cogs", "label": 'סה"כ הוצאות קבועות (עלות המכר) שנתי', "value": yearly["fixed_cogs"]},
        {"key": "yearly_gross_profit", "label": "רווח גולמי שנתי", "value": yearly["gross_profit"]},
        {"key": "yearly_fixed_ga", "label": 'סה"כ הנהלה וכלליות שנתי', "value": yearly["fixed_ga"]},
        {"key": "yearly_operating_profit", "label": "רווח תפעולי שנתי", "value": yearly["operating_profit"]},
    ]

    return {
        "columns": columns,
        "table_full": {"columns": columns, "sections": sections},
        "table_yearly_summary": yearly_summary,
    }


def generate_email_html(report_data: Dict[str, Any], business_profile: BusinessProfile) -> str:
    """
    יוצר תבנית HTML למייל מתוך נתוני הדוח
    """
    
    def format_currency(val):
        # המרה ל-float לצורך פורמט מחרוזת פייתון סטנדרטי
        return "₪{:,.0f}".format(float(val))

    summary_cards = ""
    # בניית הכרטיסים העליונים (KPIs)
    # המבנה של yearly_summary הוא רשימה של מילונים עם key, label, value (Decimal)
    for item in report_data.get('table_yearly_summary', []):
        val = item['value']
        # צבעים: רווח חיובי = ירוק, הוצאות = אדום עדין
        color = "#10b981" # ירוק ברירת מחדל
        if "expense" in item['key'] or "cost" in item['key'] or "cogs" in item['key']:
            color = "#f43f5e" # אדום
        elif val < 0:
            color = "#ef4444" # אדום חזק להפסד
        
        val_display = format_currency(val)
        
        summary_cards += f"""
        <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; width: 45%; margin-bottom: 10px; display: inline-block; vertical-align: top; box-sizing: border-box; margin-right: 2%;">
            <div style="font-size: 12px; color: #6b7280; text-transform: uppercase; font-weight: bold;">{item['label']}</div>
            <div style="font-size: 18px; font-weight: bold; color: {color}; margin-top: 5px;">{val_display}</div>
        </div>
        """
    
    # בניית טבלת הנתונים ל-HTML
    # המבנה: table_full -> sections -> rows -> values
    table_rows_html = ""
    sections = report_data.get('table_full', {}).get('sections', [])
    
    for section in sections:
        table_rows_html += f"""
        <tr style="background-color: #f3f4f6;">
            <td colspan="3" style="padding: 10px; font-weight: bold; border-bottom: 2px solid #e5e7eb; color: #374151;">{section['title']}</td>
        </tr>
        """
        for row in section['rows']:
            # הערך הראשון הוא ינואר (או ממוצע חודשי בחישובים שלך), האחרון הוא השנתי
            monthly = row['values'][0] 
            yearly = row['values'][-1]
            
            # בדיקה אם זה כמות או כסף
            is_qty = "כמות" in section['title']
            fmt = (lambda x: str(int(x))) if is_qty else format_currency

            table_rows_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #f3f4f6; color: #4b5563;">{row['label']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #f3f4f6; text-align: left;">{fmt(monthly)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #f3f4f6; text-align: left; font-weight: bold;">{fmt(yearly)}</td>
            </tr>
            """
        
        # שורת סיכום למקטע (אם קיימת)
        if section.get('total_row'):
             row = section['total_row']
             monthly = row['values'][0]
             yearly = row['values'][-1]
             
             is_qty = "כמות" in section['title']
             fmt = (lambda x: str(int(x))) if is_qty else format_currency

             table_rows_html += f"""
            <tr style="background-color: #eef2ff;">
                <td style="padding: 8px; border-bottom: 1px solid #c7d2fe; color: #312e81; font-weight: bold;">{row['label']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #c7d2fe; text-align: left; font-weight: bold; color: #312e81;">{fmt(monthly)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #c7d2fe; text-align: left; font-weight: bold; color: #312e81;">{fmt(yearly)}</td>
            </tr>
            """

    # שם העסק
    biz_name = business_profile.business_name if business_profile else "לקוח יקר"

    # תבנית ה-HTML המלאה
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica', 'Arial', sans-serif; background-color: #f9fafb; margin: 0; padding: 0; direction: rtl; text-align: right; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div style="background-color: #f3f4f6; padding: 40px 0;">
            <div class="container">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4f46e5; margin: 0;">Budget AI</h1>
                    <p style="color: #6b7280; margin-top: 5px;">הדוח הפיננסי שלך מוכן</p>
                </div>
                
                <div style="margin-bottom: 20px; background: #f5f7ff; padding: 15px; border-radius: 8px; border-right: 4px solid #4f46e5;">
                    <h2 style="margin: 0; font-size: 18px; color: #1f2937;">שלום {biz_name},</h2>
                    <p style="margin-top: 5px; color: #4b5563;">להלן סיכום התחזית השנתית שיצרת במערכת.</p>
                </div>

                <div style="text-align: center; margin-bottom: 30px;">
                    {summary_cards}
                </div>

                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background-color: #1f2937; color: white;">
                            <th style="padding: 10px; text-align: right;">סעיף</th>
                            <th style="padding: 10px; text-align: left;">חודשי</th>
                            <th style="padding: 10px; text-align: left;">שנתי</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
                
                <div style="margin-top: 40px; text-align: center; color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; padding-top: 20px;">
                    <p>© 2024 Budget AI. כל הזכויות שמורות.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html