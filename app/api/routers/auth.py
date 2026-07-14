from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, resolve_auth_context
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import AuthResult, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResult)
def auth_telegram(ctx: AuthContext = Depends(resolve_auth_context), db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.telegram_id == ctx.telegram_id, User.trip_id == settings.ACTIVE_TRIP_ID)
        .first()
    )
    if user:
        return AuthResult(onboarded=True, user=UserOut.model_validate(user))
    return AuthResult(onboarded=False, user=None)
