from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    display_order: int
    is_admin: bool
    telegram_id: int | None


class RoleClaimIn(BaseModel):
    name: str


class AuthResult(BaseModel):
    onboarded: bool
    user: UserOut | None = None
