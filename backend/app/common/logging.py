"""Logging helpers that avoid leaking document text."""

from __future__ import annotations

import logging
from typing import Final


LOGGER_NAME: Final[str] = "local_ai_academic_assistant"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
            )
        )
        logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    base = LOGGER_NAME if name is None else f"{LOGGER_NAME}.{name}"
    return logging.getLogger(base)
