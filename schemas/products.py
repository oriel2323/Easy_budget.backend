from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    name: str
    price: float
    avg_monthly_qty: int
    unit_cost: float


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    avg_monthly_qty: Optional[int] = None
    unit_cost: Optional[float] = None


class ProductOut(ProductBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
