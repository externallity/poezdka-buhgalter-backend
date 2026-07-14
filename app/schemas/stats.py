from datetime import date

from pydantic import BaseModel

from app.models.operation import ExpenseCategory


class CategoryStat(BaseModel):
    category: ExpenseCategory
    total: int
    count: int


class DailyStat(BaseModel):
    day: date
    total: int


class StatsOut(BaseModel):
    total_expenses: int
    average_expense: float
    operations_count: int
    most_expensive_day: DailyStat | None
    by_category: list[CategoryStat]
    by_day: list[DailyStat]
