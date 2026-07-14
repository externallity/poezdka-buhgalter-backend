import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OperationType(str, enum.Enum):
    TOPUP = "topup"
    EXPENSE = "expense"


class ExpenseCategory(str, enum.Enum):
    FOOD = "food"
    TAXI = "taxi"
    HOUSING = "housing"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    REGISTRATION = "registration"
    OTHER = "other"


class OperationSource(str, enum.Enum):
    BOT = "bot"
    MINIAPP = "miniapp"
    LEGACY_IMPORT = "legacy_import"


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[OperationType] = mapped_column(
        Enum(OperationType, name="operation_type", values_callable=lambda e: [x.value for x in e])
    )
    amount: Mapped[int] = mapped_column(Integer)
    category: Mapped[ExpenseCategory | None] = mapped_column(
        Enum(ExpenseCategory, name="expense_category", values_callable=lambda e: [x.value for x in e]),
        nullable=True,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[OperationSource] = mapped_column(
        Enum(OperationSource, name="operation_source", values_callable=lambda e: [x.value for x in e])
    )
    split_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    deleted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_operations_trip_user_deleted", "trip_id", "user_id", "deleted_at"),
        Index("ix_operations_trip_category", "trip_id", "category"),
    )
