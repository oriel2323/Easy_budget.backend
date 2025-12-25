from pydantic import BaseModel, ConfigDict
from typing import Optional


class BusinessProfileBase(BaseModel):
    business_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class BusinessProfileCreate(BusinessProfileBase):
    # כרגע אין שדות חובה, אפשר להשאיר ריק ולהעלות בהמשך
    pass


class BusinessProfileUpdate(BusinessProfileBase):
    pass


class BusinessProfileOut(BusinessProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
