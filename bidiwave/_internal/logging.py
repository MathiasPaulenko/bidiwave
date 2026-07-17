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

    if structured:
        formatter = logging.Formatter(
            "[bidiwave] %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [bidiwave] %(name)s %(levelname)s %(message)s"
        )

    if logger.handlers:
        # Re-apply the requested format to existing handlers instead of
        # silently discarding it (a second setup_logging() call, e.g. from
        # a second BiDiClient.connect() with a different config, must not
        # be a no-op).
        for existing_handler in logger.handlers:
            existing_handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
