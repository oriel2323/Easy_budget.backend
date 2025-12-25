from pydantic import BaseModel
from typing import Optional


class BusinessProfileBase(BaseModel):
    business_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileUpdate(BusinessProfileBase):
    pass


class BusinessProfileOut(BusinessProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
