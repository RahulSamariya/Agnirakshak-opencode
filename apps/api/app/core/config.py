from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://heatwave:CHANGE_ME@localhost:5432/heatwave_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "Heatwave Early Warning Platform"
    VERSION: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
