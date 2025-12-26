from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

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

    cats = db.query(FixedExpenseCategory).order_by(
        FixedExpenseCategory.group, FixedExpenseCategory.sort_order, FixedExpenseCategory.id
    ).all()

    values = db.query(FixedExpense).filter(FixedExpense.user_id == user_id).all()
    by_cat = {v.category_id: v for v in values}

    out = []
    for c in cats:
        v = by_cat.get(c.id)
        out.append(FixedExpenseRowOut(
            category_id=c.id,
            code=c.code,
            label=c.label,
            group=c.group,
            sort_order=c.sort_order,
            monthly_amount=float(v.monthly_amount) if v else 0.0,
        ))
    return out


@router.put("/{user_id}", response_model=dict)
def upsert_fixed_expenses(user_id: int, payload: FixedExpenseUpsertRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cat_ids = [x.category_id for x in payload.items]
    existing_cats = db.query(FixedExpenseCategory.id).filter(FixedExpenseCategory.id.in_(cat_ids)).all()
    existing_cats = {cid for (cid,) in existing_cats}
    missing = [cid for cid in cat_ids if cid not in existing_cats]
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown category_id(s): {missing}")

    existing = db.query(FixedExpense).filter(
        FixedExpense.user_id == user_id,
        FixedExpense.category_id.in_(cat_ids),
    ).all()
    by_cat = {e.category_id: e for e in existing}

    for item in payload.items:
        row = by_cat.get(item.category_id)
        if row:
            row.monthly_amount = item.monthly_amount
        else:
            db.add(FixedExpense(
                user_id=user_id,
                category_id=item.category_id,
                monthly_amount=item.monthly_amount,
            ))

    db.commit()
    return {"success": True}
