"""Tests del EventDispatcher."""

from unittest.mock import AsyncMock

import pytest

from bidiwave.events.dispatcher import EventDispatcher


@pytest.mark.asyncio
async def test_dispatch_calls_handler():
    dispatcher = EventDispatcher()
    handler = AsyncMock()
    dispatcher.on("log.entryAdded", handler)

    await dispatcher.dispatch("log.entryAdded", {
        "level": "info",
        "text": "hello",
        "timestamp": 12345,
        "source": {"realm": "r1", "context": "c1"},
    })

    handler.assert_called_once()
    event = handler.call_args[0][0]
    assert event.text == "hello"
    assert event.level == "info"


@pytest.mark.asyncio
async def test_error_isolation():
    dispatcher = EventDispatcher()
    calls: list[str] = []

    async def failing_handler(entry):
        raise ValueError("boom")

    async def good_handler(entry):
        calls.append(entry.text)

    dispatcher.on("log.entryAdded", failing_handler)
    dispatcher.on("log.entryAdded", good_handler)

    await dispatcher.dispatch("log.entryAdded", {
        "level": "info",
        "text": "test",
        "timestamp": 12345,
        "source": {"realm": "r1"},
    })

    assert len(calls) == 1
    assert calls[0] == "test"


@pytest.mark.asyncio
async def test_off_removes_handler():
    dispatcher = EventDispatcher()
    calls: list[str] = []

    async def handler(entry):
        calls.append(entry.text)

    sub = dispatcher.on("log.entryAdded", handler)
    await dispatcher.dispatch("log.entryAdded", {
        "level": "info", "text": "first", "timestamp": 1, "source": {},
    })
    assert len(calls) == 1

    dispatcher.off(sub)
    await dispatcher.dispatch("log.entryAdded", {
        "level": "info", "text": "second", "timestamp": 2, "source": {},
    })
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_multiple_event_types_independent():
    dispatcher = EventDispatcher()
    log_calls: list = []
    ctx_calls: list = []

    async def on_log(entry):
        log_calls.append(entry)

    async def on_ctx(entry):
        ctx_calls.append(entry)

    dispatcher.on("log.entryAdded", on_log)
    dispatcher.on("browsingContext.contextCreated", on_ctx)

    await dispatcher.dispatch("log.entryAdded", {
        "level": "info", "text": "log1", "timestamp": 1, "source": {},
    })
    await dispatcher.dispatch("browsingContext.contextCreated", {
        "context": "ctx-1", "url": "about:blank",
    })

    assert len(log_calls) == 1
    assert len(ctx_calls) == 1


@pytest.mark.asyncio
async def test_dispatch_no_handlers_does_nothing():
    dispatcher = EventDispatcher()
    await dispatcher.dispatch("log.entryAdded", {
        "level": "info", "text": "noop", "timestamp": 1, "source": {},
    })


@pytest.mark.asyncio
async def test_multiple_handlers_same_event():
    dispatcher = EventDispatcher()
    calls: list[str] = []

    async def handler_a(entry):
        calls.append(f"a:{entry.text}")

    async def handler_b(entry):
        calls.append(f"b:{entry.text}")

    dispatcher.on("log.entryAdded", handler_a)
    dispatcher.on("log.entryAdded", handler_b)

    await dispatcher.dispatch("log.entryAdded", {
        "level": "info", "text": "msg", "timestamp": 1, "source": {},
    })

    assert calls == ["a:msg", "b:msg"]
