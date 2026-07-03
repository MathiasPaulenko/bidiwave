"""Tests for the session module."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_session_status(client: object) -> None:
    """session.status works after the fixture's session.new."""
    status = await client.session.status()
    assert status is not None
    # When already connected via WebSocket, ready=False with message='already connected'
    assert status.message is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_subscribe_and_unsubscribe(client: object) -> None:
    """Subscribe and unsubscribe work."""
    await client.session.subscribe(["log.entryAdded"])
    await client.session.unsubscribe(["log.entryAdded"])
