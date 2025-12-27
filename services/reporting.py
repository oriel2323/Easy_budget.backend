from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.product import Product
from models.fixed_expense import FixedExpense
from models.fixed_expense_category import FixedExpenseCategory


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
