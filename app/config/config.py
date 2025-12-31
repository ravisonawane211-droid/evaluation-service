"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    # openai_api_key: str

    # Google Configuration
    google_api_key: str

    # Document Processing Settings
    chunk_size: int = 500
    chunk_overlap: int = 100

    # Model Configuration
    embedding_model: str = "gemini-embedding-001"
    llm_model: str = "gemini-2.5-flash"
    llm_temperature: float = 0.0

    # Logging
    log_level: str = "INFO"

    # RAGAS Evaluation Settings
    enable_ragas_evaluation: bool = True
    ragas_timeout_seconds: float = 30.0
    ragas_log_results: bool = True
    ragas_llm_model: str | None = "gemini-3-flash-preview"  # Defaults to llm_model if not set
    ragas_llm_temperature: float | None = 0.0  # Defaults to llm_temperature if not set
    ragas_embedding_model: str | None = "gemini-embedding-001"  # Defaults to embedding_model if not set

    # Alerts config
    project_alert_config_path:str = "./configs/thresholds.yaml"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    # Application Info
    app_name: str = "RAG Evaluation Service"
    app_version: str = "0.1.0"

    # Database Settings
    database_url: str = "./db/evaluation.db"

    #JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
