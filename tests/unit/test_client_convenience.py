"""Unit tests for BiDiClient convenience event methods."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.client import BiDiClient
from bidiwave.events.dispatcher import EventDispatcher


@pytest.fixture
def client() -> BiDiClient:
    conn = MagicMock()
    conn._dispatcher = EventDispatcher()
    conn.on_reconnect = MagicMock()
    conn.on_disconnect = MagicMock()
    return BiDiClient(conn)


def test_on_user_prompt_closed(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_user_prompt_closed(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.userPromptClosed", [])
    assert handler in handlers


def test_on_navigation_started(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_navigation_started(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.navigationStarted", [])
    assert handler in handlers


def test_on_navigation_aborted(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_navigation_aborted(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.navigationAborted", [])
    assert handler in handlers


def test_on_navigation_committed(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_navigation_committed(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.navigationCommitted", [])
    assert handler in handlers


def test_on_navigation_failed(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_navigation_failed(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.navigationFailed", [])
    assert handler in handlers


def test_on_script_message(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_script_message(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("script.message", [])
    assert handler in handlers


def test_off_unsubscribes(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_navigation_started(handler)
    assert handler in client._dispatcher._handlers.get("browsingContext.navigationStarted", [])
    client.off(sub)
    assert handler not in client._dispatcher._handlers.get("browsingContext.navigationStarted", [])


def test_on_download_will_begin(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_download_will_begin(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.downloadWillBegin", [])
    assert handler in handlers


def test_on_download_end(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_download_end(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("browsingContext.downloadEnd", [])
    assert handler in handlers


def test_on_file_dialog_opened(client: BiDiClient) -> None:
    handler = AsyncMock()
    sub = client.on_file_dialog_opened(handler)
    assert sub is not None
    handlers = client._dispatcher._handlers.get("input.fileDialogOpened", [])
    assert handler in handlers


@pytest.mark.asyncio
async def test_close_browser_sends_command(client: BiDiClient) -> None:
    client._connection.send_command = AsyncMock(return_value={})
    await client.browsing.close_browser()
    client._connection.send_command.assert_called_once_with("browser.close", {})


@pytest.mark.asyncio
async def test_create_user_context_with_accept_insecure_certs(client: BiDiClient) -> None:
    client._connection.send_command = AsyncMock(
        return_value={"userContext": "ctx-new"}
    )
    result = await client.browsing.create_user_context(accept_insecure_certs=True)
    client._connection.send_command.assert_called_once_with(
        "browser.createUserContext", {"acceptInsecureCerts": True}
    )
    assert result.user_context == "ctx-new"


@pytest.mark.asyncio
async def test_create_user_context_without_accept_insecure_certs(client: BiDiClient) -> None:
    client._connection.send_command = AsyncMock(
        return_value={"userContext": "ctx-default"}
    )
    result = await client.browsing.create_user_context()
    client._connection.send_command.assert_called_once_with(
        "browser.createUserContext", {}
    )
    assert result.user_context == "ctx-default"


@pytest.mark.asyncio
async def test_get_client_windows(client: BiDiClient) -> None:
    client._connection.send_command = AsyncMock(
        return_value={
            "clientWindows": [
                {
                    "clientWindow": "win-1",
                    "state": "normal",
                    "width": 1920,
                    "height": 1080,
                    "x": 0,
                    "y": 0,
                    "active": True,
                }
            ]
        }
    )
    result = await client.browsing.get_client_windows()
    client._connection.send_command.assert_called_once_with(
        "browser.getClientWindows", {}
    )
    assert len(result) == 1
    assert result[0].client_window == "win-1"
    assert result[0].state == "normal"
    assert result[0].width == 1920
    assert result[0].active is True


@pytest.mark.asyncio
async def test_set_client_window_state(client: BiDiClient) -> None:
    client._connection.send_command = AsyncMock(return_value={})
    await client.browsing.set_client_window_state("win-1", "maximized")
    client._connection.send_command.assert_called_once_with(
        "browser.setClientWindowState",
        {"clientWindow": "win-1", "state": "maximized"},
    )
