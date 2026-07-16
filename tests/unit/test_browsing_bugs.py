"""Regression tests for browsingContext bug fixes."""

from __future__ import annotations

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


class TestNavigateUpdatesContextUrl:
    """Bug 1: navigate/reload/traverse_history must update BrowsingContext.url."""

    async def test_navigate_updates_context_url(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-1",
        }
        ctx = BrowsingContext(id=CTX_ID, url="", _module=browsing_module)
        assert ctx.url == ""
        await browsing_module.navigate(ctx, "https://example.com")
        assert ctx.url == "https://example.com/"

    async def test_navigate_with_str_does_not_crash(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-1",
        }
        await browsing_module.navigate(CTX_ID, "https://example.com")

    async def test_reload_updates_context_url(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-2",
        }
        ctx = BrowsingContext(id=CTX_ID, url="https://old.com", _module=browsing_module)
        await browsing_module.reload(ctx)
        assert ctx.url == "https://example.com/"

    async def test_traverse_history_updates_context_url(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://previous.com/",
        }
        ctx = BrowsingContext(id=CTX_ID, url="https://current.com", _module=browsing_module)
        await browsing_module.traverse_history(ctx, "back")
        assert ctx.url == "https://previous.com/"


class TestWaitForSelectorNullBody:
    """Bug 2: wait_for_selector must not crash when document.body is null."""

    async def test_expression_includes_null_body_guard(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "boolean", "value": True},
        }
        await browsing_module.wait_for_selector(CTX_ID, "h1", timeout=5.0)
        params = mock_connection.send_command.call_args.args[1]
        expression = params["expression"]
        assert "document.body || document.documentElement" in expression
        assert "if (!target) return resolve(false)" in expression


class TestScreenshotClip:
    """Bug 3: screenshot must support clip parameter per W3C spec."""

    async def test_screenshot_with_clip(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "base64data"}
        clip = {"type": "box", "x": 0, "y": 0, "width": 100, "height": 100}
        await browsing_module.screenshot(CTX_ID, clip=clip)
        params = mock_connection.send_command.call_args.args[1]
        assert params["clip"] == clip

    async def test_screenshot_without_clip_omits_it(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "base64data"}
        await browsing_module.screenshot(CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert "clip" not in params
