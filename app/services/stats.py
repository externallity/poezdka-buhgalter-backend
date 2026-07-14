from sqlalchemy import cast, func, Date
from sqlalchemy.orm import Session

from app.models.operation import Operation, OperationType
from app.schemas.stats import CategoryStat, DailyStat, StatsOut


def compute_stats(db: Session, trip_id: int, user_id: int | None) -> StatsOut:
    base = db.query(Operation).filter(
        Operation.trip_id == trip_id,
        Operation.type == OperationType.EXPENSE,
        Operation.deleted_at.is_(None),
    )
    if user_id is not None:
        base = base.filter(Operation.user_id == user_id)

    total_expenses = base.with_entities(func.coalesce(func.sum(Operation.amount), 0)).scalar() or 0
    operations_count = base.count()
    average_expense = round(total_expenses / operations_count, 2) if operations_count else 0.0

    by_category_rows = (
        base.with_entities(Operation.category, func.sum(Operation.amount), func.count(Operation.id))
        .group_by(Operation.category)
        .all()
    )
    by_category = [
        CategoryStat(category=cat, total=int(total), count=int(count))
        for cat, total, count in by_category_rows
    ]

    day_col = cast(Operation.created_at, Date)
    by_day_rows = (
        base.with_entities(day_col.label("day"), func.sum(Operation.amount))
        .group_by(day_col)
        .order_by(day_col)
        .all()
    )
    by_day = [DailyStat(day=day, total=int(total)) for day, total in by_day_rows]

    most_expensive_day = max(by_day, key=lambda d: d.total) if by_day else None

    return StatsOut(
        total_expenses=int(total_expenses),
        average_expense=average_expense,
        operations_count=operations_count,
        most_expensive_day=most_expensive_day,
        by_category=by_category,
        by_day=by_day,
    )
