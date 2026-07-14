from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.stats import StatsOut
from app.services.stats import compute_stats

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/me", response_model=StatsOut)
def my_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return compute_stats(db, settings.ACTIVE_TRIP_ID, current_user.id)


@router.get("/company", response_model=StatsOut)
def company_stats(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return compute_stats(db, settings.ACTIVE_TRIP_ID, user_id=None)
