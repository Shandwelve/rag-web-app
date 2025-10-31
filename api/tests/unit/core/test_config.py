from unittest.mock import patch

from app.core.config import Settings


def test_default_values() -> None:
    with patch.dict("os.environ", {}, clear=True):
        test_settings = Settings()
        assert test_settings.LOG_LEVEL in ["INFO", 20]
        assert test_settings.STORAGE_PATH == "storage"
        assert test_settings.JWT_ALGORITHM == "HS256"
        assert test_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert test_settings.CHAT_MODEL == "gpt-4o-mini"
        assert test_settings.MAX_TOKENS == 1000


def test_db_url_computed_field() -> None:
    with patch.dict(
        "os.environ",
        {
            "DB_USER": "testuser",
            "DB_PASS": "testpass",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
        },
        clear=True,
    ):
        test_settings = Settings()
        expected_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
        assert test_settings.DB_URL == expected_url


def test_storage_dir_computed_field() -> None:
    with patch.dict("os.environ", {}, clear=True):
        test_settings = Settings()
        assert test_settings.STORAGE_DIR.name == "storage"
