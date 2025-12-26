from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.fixed_expense import FixedExpense
from models.fixed_expense_category import FixedExpenseCategory
from schemas.fixed_expenses import FixedExpenseRowOut, FixedExpenseUpsertRequest

router = APIRouter(prefix="/fixed-expenses", tags=["Fixed Expenses"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=list[FixedExpenseRowOut])
def get_fixed_expenses(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cats = (
        db.query(FixedExpenseCategory)
        .order_by(
            FixedExpenseCategory.group,
            FixedExpenseCategory.sort_order,
            FixedExpenseCategory.id,
        )
        .all()
    )

    values = db.query(FixedExpense).filter(FixedExpense.user_id == user_id).all()
    by_cat = {v.category_id: v for v in values}

    out = []
    for c in cats:
        v = by_cat.get(c.id)
        out.append(
            FixedExpenseRowOut(
                category_id=c.id,
                code=c.code,
                label=c.label,
                group=c.group,
                sort_order=c.sort_order,
                monthly_amount=v.monthly_amount if v else 0,
            )
        )
    return out


@router.put("/{user_id}", response_model=list[FixedExpenseRowOut])
def upsert_fixed_expenses(user_id: int, payload: FixedExpenseUpsertRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # אין מה לעדכן
    if not payload.amounts:
        return get_fixed_expenses(user_id, db)

    # 1) לוודא שכל ה-codes קיימים
    codes = list(payload.amounts.keys())
    cats = db.query(FixedExpenseCategory).filter(FixedExpenseCategory.code.in_(codes)).all()
    by_code = {c.code: c for c in cats}
    missing = [code for code in codes if code not in by_code]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown category code(s): {missing}")

    # 2) להביא existing rows של המשתמש לקטגוריות האלה
    cat_ids = [by_code[code].id for code in codes]
    existing = (
        db.query(FixedExpense)
        .filter(
            FixedExpense.user_id == user_id,
            FixedExpense.category_id.in_(cat_ids),
        )
        .all()
    )
    existing_by_cat = {e.category_id: e for e in existing}

    # 3) upsert
    for code, amount in payload.amounts.items():
        cat = by_code[code]

        row = existing_by_cat.get(cat.id)
        if row:
            row.monthly_amount = amount
        else:
            db.add(
                FixedExpense(
                    user_id=user_id,
                    category_id=cat.id,
                    monthly_amount=amount,
                )
            )

    db.commit()

    # מחזיר את כל הרשימה (נוח לסוואגר ולפרונט)
    return get_fixed_expenses(user_id, db)
