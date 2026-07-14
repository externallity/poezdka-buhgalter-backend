from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, resolve_auth_context
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import RoleClaimIn, UserOut

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("/available", response_model=list[UserOut])
def available_roles(db: Session = Depends(get_db)):
    return (
        db.query(User)
        .filter(User.trip_id == settings.ACTIVE_TRIP_ID, User.telegram_id.is_(None))
        .order_by(User.display_order)
        .all()
    )


@router.post("/claim", response_model=UserOut)
def claim_role(
    body: RoleClaimIn,
    ctx: AuthContext = Depends(resolve_auth_context),
    db: Session = Depends(get_db),
):
    # Если этот telegram_id уже закрепил имя ранее — возвращаем его же (идемпотентно),
    # повторный выбор не позволяем (как и в текущем боте — роль закрепляется навсегда).
    existing = (
        db.query(User)
        .filter(User.trip_id == settings.ACTIVE_TRIP_ID, User.telegram_id == ctx.telegram_id)
        .first()
    )
    if existing:
        return existing

    user = (
        db.query(User)
        .filter(User.trip_id == settings.ACTIVE_TRIP_ID, User.name == body.name)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Unknown name")
    if user.telegram_id is not None:
        raise HTTPException(status_code=409, detail="Name already taken")

    from sqlalchemy import func

    user.telegram_id = ctx.telegram_id
    user.role_claimed_at = func.now()
    db.commit()
    db.refresh(user)
    return user
