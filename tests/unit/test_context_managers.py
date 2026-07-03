"""Tests de context managers de BiDiClient y BrowsingContext."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingContext, BrowsingModule
from bidiwave.transport.connection import Connection


@pytest.mark.asyncio
async def test_browsing_context_aenter_returns_self():
    ctx = BrowsingContext(id="ctx1")
    result = await ctx.__aenter__()
    assert result is ctx


@pytest.mark.asyncio
async def test_browsing_context_aexit_closes_context():
    module = MagicMock(spec=BrowsingModule)
    module.close = AsyncMock()
    ctx = BrowsingContext(id="ctx1", _module=module)

    await ctx.__aexit__(None, None, None)
    module.close.assert_called_once_with("ctx1")


@pytest.mark.asyncio
async def test_browsing_context_aexit_without_module_does_nothing():
    ctx = BrowsingContext(id="ctx1")
    await ctx.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_bidi_client_aenter_aexit_calls_close():
    from bidiwave.client import BiDiClient

    mock_connection = MagicMock(spec=Connection)
    mock_connection._dispatcher = MagicMock()
    mock_connection.close = AsyncMock()

    client = BiDiClient(mock_connection)
    result = await client.__aenter__()
    assert result is client

    await client.__aexit__(None, None, None)
    mock_connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_bidi_client_aexit_on_exception_still_closes():
    from bidiwave.client import BiDiClient

    mock_connection = MagicMock(spec=Connection)
    mock_connection._dispatcher = MagicMock()
    mock_connection.close = AsyncMock()

    client = BiDiClient(mock_connection)
    await client.__aexit__(ValueError, ValueError("test"), None)
    mock_connection.close.assert_called_once()
