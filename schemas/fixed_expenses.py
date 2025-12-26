from pydantic import BaseModel, Field
from typing import Literal, Dict
from decimal import Decimal

Group = Literal["cogs", "ga"]


class FixedExpenseRowOut(BaseModel):
    category_id: int
    code: str
    label: str
    group: Group
    sort_order: int
    monthly_amount: Decimal

    class Config:
        from_attributes = True

class FixedExpenseUpsertRequest(BaseModel):
    # מפתח = code של קטגוריה, ערך = סכום חודשי
    amounts: Dict[str, Decimal] = Field(default_factory=dict)

    # אם תרצה להגביל גם “יותר מדי גדול”
    # אפשר: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
