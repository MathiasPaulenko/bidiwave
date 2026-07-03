"""Tests for client connection and lifecycle."""

from __future__ import annotations

import pytest

from bidiwave import BiDiClient


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_connect_and_close(client: object) -> None:
    """Connect and close work without errors."""
    assert client is not None


@pytest.mark.asyncio
async def test_context_manager(chrome_bidi: str) -> None:
    """async with closes the connection automatically."""
    async with await BiDiClient.connect(chrome_bidi) as c:
        status = await c.session.status()
        assert status is not None
