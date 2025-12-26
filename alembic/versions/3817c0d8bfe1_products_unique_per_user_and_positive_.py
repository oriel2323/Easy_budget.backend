"""products unique per user and positive checks

Revision ID: 3817c0d8bfe1
Revises: 5529647c72e9
Create Date: 2025-12-26 09:55:09.713342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3817c0d8bfe1"
down_revision: Union[str, Sequence[str], None] = "5529647c72e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER TABLE ADD CONSTRAINT directly -> use batch mode
    with op.batch_alter_table("products", recreate="always") as batch_op:
        # unique product name per user
        batch_op.create_unique_constraint(
            "uq_products_user_id_name",
            ["user_id", "name"],
        )

        # positive values checks
        batch_op.create_check_constraint("ck_products_price_positive", "price > 0")
        batch_op.create_check_constraint("ck_products_qty_positive", "avg_monthly_qty > 0")
        batch_op.create_check_constraint("ck_products_unit_cost_positive", "unit_cost > 0")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("products", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_products_unit_cost_positive", type_="check")
        batch_op.drop_constraint("ck_products_qty_positive", type_="check")
        batch_op.drop_constraint("ck_products_price_positive", type_="check")
        batch_op.drop_constraint("uq_products_user_id_name", type_="unique")
