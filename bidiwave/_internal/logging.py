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
    if isinstance(level, int):
        logger.setLevel(level)
    else:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if structured:
        formatter = logging.Formatter(
            "[bidiwave] %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [bidiwave] %(name)s %(levelname)s %(message)s"
        )

    # Only reformat handlers this function installed — handlers the caller
    # attached to the "bidiwave" logger keep their own formatter.
    owned = [h for h in logger.handlers if getattr(h, "_bidiwave_owned", False)]
    if owned:
        # Re-apply the requested format instead of silently discarding it
        # (a second setup_logging() call, e.g. from a second
        # BiDiClient.connect() with a different config, must not be a
        # no-op).
        for handler in owned:
            handler.setFormatter(formatter)
    elif not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler._bidiwave_owned = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
