"""add fixed expenses tables

Revision ID: d2782c9b11d8
Revises: 20fdccbbf0d4
Create Date: 2025-12-26 14:24:10.998714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d2782c9b11d8"
down_revision: Union[str, Sequence[str], None] = "20fdccbbf0d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1) create categories table first
    op.create_table(
        "fixed_expense_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("group", sa.String(length=16), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_fixed_expense_categories_code"),
        "fixed_expense_categories",
        ["code"],
        unique=True,
    )
    op.create_index(
        op.f("ix_fixed_expense_categories_group"),
        "fixed_expense_categories",
        ["group"],
        unique=False,
    )
    op.create_index(
        op.f("ix_fixed_expense_categories_id"),
        "fixed_expense_categories",
        ["id"],
        unique=False,
    )

    # 2) seed categories (now the table exists)
    fixed_expense_categories = sa.table(
        "fixed_expense_categories",
        sa.column("code", sa.String),
        sa.column("label", sa.String),
        sa.column("group", sa.String),
        sa.column("sort_order", sa.Integer),
    )

    op.bulk_insert(
        fixed_expense_categories,
        [
            # COGS
            {"code": "office_rent", "label": "שכירות משרד", "group": "cogs", "sort_order": 10},
            {"code": "employees_salary", "label": "משכורת עובדים (עלות מעסיק)", "group": "cogs", "sort_order": 20},
            {"code": "arnona", "label": "ארנונה", "group": "cogs", "sort_order": 30},
            {"code": "utilities", "label": "חשמל, מים, גז", "group": "cogs", "sort_order": 40},
            {"code": "work_software", "label": "תוכנות דיגיטליות לעבודה שוטפת", "group": "cogs", "sort_order": 50},
            {"code": "office_supplies", "label": "ציוד משרדי ו / או ציוד עסקי מתכלה", "group": "cogs", "sort_order": 60},
            # GA
            {"code": "cpa", "label": "רואה חשבון", "group": "ga", "sort_order": 10},
            {"code": "bookkeeping", "label": "הנהלת חשבונות שוטף", "group": "ga", "sort_order": 20},
            {"code": "accounting_software", "label": "תוכנה דיגיטלית להנהלת חשבונות", "group": "ga", "sort_order": 30},
            {"code": "marketing_design", "label": "שיווק - עיצובים גרפיים", "group": "ga", "sort_order": 40},
            {"code": "marketing_digital", "label": "שיווק - פרסום בדיגיטל", "group": "ga", "sort_order": 50},
            {"code": "marketing_print", "label": "פרסום בפרינט", "group": "ga", "sort_order": 60},
            {"code": "website_maintenance", "label": "תחזוקת אתר שוטף", "group": "ga", "sort_order": 70},
            {"code": "business_consulting", "label": "ייעוץ עסקי שוטף", "group": "ga", "sort_order": 80},
            {"code": "phone_internet", "label": "טלפון ואינטרנט", "group": "ga", "sort_order": 90},
            {"code": "insurance_third_party", "label": "ביטוח צד ג'", "group": "ga", "sort_order": 100},
            {"code": "insurance_property", "label": "ביטוח רכוש", "group": "ga", "sort_order": 110},
            {"code": "other_expense", "label": "הוצאה אחרת", "group": "ga", "sort_order": 120},
        ],
    )

    # 3) create fixed_expenses table
    op.create_table(
        "fixed_expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column(
            "monthly_amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.CheckConstraint("monthly_amount >= 0", name="ck_fixed_expenses_amount_ge0"),
        sa.ForeignKeyConstraint(["category_id"], ["fixed_expense_categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "category_id", name="uq_fixed_expenses_user_category"),
    )
    op.create_index(op.f("ix_fixed_expenses_category_id"), "fixed_expenses", ["category_id"], unique=False)
    op.create_index(op.f("ix_fixed_expenses_id"), "fixed_expenses", ["id"], unique=False)
    op.create_index(op.f("ix_fixed_expenses_user_id"), "fixed_expenses", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_fixed_expenses_user_id"), table_name="fixed_expenses")
    op.drop_index(op.f("ix_fixed_expenses_id"), table_name="fixed_expenses")
    op.drop_index(op.f("ix_fixed_expenses_category_id"), table_name="fixed_expenses")
    op.drop_table("fixed_expenses")

    op.drop_index(op.f("ix_fixed_expense_categories_id"), table_name="fixed_expense_categories")
    op.drop_index(op.f("ix_fixed_expense_categories_group"), table_name="fixed_expense_categories")
    op.drop_index(op.f("ix_fixed_expense_categories_code"), table_name="fixed_expense_categories")
    op.drop_table("fixed_expense_categories")
