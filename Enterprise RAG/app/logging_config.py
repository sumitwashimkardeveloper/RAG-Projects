"""
Logging Configuration
"""

import logging
import logging.config
import sys
from app.config import settings


def setup_logging():
    """
    Configure logging for the application
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper())

    if settings.LOG_FORMAT == "json":
        # JSON logging format for structured logs
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": sys.stdout,
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
        }
    else:
        # Standard logging format
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "standard",
                    "stream": sys.stdout,
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "sqlalchemy.engine": {
                    "level": "WARNING" if not settings.DEBUG else "INFO",
                },
                "asyncio": {
                    "level": "WARNING",
                },
            },
        }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}"
    )
