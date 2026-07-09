from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://panah:panah@localhost:5433/panah"

    secret_key: str = "dev-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24


settings = Settings()
