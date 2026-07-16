"""Tests del Page object."""

import base64
from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.convenience.page import Page
from bidiwave.modules.browsing import BrowsingContext
from bidiwave.protocol.remote_value import StringValue


@pytest.mark.asyncio
async def test_page_evaluate_calls_script():
    browsing = MagicMock()
    script = MagicMock()
    script.evaluate = AsyncMock(return_value=StringValue(type="string", value="title"))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, script, ctx)

    result = await page.evaluate("document.title")
    script.evaluate.assert_called_once_with(
        ctx,
        "document.title",
        False,
        sandbox=None,
        serialization_options=None,
        user_activation=False,
    )
    assert isinstance(result, StringValue)
    assert result.value == "title"


@pytest.mark.asyncio
async def test_page_evaluate_with_serialization_options():
    browsing = MagicMock()
    script = MagicMock()
    script.evaluate = AsyncMock(return_value=StringValue(type="string", value="data"))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, script, ctx)

    ser_opts = {"maxObjectDepth": 2}
    await page.evaluate("document.title", serialization_options=ser_opts, user_activation=True)
    script.evaluate.assert_called_once_with(
        ctx,
        "document.title",
        False,
        sandbox=None,
        serialization_options=ser_opts,
        user_activation=True,
    )


@pytest.mark.asyncio
async def test_page_call_with_this_and_serialization():
    browsing = MagicMock()
    script = MagicMock()
    script.call_function = AsyncMock(return_value=StringValue(type="string", value="ok"))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, script, ctx)

    this_val = {"type": "undefined"}
    ser_opts = {"maxObjectDepth": 1}
    await page.call("fn()", this=this_val, serialization_options=ser_opts, user_activation=True)
    script.call_function.assert_called_once_with(
        ctx,
        "fn()",
        None,
        False,
        sandbox=None,
        this=this_val,
        serialization_options=ser_opts,
        user_activation=True,
    )


@pytest.mark.asyncio
async def test_page_screenshot_with_origin():
    browsing = MagicMock()
    screenshot_data = base64.b64encode(b"png-data").decode()
    from bidiwave.protocol.results import Screenshot

    browsing.screenshot = AsyncMock(return_value=Screenshot(data=screenshot_data))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    result = await page.screenshot(origin="document")
    browsing.screenshot.assert_called_once_with(
        ctx, "png", None, None, origin="document"
    )
    assert result == b"png-data"


@pytest.mark.asyncio
async def test_page_locate_nodes_with_start_nodes():
    browsing = MagicMock()
    from bidiwave.protocol.results import LocateNodesResult

    browsing.locate_nodes = AsyncMock(return_value=LocateNodesResult(nodes=[{"sharedId": "n1"}]))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    start_nodes = [{"sharedId": "start-1"}]
    result = await page.locate_nodes({"type": "css", "value": "div"}, start_nodes=start_nodes)
    browsing.locate_nodes.assert_called_once_with(
        ctx,
        {"type": "css", "value": "div"},
        max_node_count=None,
        start_nodes=start_nodes,
    )
    assert len(result) == 1


@pytest.mark.asyncio
async def test_page_screenshot_returns_bytes():
    browsing = MagicMock()
    screenshot_data = base64.b64encode(b"png-data").decode()
    from bidiwave.protocol.results import Screenshot

    browsing.screenshot = AsyncMock(return_value=Screenshot(data=screenshot_data))

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    result = await page.screenshot()
    assert result == b"png-data"


@pytest.mark.asyncio
async def test_page_wait_for_selector_calls_browsing():
    browsing = MagicMock()
    browsing.wait_for_selector = AsyncMock(return_value=True)

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    result = await page.wait_for_selector("h1", timeout=5.0)
    browsing.wait_for_selector.assert_called_once_with(ctx, "h1", 5.0)
    assert result is True


@pytest.mark.asyncio
async def test_page_close_closes_context():
    browsing = MagicMock()
    browsing.close = AsyncMock()

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    await page.close()
    browsing.close.assert_called_once_with(ctx)


@pytest.mark.asyncio
async def test_page_aenter_aexit():
    browsing = MagicMock()
    browsing.close = AsyncMock()

    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    result = await page.__aenter__()
    assert result is page

    await page.__aexit__(None, None, None)
    browsing.close.assert_called_once()


@pytest.mark.asyncio
async def test_page_evaluate_without_script_raises():
    browsing = MagicMock()
    ctx = BrowsingContext(id="ctx1")
    page = Page(browsing, None, ctx)

    with pytest.raises(RuntimeError, match="ScriptModule not available"):
        await page.evaluate("document.title")
