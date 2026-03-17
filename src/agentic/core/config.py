"""Framework configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGENTIC_",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Agentic Skill Framework"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    db_path: str = "agentic.db"

    # Security
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # Execution defaults
    default_timeout_ms: int = 30_000
    default_max_retries: int = 3
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout_s: int = 60

    # Observability
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = True

    # Approval workflow
    approval_expiry_hours: int = 24


def get_settings() -> Settings:
    return Settings()
