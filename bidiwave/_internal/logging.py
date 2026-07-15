"""Structured logging for bidiwave."""

import logging
import sys


def setup_logging(
    level: str = "INFO",
    structured: bool = False,
) -> None:
    """Configures logging for bidiwave.

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR").
        structured: If True, uses structured format with keys.
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
    if not logger.handlers:
        logger.addHandler(handler)
