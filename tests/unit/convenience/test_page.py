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
    script.evaluate.assert_called_once_with(ctx, "document.title", False, sandbox=None)
    assert isinstance(result, StringValue)
    assert result.value == "title"


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
