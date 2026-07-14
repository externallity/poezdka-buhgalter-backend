from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.telegram_auth import verify_telegram_init_data


class UnclaimedUserError(HTTPException):
    """Возвращается, когда telegram_id ещё не привязан ни к одному участнику —
    и бот, и Mini App в ответ на это должны показать выбор имени."""

    def __init__(self, telegram_id: int):
        super().__init__(status_code=404, detail={"error": "unclaimed", "telegram_id": telegram_id})


@dataclass
class AuthContext:
    telegram_id: int
    source: str  # "bot" | "miniapp"


def resolve_auth_context(
    authorization: str | None = Header(None),
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    telegram_id: int | None = Query(None),
) -> AuthContext:
    """Единая точка входа для двух способов авторизации:
    - бот: Authorization: Bearer <BOT_SHARED_SECRET> + ?telegram_id=... в query
    - Mini App: X-Telegram-Init-Data: <raw initData>, telegram_id достаётся из подписанных данных
    """
    if authorization == f"Bearer {settings.BOT_SHARED_SECRET}":
        if telegram_id is None:
            raise HTTPException(status_code=400, detail="telegram_id query param required for bot auth")
        return AuthContext(telegram_id=telegram_id, source="bot")

    if x_telegram_init_data:
        data = verify_telegram_init_data(
            x_telegram_init_data, settings.TELEGRAM_BOT_TOKEN, settings.INIT_DATA_MAX_AGE_SECONDS
        )
        return AuthContext(telegram_id=int(data["user"]["id"]), source="miniapp")

    raise HTTPException(status_code=401, detail="Missing authentication")


def get_current_user(
    ctx: AuthContext = Depends(resolve_auth_context),
    db: Session = Depends(get_db),
) -> User:
    user = (
        db.query(User)
        .filter(User.telegram_id == ctx.telegram_id, User.trip_id == settings.ACTIVE_TRIP_ID)
        .first()
    )
    if not user:
        raise UnclaimedUserError(ctx.telegram_id)
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


def get_auth(
    ctx: AuthContext = Depends(resolve_auth_context),
    db: Session = Depends(get_db),
) -> tuple[User, str]:
    """Для эндпоинтов, которым нужно знать не только пользователя, но и источник
    вызова (bot/miniapp) — например для проставления Operation.source."""
    user = get_current_user(ctx, db)
    return user, ctx.source
