import logging

logger = logging.getLogger(__name__)

from typing import Literal, Optional, List

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

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
