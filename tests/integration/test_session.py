"""Tests del módulo session."""

from __future__ import annotations

import pytest


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_session_status(client: object) -> None:
    """session.status funciona después de session.new del fixture."""
    status = await client.session.status()
    assert status is not None
    assert status.ready is True


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_subscribe_and_unsubscribe(client: object) -> None:
    """Subscribe y unsubscribe funcionan."""
    await client.session.subscribe(["log.entryAdded"])
    await client.session.unsubscribe(["log.entryAdded"])
