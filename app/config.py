from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    BOT_SHARED_SECRET: str
    CORS_ORIGINS: str = "*"
    ACTIVE_TRIP_ID: int = 1
    INIT_DATA_MAX_AGE_SECONDS: int = 86400

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
