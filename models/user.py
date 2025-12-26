from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password = Column(String)

    business_profile = relationship(
    "BusinessProfile",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan",)

    products = relationship(
    "Product",
    back_populates="user",
    cascade="all, delete-orphan",)
