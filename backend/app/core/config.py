"""Application configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Meeting Brief Agent"
    debug: bool = False
    api_prefix: str = "/api"

    # Database
    database_url: str = "sqlite+aiosqlite:///./meeting_brief.db"

    # LLM Provider
    llm_provider: str = "openai"  # openai, anthropic, ollama, llamacpp

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # LlamaCpp
    llamacpp_model_path: Optional[str] = None
    llamacpp_n_ctx: int = 4096
    llamacpp_n_gpu_layers: int = -1

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "meeting_context"

    # Calendar Integration
    google_credentials_path: Optional[str] = None
    outlook_client_id: Optional[str] = None
    outlook_client_secret: Optional[str] = None

    # Email Integration
    imap_host: Optional[str] = None
    imap_port: int = 993
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None

    # CRM Integration
    crm_provider: Optional[str] = None  # hubspot, salesforce
    crm_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


settings = get_settings()
