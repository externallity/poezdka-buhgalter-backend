"""initial schema: trips, users, operations + seed 1 trip and 9 participants

Revision ID: 0001
Revises:
Create Date: 2026-07-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARTICIPANTS = ["Амир", "Юля", "Искан", "Навид", "Лера", "Егор", "Полина", "Поля", "Катя"]


def upgrade() -> None:
    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "exchange_rate_rub_per_1000_sum",
            sa.Numeric(10, 4),
            nullable=False,
            server_default="7",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id"), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("role_claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("trip_id", "name", name="ux_users_trip_name"),
    )
    op.create_index("ix_users_trip_id", "users", ["trip_id"])
    op.create_index(
        "ux_users_trip_telegram",
        "users",
        ["trip_id", "telegram_id"],
        unique=True,
        postgresql_where=sa.text("telegram_id IS NOT NULL"),
    )

    operation_type = sa.Enum("topup", "expense", name="operation_type")
    expense_category = sa.Enum(
        "food", "taxi", "housing", "shopping", "entertainment", "registration", "other",
        name="expense_category",
    )
    operation_source = sa.Enum("bot", "miniapp", "legacy_import", name="operation_source")

    op.create_table(
        "operations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", operation_type, nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("category", expense_category, nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("source", operation_source, nullable=False),
        sa.Column("split_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_operations_trip_id", "operations", ["trip_id"])
    op.create_index("ix_operations_user_id", "operations", ["user_id"])
    op.create_index("ix_operations_split_group_id", "operations", ["split_group_id"])
    op.create_index("ix_operations_deleted_at", "operations", ["deleted_at"])
    op.create_index("ix_operations_created_at", "operations", ["created_at"])
    op.create_index(
        "ix_operations_trip_user_deleted", "operations", ["trip_id", "user_id", "deleted_at"]
    )
    op.create_index("ix_operations_trip_category", "operations", ["trip_id", "category"])

    # Сид: 1 поездка + 9 участников (порядок = текущий PARTICIPANTS в Code.gs,
    # важно для распределения остатка в "Между всеми")
    trips_table = sa.table(
        "trips",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    op.bulk_insert(trips_table, [{"id": 1, "name": "Поездка"}])

    users_table = sa.table(
        "users",
        sa.column("trip_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("display_order", sa.Integer),
        sa.column("is_admin", sa.Boolean),
    )
    op.bulk_insert(
        users_table,
        [
            {"trip_id": 1, "name": name, "display_order": idx + 1, "is_admin": name == "Амир"}
            for idx, name in enumerate(PARTICIPANTS)
        ],
    )


def downgrade() -> None:
    op.drop_table("operations")
    op.drop_table("users")
    op.drop_table("trips")
    sa.Enum(name="operation_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="expense_category").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="operation_source").drop(op.get_bind(), checkfirst=True)
