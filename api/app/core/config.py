import logging

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""
    LOG_LEVEL: str | int = Field(default=logging.INFO)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @computed_field
    def DB_URL(self) -> str:  # noqa: N802
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
