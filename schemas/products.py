from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    avg_monthly_qty: int = Field(gt=0)
    unit_cost: float = Field(ge=0)  # מותר 0 (שירות/ייעוץ)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    avg_monthly_qty: Optional[int] = Field(default=None, gt=0)
    unit_cost: Optional[float] = Field(default=None, ge=0)  # מותר 0

class ProductOut(ProductBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
