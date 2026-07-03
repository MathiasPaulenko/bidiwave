"""Logging estructurado para bidiwave."""

import logging
import sys


def setup_logging(
    level: str = "INFO",
    structured: bool = False,
) -> None:
    """Configura logging para bidiwave.

    Args:
        level: Nivel de logging ("DEBUG", "INFO", "WARNING", "ERROR").
        structured: Si True, usa formato estructurado con claves.
    """
    logger = logging.getLogger("bidiwave")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stderr)

    if structured:
        formatter = logging.Formatter(
            "[bidiwave] %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [bidiwave] %(name)s %(levelname)s %(message)s"
        )

    handler.setFormatter(formatter)
    logger.handlers = [handler]
