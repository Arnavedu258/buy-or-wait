from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==========================================================
# PROJECT ROOT
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]


# ==========================================================
# ENTERPRISE SETTINGS
# ==========================================================

class Settings(BaseSettings):
    """
    Immutable application configuration.

    Features
    --------
    • Singleton
    • .env support
    • Type validation
    • Auto directory creation
    • OS independent
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------
    # Application
    # ------------------------------------------------------

    APP_NAME: str = "Buy Or Wait"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    DEBUG: bool = True

    # ------------------------------------------------------
    # Paths
    # ------------------------------------------------------

    ROOT_DIR: Path = ROOT_DIR

    DATASET_DIR: Path = ROOT_DIR / "dataset"

    OUTPUT_FILE: Path = ROOT_DIR / "output.csv"

    REPORT_DIR: Path = ROOT_DIR / "evaluation" / "reports"

    LOG_DIR: Path = ROOT_DIR / "logs"

    # ------------------------------------------------------
    # AI / RAG
    # ------------------------------------------------------

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    EMBEDDING_DIM: PositiveInt = 384

    TOP_K: PositiveInt = 5

    VECTOR_CACHE_SIZE: PositiveInt = 2048

    # ------------------------------------------------------
    # Performance
    # ------------------------------------------------------

    MAX_WORKERS: PositiveInt = 8

    REQUEST_TIMEOUT: PositiveInt = 30

    CACHE_SIZE: PositiveInt = 5000

    # ------------------------------------------------------
    # Finance
    # ------------------------------------------------------

    DEFAULT_CURRENCY: str = "INR"

    MIN_EMERGENCY_MONTHS: PositiveInt = 3

    CONFIDENCE_THRESHOLD: float = Field(
        default=0.75,
        ge=0,
        le=1,
    )

    # ------------------------------------------------------
    # Infrastructure
    # ------------------------------------------------------

    def ensure_directories(self) -> None:
        """Create runtime directories safely."""

        self.REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )


# ==========================================================
# SINGLETON FACTORY
# ==========================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings


# Global immutable configuration
settings = get_settings()