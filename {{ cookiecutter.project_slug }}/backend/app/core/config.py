import logging

logger = logging.getLogger(__name__)

from typing import Literal, Optional

from pydantic_settings import BaseSettings
from pydantic import Field

from pathlib import Path

BASE_DIR: Path = Path(__file_).parent.parent.parent
ENV_FILE: Path = BASE_DIR / ".env.local"

class Settings(BaseSettings):
    # Environment Configuration
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = Field(default="development")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="DEBUG")

    # Logging Configuration
    LOG_DIR: Path = Field(default=BASE_DIR / "logs")
    LOG_FILE_MAX_BYTES: int = Field(default=10 * 1024 * 1024) # 10MB
    LOG_FILE_BACKUP_COUNT: int = Field(default=5)

    {% if cookiecutter.ai_project == 'y' %}
    # LLM Configuration
    LLM_MODEL: Optional[str] = Field(default="gpt-5-nano")
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    {% endif %}

    {% if cookiecutter.use_celery == 'y' %}
    # Redis Configuration
    REDIS_HOST: Optional[str] = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)

    # Celery Configuration
    CELERY_BROKER_URL: Optional[str] = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default="redis://localhost:6379/0")
    {% endif %}

    {% if cookiecutter.use_supabase == 'y' %}
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None)
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None)
    {% endif %}

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False
        ignore_extra = True
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()

__all__ = ["settings"]