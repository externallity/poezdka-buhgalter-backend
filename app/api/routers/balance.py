from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.balance import BalanceOut
from app.services.balance import compute_balance

router = APIRouter(prefix="/api/v1/balance", tags=["balance"])


@router.get("/me", response_model=BalanceOut)
def my_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = compute_balance(db, settings.ACTIVE_TRIP_ID, current_user.id)
    return BalanceOut(user_id=current_user.id, name=current_user.name, **b)


@router.get("", response_model=list[BalanceOut])
def all_balances(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.trip_id == settings.ACTIVE_TRIP_ID)
        .order_by(User.display_order)
        .all()
    )
    result = []
    for u in users:
        b = compute_balance(db, settings.ACTIVE_TRIP_ID, u.id)
        result.append(BalanceOut(user_id=u.id, name=u.name, **b))
    return result
