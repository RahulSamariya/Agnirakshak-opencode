from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://heatwave:heatwave_secret@localhost:5432/heatwave_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "Heatwave Early Warning Platform"
    VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
