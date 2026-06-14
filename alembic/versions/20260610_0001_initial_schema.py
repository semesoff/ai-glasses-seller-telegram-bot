"""initial schema

Revision ID: 20260610_0001
Revises:
Create Date: 2026-06-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260610_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    order_status = postgresql.ENUM("NEW", "CONFIRMED", "DELIVERING", "COMPLETED", name="orderstatus", create_type=False)
    order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=False),
        sa.Column("gender", sa.String(length=40), nullable=False),
        sa.Column("shape", sa.String(length=80), nullable=False),
        sa.Column("frame_material", sa.String(length=80), nullable=False),
        sa.Column("color", sa.String(length=80), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("reviews_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for column in ("brand", "type", "gender", "shape", "frame_material", "color", "price"):
        op.create_index(f"ix_products_{column}", "products", [column])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_orders_telegram_id", "orders", ["telegram_id"])
    op.create_index("ix_orders_product_id", "orders", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_product_id", table_name="orders")
    op.drop_index("ix_orders_telegram_id", table_name="orders")
    op.drop_table("orders")
    for column in ("price", "color", "frame_material", "shape", "gender", "type", "brand"):
        op.drop_index(f"ix_products_{column}", table_name="products")
    op.drop_table("products")
    sa.Enum(name="orderstatus").drop(op.get_bind(), checkfirst=True)
