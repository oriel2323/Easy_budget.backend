from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class FixedExpense(Base):
    __tablename__ = "fixed_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("fixed_expense_categories.id"), nullable=False, index=True)

    # מותר 0
    monthly_amount = Column(Numeric(12, 2), nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "category_id", name="uq_fixed_expenses_user_category"),
        CheckConstraint("monthly_amount >= 0", name="ck_fixed_expenses_amount_ge0"),
    )

    user = relationship("User", back_populates="fixed_expenses")
    category = relationship("FixedExpenseCategory", back_populates="user_values")
