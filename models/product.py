from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)

    # selling price per unit
    price = Column(Numeric(12, 2), nullable=False)

    # average quantity sold per month
    avg_monthly_qty = Column(Integer, nullable=False)

    # direct production cost per unit
    unit_cost = Column(Numeric(12, 2), nullable=False)

    user = relationship("User", back_populates="products")
