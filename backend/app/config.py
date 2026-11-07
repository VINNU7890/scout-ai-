import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys & Providers
    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_API_KEY: str = Field(default="", description="Alias for Google API key")
    GEMINI_MODEL: str = Field(default="gemini-3.5-flash", description="Gemini chat model")
    GEMINI_EMBED_MODEL: str = Field(
        default="models/gemini-embedding-001", description="Gemini embeddings model"
    )
    TAVILY_API_KEY: str | None = Field(default=None, description="Optional Tavily API key")
    APP_API_KEY: str | None = Field(default=None, description="Optional API key for client auth")

    # LangSmith
    LANGSMITH_API_KEY: str | None = Field(default=None, description="Optional LangSmith key")
    LANGSMITH_PROJECT: str = Field(default="scoutai", description="LangSmith project name")

    # Operational Modes & Storage
    DEMO_MODE: bool = Field(default=True, description="Replay pre-recorded run without LLM")
    DATABASE_URL: str = Field(default="sqlite:///./scoutai.db", description="SQLite database URL")
    CHROMA_DIR: str = Field(default="./data/chroma", description="Directory for ChromaDB vectors")
    UPLOAD_DIR: str = Field(default="./data/uploads", description="Directory for document uploads")
    STATIC_DIR: str = Field(
        default="./frontend/dist", description="Directory for frontend static assets"
    )

    # Security, Limits & Timeouts
    CORS_ORIGINS: str = Field(default="*", description="Allowed CORS origins (comma-separated or '*')")
    MAX_LLM_CALLS_PER_RUN: int = Field(default=60, description="Cap on total LLM calls per run")
    MAX_FETCH_SIZE_BYTES: int = Field(
        default=1_500_000, description="Max response size for web fetches"
    )
    FETCH_TIMEOUT_SECONDS: int = Field(default=10, description="HTTP fetch timeout")
    PAGE_TRUNCATION_LIMIT: int = Field(
        default=15_000, description="Max character length for web page content"
    )
    CACHE_EXPIRATION_HOURS: int = Field(
        default=24, description="Hours to cache search & page fetch results"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, description="Rate limit requests per IP per minute"
    )
    PORT: int = Field(default=8000, description="Port to listen on")

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def effective_gemini_key(self) -> str:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY

    @property
    def effective_database_url(self) -> str:
        if os.environ.get("DATA_DIR"):
            data_dir = os.environ["DATA_DIR"]
            os.makedirs(data_dir, exist_ok=True)
            return f"sqlite:///{os.path.join(data_dir, 'scoutai.db')}"
        return self.DATABASE_URL

    @property
    def effective_chroma_dir(self) -> str:
        if os.environ.get("DATA_DIR"):
            return os.path.join(os.environ["DATA_DIR"], "chroma")
        return self.CHROMA_DIR

    @property
    def effective_upload_dir(self) -> str:
        if os.environ.get("DATA_DIR"):
            return os.path.join(os.environ["DATA_DIR"], "uploads")
        return self.UPLOAD_DIR


@lru_cache()
def get_settings() -> Settings:
    return Settings()
