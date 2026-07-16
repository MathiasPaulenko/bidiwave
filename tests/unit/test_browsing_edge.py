"""Edge-case unit tests for BrowsingModule.

create, navigate, close, screenshot, get_tree, viewport, open, context manager.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingContext, BrowsingModule
from bidiwave.protocol.commands import ViewportSize
from bidiwave.protocol.results import Navigation, Screenshot

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


class TestCreateContext:
    async def test_create_context_default_type(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID, "url": ""}
        ctx = await browsing_module.create_context()
        assert ctx.id == CTX_ID
        assert ctx.url == ""
        params = mock_connection.send_command.call_args.args[1]
        assert params["type"] == "tab"

    async def test_create_context_window(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": "win-1", "url": ""}
        ctx = await browsing_module.create_context(type="window")
        assert ctx.id == "win-1"
        params = mock_connection.send_command.call_args.args[1]
        assert params["type"] == "window"

    async def test_create_context_with_user_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID, "url": ""}
        await browsing_module.create_context(user_context="uc-1")
        params = mock_connection.send_command.call_args.args[1]
        assert params["userContext"] == "uc-1"

    async def test_create_context_no_user_context_omitted(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID, "url": ""}
        await browsing_module.create_context()
        params = mock_connection.send_command.call_args.args[1]
        assert "userContext" not in params

    async def test_create_context_returns_browsing_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID, "url": "https://example.com"}
        ctx = await browsing_module.create_context()
        assert isinstance(ctx, BrowsingContext)
        assert ctx._module is browsing_module

    async def test_create_context_returns_user_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "",
            "userContext": "uc-1",
        }
        ctx = await browsing_module.create_context(user_context="uc-1")
        assert ctx.user_context == "uc-1"

    async def test_create_context_user_context_none_when_absent(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID, "url": ""}
        ctx = await browsing_module.create_context()
        assert ctx.user_context is None

    async def test_create_context_url_missing(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": CTX_ID}
        ctx = await browsing_module.create_context()
        assert ctx.url == ""


class TestNavigate:
    async def test_navigate_wait_none(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-1",
        }
        result = await browsing_module.navigate(CTX_ID, "https://example.com", wait="none")
        assert isinstance(result, Navigation)
        params = mock_connection.send_command.call_args.args[1]
        assert params["wait"] == "none"

    async def test_navigate_wait_interactive(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        await browsing_module.navigate(CTX_ID, "https://example.com", wait="interactive")
        params = mock_connection.send_command.call_args.args[1]
        assert params["wait"] == "interactive"

    async def test_navigate_default_wait_complete(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        await browsing_module.navigate(CTX_ID, "https://example.com")
        params = mock_connection.send_command.call_args.args[1]
        assert params["wait"] == "complete"

    async def test_navigate_with_browsing_context_object(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        ctx = BrowsingContext(id=CTX_ID)
        await browsing_module.navigate(ctx, "https://example.com")
        params = mock_connection.send_command.call_args.args[1]
        assert params["context"] == CTX_ID

    async def test_navigate_with_navigation_id(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-abc-123",
        }
        result = await browsing_module.navigate(CTX_ID, "https://example.com")
        assert result.navigation == "nav-abc-123"

    async def test_navigate_about_blank(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "about:blank",
        }
        result = await browsing_module.navigate(CTX_ID, "about:blank")
        assert result.url == "about:blank"

    async def test_navigate_no_navigation_id(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": CTX_ID,
            "url": "https://example.com/",
        }
        result = await browsing_module.navigate(CTX_ID, "https://example.com")
        assert result.navigation is None


class TestClose:
    async def test_close_with_str(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.close(CTX_ID)
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.close", {"context": CTX_ID}
        )

    async def test_close_with_browsing_context_object(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = BrowsingContext(id=CTX_ID)
        await browsing_module.close(ctx)
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.close", {"context": CTX_ID}
        )


class TestScreenshot:
    async def test_screenshot_default_png(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "iVBORw0KGgo="}
        result = await browsing_module.screenshot(CTX_ID)
        assert isinstance(result, Screenshot)
        assert result.data == "iVBORw0KGgo="
        params = mock_connection.send_command.call_args.args[1]
        assert "format" not in params
        assert "quality" not in params

    async def test_screenshot_jpeg(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "/9j/4AAQ="}
        await browsing_module.screenshot(CTX_ID, format="jpeg")
        params = mock_connection.send_command.call_args.args[1]
        assert params["format"] == "jpeg"

    async def test_screenshot_jpeg_with_quality(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "/9j/4AAQ="}
        await browsing_module.screenshot(CTX_ID, format="jpeg", quality=50)
        params = mock_connection.send_command.call_args.args[1]
        assert params["quality"] == 50

    async def test_screenshot_quality_ignored_for_png(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "iVBORw0KGgo="}
        await browsing_module.screenshot(CTX_ID, format="png", quality=50)
        params = mock_connection.send_command.call_args.args[1]
        assert "quality" not in params

    async def test_screenshot_with_browsing_context_object(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "iVBORw0KGgo="}
        ctx = BrowsingContext(id=CTX_ID)
        await browsing_module.screenshot(ctx)
        params = mock_connection.send_command.call_args.args[1]
        assert params["context"] == CTX_ID

    async def test_screenshot_with_origin(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "iVBORw0KGgo="}
        await browsing_module.screenshot(CTX_ID, origin="document")
        params = mock_connection.send_command.call_args.args[1]
        assert params["origin"] == "document"

    async def test_screenshot_with_clip_and_origin(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"data": "iVBORw0KGgo="}
        clip = {"type": "box", "x": 0, "y": 0, "width": 100, "height": 100}
        await browsing_module.screenshot(CTX_ID, clip=clip, origin="viewport")
        params = mock_connection.send_command.call_args.args[1]
        assert params["clip"] == clip
        assert params["origin"] == "viewport"


class TestCreateContextExtended:
    async def test_create_context_with_reference_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": "new-ctx"}
        await browsing_module.create_context(reference_context=CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert params["referenceContext"] == CTX_ID

    async def test_create_context_with_background(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": "new-ctx"}
        await browsing_module.create_context(background=True)
        params = mock_connection.send_command.call_args.args[1]
        assert params["background"] is True

    async def test_create_context_no_reference_context_omitted(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"context": "new-ctx"}
        await browsing_module.create_context()
        params = mock_connection.send_command.call_args.args[1]
        assert "referenceContext" not in params
        assert "background" not in params


class TestGetTree:
    async def test_get_tree_no_params(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"contexts": []}
        result = await browsing_module.get_tree()
        assert result.contexts == []
        params = mock_connection.send_command.call_args.args[1]
        assert params == {}

    async def test_get_tree_with_root(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"contexts": [{"context": CTX_ID}]}
        result = await browsing_module.get_tree(root=CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert params["root"] == CTX_ID
        assert len(result.contexts) == 1
        assert result.contexts[0].context == CTX_ID

    async def test_get_tree_with_max_depth(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"contexts": []}
        await browsing_module.get_tree(max_depth=2)
        params = mock_connection.send_command.call_args.args[1]
        assert params["maxDepth"] == 2

    async def test_get_tree_with_root_and_max_depth(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"contexts": []}
        await browsing_module.get_tree(root=CTX_ID, max_depth=3)
        params = mock_connection.send_command.call_args.args[1]
        assert params["root"] == CTX_ID
        assert params["maxDepth"] == 3


class TestSetViewportEdge:
    async def test_set_viewport_with_viewport_size_object(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        vs = ViewportSize(width=1024, height=768)
        await browsing_module.set_viewport(CTX_ID, viewport=vs)
        params = mock_connection.send_command.call_args.args[1]
        assert params["viewport"] == {"width": 1024, "height": 768}

    async def test_set_viewport_with_dict(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(CTX_ID, viewport={"width": 800, "height": 600})
        params = mock_connection.send_command.call_args.args[1]
        assert params["viewport"] == {"width": 800, "height": 600}

    async def test_set_viewport_only_dpr(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(CTX_ID, device_pixel_ratio=3.0)
        params = mock_connection.send_command.call_args.args[1]
        assert "viewport" not in params
        assert params["devicePixelRatio"] == 3.0

    async def test_set_viewport_both_none(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(CTX_ID)
        params = mock_connection.send_command.call_args.args[1]
        assert "viewport" not in params
        assert "devicePixelRatio" not in params

    async def test_set_viewport_with_browsing_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = BrowsingContext(id=CTX_ID)
        await browsing_module.set_viewport(ctx, viewport={"width": 100, "height": 100})
        params = mock_connection.send_command.call_args.args[1]
        assert params["context"] == CTX_ID


class TestGetViewportEdge:
    async def test_get_viewport_with_browsing_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "viewport": {"width": 1920, "height": 1080, "devicePixelRatio": 1.0},
        }
        ctx = BrowsingContext(id=CTX_ID)
        result = await browsing_module.get_viewport(ctx)
        assert result.width == 1920
        assert result.height == 1080

    async def test_get_viewport_default_dpr(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "viewport": {"width": 800, "height": 600},
        }
        result = await browsing_module.get_viewport(CTX_ID)
        assert result.device_pixel_ratio == 1.0


class TestBrowsingContextManager:
    async def test_aexit_closes_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = BrowsingContext(id=CTX_ID, _module=browsing_module)
        async with ctx:
            pass
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.close", {"context": CTX_ID}
        )

    async def test_aexit_without_module_does_nothing(
        self,
        mock_connection: MockConn,
    ) -> None:
        ctx = BrowsingContext(id=CTX_ID, _module=None)
        async with ctx:
            pass
        mock_connection.send_command.assert_not_called()

    async def test_aexit_reraises_on_exception(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = BrowsingContext(id=CTX_ID, _module=browsing_module)
        with pytest.raises(ValueError, match="test error"):
            async with ctx:
                raise ValueError("test error")
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.close", {"context": CTX_ID}
        )

    async def test_aexit_reraises_close_error_on_success(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.side_effect = RuntimeError("close failed")
        ctx = BrowsingContext(id=CTX_ID, _module=browsing_module)
        with pytest.raises(RuntimeError, match="close failed"):
            async with ctx:
                pass
        mock_connection.send_command.assert_called_once()

    async def test_aexit_reraises_original_on_close_error_with_exception(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.side_effect = RuntimeError("close failed")
        ctx = BrowsingContext(id=CTX_ID, _module=browsing_module)
        with pytest.raises(ValueError, match="original"):
            async with ctx:
                raise ValueError("original")


class TestOpen:
    async def test_open_success(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.side_effect = [
            {"context": CTX_ID, "url": ""},
            {"context": CTX_ID, "url": "https://example.com/", "navigation": "nav-1"},
        ]
        page = await browsing_module.open("https://example.com")
        assert page is not None
        assert page._context.id == CTX_ID

    async def test_open_navigation_failure_closes_context(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.side_effect = [
            {"context": CTX_ID, "url": ""},
            RuntimeError("navigation failed"),
            None,
        ]
        with pytest.raises(RuntimeError, match="navigation failed"):
            await browsing_module.open("https://invalid.url")
        close_call = mock_connection.send_command.call_args_list[-1]
        assert close_call.args[0] == "browsingContext.close"

    async def test_open_with_wait_none(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.side_effect = [
            {"context": CTX_ID, "url": ""},
            {"context": CTX_ID, "url": "https://example.com/"},
        ]
        await browsing_module.open("https://example.com", wait="none")
        nav_call = mock_connection.send_command.call_args_list[1]
        assert nav_call.args[1]["wait"] == "none"


class TestNavigateModelValidation:
    def test_navigation_with_all_fields(self) -> None:
        nav = Navigation.model_validate({
            "context": CTX_ID,
            "url": "https://example.com/",
            "navigation": "nav-1",
            "status": "complete",
        })
        assert nav.context == CTX_ID
        assert nav.url == "https://example.com/"
        assert nav.navigation == "nav-1"
        assert nav.status == "complete"

    def test_navigation_minimal(self) -> None:
        nav = Navigation.model_validate({"url": "about:blank"})
        assert nav.url == "about:blank"
        assert nav.context is None
        assert nav.navigation is None

    def test_navigation_default_status(self) -> None:
        nav = Navigation.model_validate({"url": "https://example.com/"})
        assert nav.status == "complete"
