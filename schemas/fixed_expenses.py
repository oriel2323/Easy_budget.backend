from pydantic import BaseModel, Field
from typing import Optional, Literal

Group = Literal["cogs", "ga"]

class FixedExpenseRowOut(BaseModel):
    category_id: int
    code: str
    label: str
    group: Group
    sort_order: int
    monthly_amount: float

class FixedExpenseUpsertItem(BaseModel):
    category_id: int
    monthly_amount: float = Field(ge=0)

class FixedExpenseUpsertRequest(BaseModel):
    items: list[FixedExpenseUpsertItem]
