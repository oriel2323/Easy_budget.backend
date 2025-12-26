from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_products_user_id_name"),
        CheckConstraint("price > 0", name="ck_products_price_positive"),
        CheckConstraint("avg_monthly_qty > 0", name="ck_products_avg_monthly_qty_positive"),
        CheckConstraint("unit_cost > 0", name="ck_products_unit_cost_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    price = Column(Numeric(12, 2), nullable=False)
    avg_monthly_qty = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)

    user = relationship("User", back_populates="products")
