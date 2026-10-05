"""Tests for historyUpdated, deleteCookie, setViewport, addPreloadScript."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.commands import ViewportSize
from bidiwave.protocol.events import (
    BrowsingContextHistoryUpdatedEvent,
    parse_event,
)
from bidiwave.protocol.results import AddPreloadScriptResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


class TestHistoryUpdatedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com/page",
        }
        event = parse_event("browsingContext.historyUpdated", params)
        assert isinstance(event, BrowsingContextHistoryUpdatedEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com/page"


class TestDeleteCookie:
    async def test_delete_cookie(
        self,
        mock_connection: MockConn,
    ) -> None:
        storage = StorageModule(mock_connection)
        await storage.delete_cookie("ctx-1", "session")
        mock_connection.send_command.assert_called_once()
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "storage.deleteCookies"
        assert call_args.args[1]["filter"] == {"name": "session"}
        assert call_args.args[1]["partition"] == {
            "type": "context",
            "context": "ctx-1",
        }


class TestSetViewportWithModel:
    async def test_set_viewport_with_viewport_size(
        self,
        mock_connection: MockConn,
    ) -> None:
        browsing = BrowsingModule(mock_connection, MagicMock())
        size = ViewportSize(width=800, height=600)
        await browsing.set_viewport("ctx-1", viewport=size, device_pixel_ratio=2.0)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["viewport"] == {"width": 800, "height": 600}
        assert call_args.args[1]["devicePixelRatio"] == 2.0

    async def test_set_viewport_with_dict(
        self,
        mock_connection: MockConn,
    ) -> None:
        browsing = BrowsingModule(mock_connection, MagicMock())
        await browsing.set_viewport("ctx-1", viewport={"width": 1024, "height": 768})
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["viewport"] == {"width": 1024, "height": 768}

    async def test_reset_viewport_sends_nulls(
        self,
        mock_connection: MockConn,
    ) -> None:
        browsing = BrowsingModule(mock_connection, MagicMock())
        await browsing.reset_viewport("ctx-1")
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["viewport"] is None
        assert call_args.args[1]["devicePixelRatio"] is None
        assert call_args.args[1]["context"] == "ctx-1"


class TestScriptAddPreloadScript:
    async def test_add_preload_script_basic(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-1"}
        script = ScriptModule(mock_connection)
        result = await script.add_preload_script(
            "() => { console.log('hello'); }",
        )
        assert isinstance(result, AddPreloadScriptResult)
        assert result.script == "preload-1"

    async def test_add_preload_script_with_contexts(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-2"}
        script = ScriptModule(mock_connection)
        result = await script.add_preload_script(
            "() => {}",
            contexts=["ctx-1", "ctx-2"],
            sandbox="my-sandbox",
        )
        assert result.script == "preload-2"
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["contexts"] == ["ctx-1", "ctx-2"]
        assert call_args.args[1]["sandbox"] == "my-sandbox"
