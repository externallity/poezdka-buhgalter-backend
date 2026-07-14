from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.operation import Operation, OperationType
from app.models.trip import Trip


def compute_balance(db: Session, trip_id: int, user_id: int) -> dict:
    row = db.query(
        func.coalesce(
            func.sum(case((Operation.type == OperationType.TOPUP, Operation.amount), else_=0)), 0
        ).label("topup"),
        func.coalesce(
            func.sum(case((Operation.type == OperationType.EXPENSE, Operation.amount), else_=0)), 0
        ).label("expense"),
    ).filter(
        Operation.trip_id == trip_id,
        Operation.user_id == user_id,
        Operation.deleted_at.is_(None),
    ).one()

    topup_sum, expense_sum = int(row.topup), int(row.expense)
    balance_sum = topup_sum - expense_sum

    trip = db.get(Trip, trip_id)
    rate = float(trip.exchange_rate_rub_per_1000_sum) if trip else 7.0
    balance_rub = round(balance_sum * rate / 1000, 2)

    return {
        "topup_sum": topup_sum,
        "expense_sum": expense_sum,
        "balance_sum": balance_sum,
        "balance_rub": balance_rub,
    }


def sum_to_rub(amount_sum: int, rate_rub_per_1000: float) -> float:
    return round(amount_sum * float(rate_rub_per_1000) / 1000, 2)


def rub_to_sum(amount_rub: int, rate_rub_per_1000: float) -> int:
    return round(amount_rub * 1000 / float(rate_rub_per_1000))
