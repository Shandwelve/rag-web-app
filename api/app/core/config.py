import base64
import hashlib
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
    WORKOS_COOKIE_SECRET: str = ""
    WORKOS_ORGANIZATION_ID: str = ""
    FRONTEND_URL: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str = ""
    CHAT_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 1000

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

    @computed_field
    def WORKOS_COOKIE_PASSWORD(self) -> str:  # noqa: N802
        if not self.WORKOS_COOKIE_SECRET:
            return ""
        key_bytes = hashlib.sha256(self.WORKOS_COOKIE_SECRET.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes).decode()


settings = Settings()
