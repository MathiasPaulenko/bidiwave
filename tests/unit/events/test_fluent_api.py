"""Tests de fluent API y decorator mode del EventDispatcher."""

import pytest

from bidiwave.events.dispatcher import EventDispatcher


@pytest.mark.asyncio
async def test_fluent_api_chains_on():
    dispatcher = EventDispatcher()

    async def h1(_event):
        pass

    async def h2(_event):
        pass

    result = dispatcher.on("event_a", h1)
    assert result is not None

    result2 = dispatcher.on("event_b", h2)
    assert result2 is not None

    assert len(dispatcher._handlers["event_a"]) == 1
    assert len(dispatcher._handlers["event_b"]) == 1


@pytest.mark.asyncio
async def test_decorator_mode():
    dispatcher = EventDispatcher()

    @dispatcher.on("my_event")
    async def my_handler(_event):
        pass

    assert "my_event" in dispatcher._handlers
    assert my_handler in dispatcher._handlers["my_event"]


@pytest.mark.asyncio
async def test_on_returns_subscription_when_handler_provided():
    from bidiwave.events.handlers import Subscription

    dispatcher = EventDispatcher()

    async def handler(_event):
        pass

    result = dispatcher.on("test_event", handler)
    assert isinstance(result, Subscription)
    assert result.event_type == "test_event"
    assert result.handler is handler


@pytest.mark.asyncio
async def test_decorator_preserves_function():
    dispatcher = EventDispatcher()

    @dispatcher.on("event_x")
    async def original_func(_event):
        pass

    assert callable(original_func)
