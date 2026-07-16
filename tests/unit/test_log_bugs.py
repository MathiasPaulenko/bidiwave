"""Regression tests for log module bug fixes."""

from __future__ import annotations

from bidiwave.protocol.events import LogEntryAddedEvent, parse_event


class TestLogEntryAddedLevelEnum:
    """Bug 32: level should use 'warning' not 'warn' per W3C spec."""

    def test_level_warning_accepted(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "warning",
            "text": "careful",
            "timestamp": 123,
            "source": {},
        })
        assert event.level == "warning"

    def test_level_warn_normalized(self) -> None:
        """Edge browser sends 'warn' but W3C spec uses 'warning' — normalize."""
        event = LogEntryAddedEvent.model_validate({
            "level": "warn",
            "text": "careful",
            "timestamp": 123,
            "source": {},
        })
        assert event.level == "warning"


class TestLogEntryAddedStackTrace:
    """Bug 33: missing stackTrace field per spec."""

    def test_stack_trace_present(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "error",
            "text": "oops",
            "timestamp": 999,
            "source": {},
            "stackTrace": {"callFrames": []},
        })
        assert event.stack_trace is not None

    def test_stack_trace_optional(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "info",
            "text": "hello",
            "timestamp": 123,
            "source": {},
        })
        assert event.stack_trace is None


class TestLogEntryAddedTypeLiteral:
    """Bug 34: type should be Literal['console', 'javascript'] per spec."""

    def test_type_console(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "info",
            "text": "hello",
            "timestamp": 123,
            "source": {},
            "type": "console",
        })
        assert event.type == "console"

    def test_type_javascript(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "error",
            "text": "oops",
            "timestamp": 123,
            "source": {},
            "type": "javascript",
        })
        assert event.type == "javascript"


class TestLogEntryAddedMethodField:
    """Bug 35: missing method field for console entries per spec."""

    def test_method_field_present(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "info",
            "text": "hello",
            "timestamp": 123,
            "source": {},
            "type": "console",
            "method": "log",
        })
        assert event.method == "log"

    def test_method_field_optional(self) -> None:
        event = LogEntryAddedEvent.model_validate({
            "level": "info",
            "text": "hello",
            "timestamp": 123,
            "source": {},
        })
        assert event.method is None


class TestParseEventLogWithNewFields:
    """Verify parse_event works with updated LogEntryAddedEvent."""

    def test_parse_log_with_warning_level(self) -> None:
        event = parse_event("log.entryAdded", {
            "level": "warning",
            "text": "careful",
            "timestamp": 123,
            "source": {},
        })
        assert isinstance(event, LogEntryAddedEvent)
        assert event.level == "warning"
