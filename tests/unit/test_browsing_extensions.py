"""Unit tests for browsing extensions: reload, traverse_history, handle_user_prompt, print."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.protocol.results import Navigation, PrintResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def browsing_module(mock_connection: MockConn) -> BrowsingModule:
    return BrowsingModule(mock_connection)


CTX_ID = "ctx-1"


class TestReload:
    async def test_reload_basic(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-1",
        }
        result = await browsing_module.reload(CTX_ID)
        assert isinstance(result, Navigation)
        assert result.url == "https://example.com/"
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.reload"
        assert call.args[1]["context"] == CTX_ID
        assert call.args[1]["wait"] == "complete"

    async def test_reload_with_ignore_cache(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        await browsing_module.reload(CTX_ID, ignore_cache=True)
        params = mock_connection.send_command.call_args.args[1]
        assert params["ignoreCache"] is True

    async def test_reload_wait_interactive(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        await browsing_module.reload(CTX_ID, wait="interactive")
        params = mock_connection.send_command.call_args.args[1]
        assert params["wait"] == "interactive"


class TestTraverseHistory:
    async def test_traverse_back(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://previous.example.com/",
        }
        result = await browsing_module.traverse_history(CTX_ID, "back")
        assert isinstance(result, Navigation)
        assert result.url == "https://previous.example.com/"
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.traverseHistory"
        assert call.args[1]["direction"] == "back"

    async def test_traverse_forward(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://next.example.com/",
        }
        result = await browsing_module.traverse_history(CTX_ID, "forward")
        assert isinstance(result, Navigation)
        assert result.url == "https://next.example.com/"
        params = mock_connection.send_command.call_args.args[1]
        assert params["direction"] == "forward"


class TestHandleUserPrompt:
    async def test_accept_prompt(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.handle_user_prompt(CTX_ID, accept=True)
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.handleUserPrompt"
        assert call.args[1]["context"] == CTX_ID
        assert call.args[1]["accept"] is True

    async def test_dismiss_prompt(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.handle_user_prompt(CTX_ID, accept=False)
        params = mock_connection.send_command.call_args.args[1]
        assert params["accept"] is False

    async def test_prompt_with_user_text(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.handle_user_prompt(
            CTX_ID, accept=True, user_text="hello"
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["userText"] == "hello"

    async def test_prompt_no_optional_params(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.handle_user_prompt(CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert "accept" not in params
        assert "userText" not in params


class TestPrint:
    async def test_print_basic(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "JVBERi0xLjQK"}
        result = await browsing_module.print(CTX_ID)
        assert isinstance(result, PrintResult)
        assert result.data == "JVBERi0xLjQK"
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.print"
        assert call.args[1]["context"] == CTX_ID

    async def test_print_with_options(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "JVBERi0xLjQK"}
        await browsing_module.print(
            CTX_ID,
            background=True,
            orientation="landscape",
            scale=0.5,
            margin={"top": 1, "bottom": 1, "left": 1, "right": 1},
            page={"width": 8.5, "height": 11},
            page_ranges=["1-3", "5"],
            shrink_to_fit=False,
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["printBackground"] is True
        assert params["orientation"] == "landscape"
        assert params["scale"] == 0.5
        assert params["margin"] == {"top": 1, "bottom": 1, "left": 1, "right": 1}
        assert params["page"] == {"width": 8.5, "height": 11}
        assert params["pageRanges"] == ["1-3", "5"]
        assert params["shrinkToFit"] is False

    async def test_print_defaults(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": ""}
        await browsing_module.print(CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert params["printBackground"] is False
        assert params["orientation"] == "portrait"
        assert params["scale"] == 1.0
        assert params["shrinkToFit"] is True
        assert "margin" not in params
        assert "page" not in params
        assert "pageRanges" not in params
