from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20fdccbbf0d4'
down_revision: Union[str, Sequence[str], None] = '3817c0d8bfe1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # שמות אפשריים ישנים (למקרה שכבר נוצרו פעם)
    old_unique = ["uq_products_user_id_name"]
    old_checks = [
        "ck_products_price_positive",
        "ck_products_avg_monthly_qty_positive",
        "ck_products_unit_cost_positive",
        "ck_products_price_gt0",
        "ck_products_qty_gt0",
        "ck_products_unit_cost_gt0",
        "ck_products_unit_cost_ge0",
    ]

    if dialect == "sqlite":
        # לבדוק מה קיים באמת לפני שמנסים drop (כי ב-SQLite זה נבדק רק ב-flush)
        table_sql = bind.execute(
            sa.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
        ).scalar() or ""

        idx_rows = bind.execute(sa.text("PRAGMA index_list('products')")).fetchall()
        existing_indexes = {r[1] for r in idx_rows}  # name נמצא בעמודה 2

        def has_check(name: str) -> bool:
            return name in table_sql

        def has_unique_index(name: str) -> bool:
         return name in existing_indexes

        with op.batch_alter_table("products", recreate="always") as batch_op:
         # למחוק רק אם באמת קיים
            if has_check("ck_products_price_positive"):
                batch_op.drop_constraint("ck_products_price_positive", type_="check")
            if has_check("ck_products_avg_monthly_qty_positive"):
                batch_op.drop_constraint("ck_products_avg_monthly_qty_positive", type_="check")
            if has_check("ck_products_unit_cost_positive"):
                batch_op.drop_constraint("ck_products_unit_cost_positive", type_="check")

            if has_check("ck_products_price_gt0"):
                batch_op.drop_constraint("ck_products_price_gt0", type_="check")
            if has_check("ck_products_qty_gt0"):
                batch_op.drop_constraint("ck_products_qty_gt0", type_="check")
            if has_check("ck_products_unit_cost_ge0"):
                batch_op.drop_constraint("ck_products_unit_cost_ge0", type_="check")

            # unique יכול להופיע כ-index
            if has_unique_index("uq_products_user_id_name"):
                batch_op.drop_constraint("uq_products_user_id_name", type_="unique")

            # עכשיו ליצור את החוקים הנכונים
            batch_op.create_unique_constraint("uq_products_user_id_name", ["user_id", "name"])
            batch_op.create_check_constraint("ck_products_price_gt0", "price > 0")
            batch_op.create_check_constraint("ck_products_qty_gt0", "avg_monthly_qty > 0")
            batch_op.create_check_constraint("ck_products_unit_cost_ge0", "unit_cost >= 0")
        return


    # Postgres (Railway): אפשר DROP ... IF EXISTS ואז ליצור מחדש
    for c in old_checks:
        op.execute(f'ALTER TABLE products DROP CONSTRAINT IF EXISTS "{c}"')
    for u in old_unique:
        op.execute(f'ALTER TABLE products DROP CONSTRAINT IF EXISTS "{u}"')

    op.create_unique_constraint("uq_products_user_id_name", "products", ["user_id", "name"])
    op.create_check_constraint("ck_products_price_gt0", "products", "price > 0")
    op.create_check_constraint("ck_products_qty_gt0", "products", "avg_monthly_qty > 0")
    op.create_check_constraint("ck_products_unit_cost_ge0", "products", "unit_cost >= 0")


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "sqlite":
        with op.batch_alter_table("products", recreate="always") as batch_op:
            for name, typ in [
                ("ck_products_unit_cost_ge0", "check"),
                ("ck_products_qty_gt0", "check"),
                ("ck_products_price_gt0", "check"),
                ("uq_products_user_id_name", "unique"),
            ]:
                try:
                    batch_op.drop_constraint(name, type_=typ)
                except Exception:
                    pass
        return

    op.drop_constraint("ck_products_unit_cost_ge0", "products", type_="check")
    op.drop_constraint("ck_products_qty_gt0", "products", type_="check")
    op.drop_constraint("ck_products_price_gt0", "products", type_="check")
    op.drop_constraint("uq_products_user_id_name", "products", type_="unique")
