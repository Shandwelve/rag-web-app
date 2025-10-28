import logging
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOG_LEVEL: str | int = Field(default=logging.INFO)
    STORAGE_PATH: str = "storage"

    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""

    WORKOS_API_KEY: str = ""
    WORKOS_CLIENT_ID: str = ""
    WORKOS_REDIRECT_URI: str = ""
    WORKOS_STATE_SECRET: str = ""
    WORKOS_STATE_TIMEOUT: int = 600

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str = ""
    CHROMA_PERSIST_DIRECTORY: str = "chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1000
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    MAX_CONCURRENT_PROCESSING: int = 3
    PROCESSING_TIMEOUT: int = 300
    ENABLE_EMBEDDINGS: bool = True
    CACHE_PROCESSED_DOCS: bool = True

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore",
        populate_by_name=True,
    )

    @computed_field
    def DB_URL(self) -> str:  # noqa: N802
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    def STORAGE_DIR(self) -> Path:  # noqa: N802
        return Path(__file__).parent.parent.parent / self.STORAGE_PATH


settings = Settings()
