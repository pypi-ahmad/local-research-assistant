"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Route stdlib logs to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        level = record.levelname
        logger.bind(logger_name=record.name).log(level, record.getMessage())


def setup_logging() -> None:
    """Configure JSON logs for API and worker services."""
    logger.remove()
    logger.add(sys.stdout, serialize=True)

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
