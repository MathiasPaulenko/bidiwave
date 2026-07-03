"""Tests de eventos en tiempo real."""

from __future__ import annotations

import asyncio

import pytest


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_console_log_event(client: object, context: object) -> None:
    """log.entryAdded is captured in real time."""
    logs: list[str] = []

    async def on_log(entry: object) -> None:
        logs.append(entry.text)

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.script.evaluate(context, "console.log('test-event-123')")

    await asyncio.sleep(2)

    assert any("test-event-123" in log for log in logs)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_context_created_event(client: object) -> None:
    """browsingContext.contextCreated is captured when creating a context."""
    events: list[object] = []

    async def on_created(event: object) -> None:
        events.append(event)

    client.on("browsingContext.contextCreated", on_created)
    await client.session.subscribe(["browsingContext.contextCreated"])

    ctx = await client.browsing.create_context()
    await asyncio.sleep(1)

    assert len(events) >= 1
    # The event may be for any context, find the one matching our ctx
    ctx_ids = [e.context for e in events]
    assert ctx.id in ctx_ids

    await client.browsing.close(ctx)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_context_destroyed_event(client: object) -> None:
    """browsingContext.contextDestroyed is captured when closing a context."""
    events: list[object] = []

    async def on_destroyed(event: object) -> None:
        events.append(event)

    client.on("browsingContext.contextDestroyed", on_destroyed)
    await client.session.subscribe(["browsingContext.contextDestroyed"])

    ctx = await client.browsing.create_context()
    await asyncio.sleep(0.5)
    await client.browsing.close(ctx)
    await asyncio.sleep(1)

    assert len(events) >= 1
    assert events[0].context == ctx.id
