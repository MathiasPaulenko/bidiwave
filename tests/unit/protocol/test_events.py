"""Tests de modelos de eventos del protocolo."""

from bidiwave.protocol.events import (
    BrowsingContextCreatedEvent,
    Event,
    LogEntryAddedEvent,
    parse_event,
)


def test_log_entry_added_parsing():
    event = LogEntryAddedEvent.model_validate({
        "level": "info",
        "text": "hello",
        "timestamp": 12345,
        "source": {"realm": "r1", "context": "c1"},
        "type": "console",
        "args": [{"type": "string", "value": "hello"}],
    })
    assert event.level == "info"
    assert event.text == "hello"
    assert len(event.args) == 1


def test_browsing_context_created_parsing():
    event = BrowsingContextCreatedEvent.model_validate({
        "context": "ctx-1",
        "url": "about:blank",
        "user_context": "default",
    })
    assert event.context == "ctx-1"
    assert event.url == "about:blank"


def test_parse_event_unknown_returns_base():
    event = parse_event("unknown.event", {"foo": "bar"})
    assert isinstance(event, Event)
    assert event.method == "unknown.event"


def test_parse_event_log_entry_added():
    event = parse_event("log.entryAdded", {
        "level": "error",
        "text": "oops",
        "timestamp": 999,
        "source": {},
    })
    assert isinstance(event, LogEntryAddedEvent)
    assert event.level == "error"


def test_parse_event_browsing_context_created():
    event = parse_event("browsingContext.contextCreated", {
        "context": "ctx-2",
        "url": "https://example.com",
    })
    assert isinstance(event, BrowsingContextCreatedEvent)
    assert event.context == "ctx-2"
