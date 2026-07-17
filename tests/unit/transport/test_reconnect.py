"""Tests de reconnect del Connection."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets

from bidiwave.exceptions import BiDiConnectionError
from bidiwave.transport.connection import Connection, TransportConfig


@pytest.mark.asyncio
async def test_on_disconnect_handler_called_on_close():
    config = TransportConfig(max_retries=1, retry_delay=0.01, retry_backoff=1.0)
    conn = Connection("ws://localhost:9999", config=config)

    disconnect_called = asyncio.Event()

    async def on_disconnect(_event):
        disconnect_called.set()

    conn.on_disconnect(on_disconnect)

    mock_ws = AsyncMock()
    mock_ws.__aiter__ = MagicMock(return_value=mock_ws)
    mock_ws.__anext__ = AsyncMock(side_effect=websockets.ConnectionClosed(None, None))

    with patch.object(websockets, "connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = mock_ws
        await conn.connect()
        await asyncio.sleep(0.1)

    assert disconnect_called.is_set()
    await conn.close()


@pytest.mark.asyncio
async def test_on_reconnect_handler_called_after_reconnect():
    config = TransportConfig(max_retries=2, retry_delay=0.01, retry_backoff=1.0)
    conn = Connection("ws://localhost:9999", config=config)

    reconnect_called = asyncio.Event()

    async def on_reconnect(_event):
        reconnect_called.set()

    conn.on_reconnect(on_reconnect)

    first_ws = AsyncMock()
    first_ws.__aiter__ = MagicMock(return_value=first_ws)
    first_ws.__anext__ = AsyncMock(side_effect=websockets.ConnectionClosed(None, None))

    second_ws = AsyncMock()
    second_ws.__aiter__ = MagicMock(return_value=second_ws)
    second_ws.__anext__ = AsyncMock(side_effect=asyncio.CancelledError())

    with patch.object(websockets, "connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = [first_ws, second_ws]
        await conn.connect()
        await asyncio.sleep(0.2)

    assert reconnect_called.is_set()
    await conn.close()


@pytest.mark.asyncio
async def test_reconnect_fails_after_max_retries():
    config = TransportConfig(max_retries=2, retry_delay=0.01, retry_backoff=1.0)
    conn = Connection("ws://localhost:9999", config=config)

    mock_ws = AsyncMock()
    mock_ws.__aiter__ = MagicMock(return_value=mock_ws)
    mock_ws.__anext__ = AsyncMock(side_effect=websockets.ConnectionClosed(None, None))

    with patch.object(websockets, "connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = [
            mock_ws,
            OSError("refused"),
            OSError("refused"),
        ]
        await conn.connect()
        await asyncio.sleep(0.3)

    assert conn._reconnecting is False
    await conn.close()


@pytest.mark.asyncio
async def test_send_command_raises_when_closed():
    conn = Connection("ws://localhost:9999")
    conn._closed = True
    with pytest.raises(BiDiConnectionError):
        await conn.send_command("session.status", {})


@pytest.mark.asyncio
async def test_send_command_fails_fast_while_reconnecting():
    conn = Connection("ws://localhost:9999")
    conn._ws = AsyncMock()
    conn._reconnecting = True
    with pytest.raises(BiDiConnectionError, match="reconnecting"):
        await conn.send_command("session.status", {})
