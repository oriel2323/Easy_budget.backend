from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # one-to-one: לכל user יש business_profile אחד
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    business_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)

    user = relationship("User", back_populates="business_profile")
