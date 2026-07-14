from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.operation import ExpenseCategory, OperationSource, OperationType
from app.schemas.balance import BalanceOut


class OperationCreateIn(BaseModel):
    type: OperationType
    amount: int
    currency: str = "SUM"  # "SUM" | "RUB"
    category: ExpenseCategory | None = None
    comment: str | None = None
    user_id: int | None = None  # для админа: пополнение/расход за другого участника


class OperationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: OperationType
    amount: int
    category: ExpenseCategory | None
    comment: str | None
    source: OperationSource
    created_at: datetime


class OperationCreateResult(BaseModel):
    operation: OperationOut
    balance: BalanceOut


class SplitCreateIn(BaseModel):
    amount: int
    participant_user_ids: list[int]
    category: ExpenseCategory | None = None
    comment: str | None = None


class SplitShareOut(BaseModel):
    user_id: int
    name: str
    amount: int


class SplitCreateResult(BaseModel):
    operations: list[OperationOut]
    breakdown: list[SplitShareOut]
