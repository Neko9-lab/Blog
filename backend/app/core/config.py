from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BlogForum"
    api_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/blog",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    jwt_secret: str = Field(default="change_me", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 7, validation_alias="REFRESH_TOKEN_EXPIRE_MINUTES")

    rate_limit_window_seconds: int = Field(default=300, validation_alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_max_attempts: int = Field(default=5, validation_alias="RATE_LIMIT_MAX_ATTEMPTS")
    rate_limit_lock_seconds: int = Field(default=900, validation_alias="RATE_LIMIT_LOCK_SECONDS")

    model_config = SettingsConfigDict(env_file=[".env", "../.env"])


settings = Settings()
