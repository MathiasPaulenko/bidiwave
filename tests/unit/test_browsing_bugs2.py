"""Regression tests for browsingContext bug fixes — round 2."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingContext, BrowsingModule

CTX_ID = "ctx-123"

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def browsing_module(mock_connection: MockConn) -> BrowsingModule:
    return BrowsingModule(mock_connection)


class TestNavigationUrlMissing:
    """Bug 4: Navigation.url is required but browser may omit it when wait='none'."""

    async def test_navigate_wait_none_no_url_in_response(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "navigation": "nav-1",
        }
        nav = await browsing_module.navigate(CTX_ID, "https://example.com", wait="none")
        assert nav.context == CTX_ID
        assert nav.navigation == "nav-1"
        assert nav.url == ""

    async def test_navigation_model_url_missing_defaults_to_empty(self) -> None:
        from bidiwave.protocol.results import Navigation

        nav = Navigation.model_validate({"context": CTX_ID, "navigation": "nav-1"})
        assert nav.url == ""


class TestWaitForSelectorExceptionResult:
    """Bug 5: wait_for_selector doesn't handle JS exception results."""

    async def test_wait_for_selector_js_exception_raises(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "exception",
            "exceptionDetails": {"text": "SyntaxError: unexpected token"},
        }
        with pytest.raises(Exception, match="SyntaxError"):
            await browsing_module.wait_for_selector(CTX_ID, "h1", timeout=5.0)


class TestWaitForFunctionExceptionResult:
    """Bug 5b: wait_for_function doesn't handle JS exception results."""

    async def test_wait_for_function_js_exception_raises(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "exception",
            "exceptionDetails": {"text": "ReferenceError: x is not defined"},
        }
        with pytest.raises(Exception, match="ReferenceError"):
            await asyncio.wait_for(
                browsing_module.wait_for_function(CTX_ID, "badExpr()", timeout=1.0),
                timeout=3.0,
            )

    async def test_wait_for_function_uses_await_promise(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        await browsing_module.wait_for_function(CTX_ID, "document.ready", timeout=5.0)
        params = mock_connection.send_command.call_args.args[1]
        assert params["awaitPromise"] is True
        assert "new Promise" in params["expression"]
