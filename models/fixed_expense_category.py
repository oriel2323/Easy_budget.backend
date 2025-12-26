from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class FixedExpenseCategory(Base):
    __tablename__ = "fixed_expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), nullable=False, unique=True, index=True)   # id פנימי יציב
    label = Column(String(255), nullable=False)                          # עברית לתצוגה
    group = Column(String(16), nullable=False, index=True)               # "cogs" / "ga"
    sort_order = Column(Integer, nullable=False, default=0)

    user_values = relationship("FixedExpense", back_populates="category", cascade="all, delete-orphan")
