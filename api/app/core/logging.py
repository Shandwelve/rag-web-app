import logging
import logging.handlers
from pathlib import Path

from app.core.config import settings


def setup_logging() -> logging.Logger:
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_level = settings.LOG_LEVEL
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger("api")
    logger.setLevel(log_level)

    logger.handlers.clear()

    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "api.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    error_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    logger.propagate = False

    return logger


def get_logger(name: str = "api") -> logging.Logger:
    return logging.getLogger(name)
