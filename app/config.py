from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://inventory:inventory@localhost:5432/inventory"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env"}


settings = Settings()
