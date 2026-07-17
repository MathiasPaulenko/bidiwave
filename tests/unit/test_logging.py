"""Unit tests for bidiwave._internal.logging.setup_logging."""

from __future__ import annotations

import logging

from bidiwave._internal.logging import setup_logging


def _reset_bidiwave_logger() -> logging.Logger:
    logger = logging.getLogger("bidiwave")
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)
    return logger


def test_setup_logging_adds_single_handler() -> None:
    logger = _reset_bidiwave_logger()
    setup_logging(level="DEBUG")
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1


def test_setup_logging_does_not_duplicate_handlers_on_repeat_calls() -> None:
    logger = _reset_bidiwave_logger()
    setup_logging(level="INFO")
    setup_logging(level="WARNING")
    setup_logging(level="ERROR")
    assert len(logger.handlers) == 1
    assert logger.level == logging.ERROR


def test_setup_logging_reapplies_format_on_second_call() -> None:
    """Regression: a second setup_logging() call (e.g. a second
    BiDiClient.connect() with structured=True) must update the format
    of the existing handler instead of being silently discarded."""
    logger = _reset_bidiwave_logger()
    setup_logging(structured=False)
    plain_formatter = logger.handlers[0].formatter
    assert plain_formatter is not None
    assert "asctime" in plain_formatter._fmt  # type: ignore[union-attr]

    setup_logging(structured=True)
    structured_formatter = logger.handlers[0].formatter
    assert structured_formatter is not None
    assert "asctime" not in structured_formatter._fmt  # type: ignore[union-attr]
    assert len(logger.handlers) == 1


def test_setup_logging_invalid_level_falls_back_to_info() -> None:
    logger = _reset_bidiwave_logger()
    setup_logging(level="NOT_A_REAL_LEVEL")
    assert logger.level == logging.INFO
