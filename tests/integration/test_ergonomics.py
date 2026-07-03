"""Tests de la convenience layer: Page object, wait helpers, context managers."""

from __future__ import annotations

import pytest

from bidiwave import StringValue


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_page_object(client: object) -> None:
    """Page object funciona end-to-end."""
    async with await client.browsing.open("https://example.com") as page:
        title = await page.evaluate("document.title")
        assert isinstance(title, StringValue)
        assert "Example" in title.value

        await page.wait_for_selector("h1", timeout=5)

        screenshot = await page.screenshot()
        assert len(screenshot) > 0
        assert screenshot[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_wait_for_selector(client: object, context: object) -> None:
    """wait_for_selector funciona con timeout."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    found = await client.browsing.wait_for_selector(context, "h1", timeout=5)
    assert found is True


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_wait_for_function(client: object, context: object) -> None:
    """wait_for_function funciona con timeout."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.wait_for_function(
        context,
        "() => document.readyState === 'complete'",
        timeout=5,
    )
    assert result


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_type_narrowing_match(client: object, context: object) -> None:
    """match con subtipos de RemoteValue funciona."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "document.title")

    matched = False
    match result:
        case StringValue(value=title):
            assert "Example" in title
            matched = True
        case _:
            pytest.fail(f"Expected StringValue, got {type(result)}")

    assert matched
