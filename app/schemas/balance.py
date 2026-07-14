from pydantic import BaseModel


class BalanceOut(BaseModel):
    user_id: int
    name: str
    topup_sum: int
    expense_sum: int
    balance_sum: int
    balance_rub: float
