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

    # Google Configuration
    google_api_key: str

    # OpenAI Configuration
    openai_api_key: str
    
    provider: str = "openai"  # Default to OpenAI, can be overridden by .env

    llm_max_tokens: int = 9216

    # Model Configuration
    # Gemini Models
    embedding_gemini_model: str = "gemini-embedding-001"
    llm_gemini_model: str = "gemini-2.5-flash"

    # OpenAI Models
    llm_openai_model: str = "gpt-5-mini"
    embedding_openai_model: str = "text-embedding-3-small"

    # Ollama Models
    ollama_url: str = "http://localhost:11434/v1"
    llm_ollama_model: str = "gemma3:1b"
    embedding_ollama_model: str = "embeddinggemma:latest"
    
    llm_temperature: float = 0.0

    # Logging
    log_level: str = "INFO"

    # RAGAS Evaluation Settings
    enable_ragas_evaluation: bool = True
    ragas_timeout_seconds: float = 30.0
    ragas_log_results: bool = True

    # Alerts config
    project_alert_config_path:str = "./configs/thresholds.yaml"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    # Application Info
    app_name: str = "RAG Evaluation Service"
    app_version: str = "0.1.0"

    # Database Settings
    database_url: str

    #JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
