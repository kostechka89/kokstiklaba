import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(level: str = "INFO") -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            timestamper,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


logger = get_logger(__name__)
