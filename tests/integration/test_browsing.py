"""Tests for the browsing module."""

from __future__ import annotations

import base64

import pytest


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_create_and_close_context(client: object) -> None:
    """Creating and closing a context works."""
    ctx = await client.browsing.create_context()
    assert ctx.id is not None
    await client.browsing.close(ctx)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate(client: object, context: object) -> None:
    """Navigating to a URL works."""
    result = await client.browsing.navigate(context, "https://example.com", wait="complete")
    assert result is not None
    assert result.url == "https://example.com/"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_with_context_manager(client: object) -> None:
    """BrowsingContext context manager works."""
    async with await client.browsing.create_context() as ctx:
        await client.browsing.navigate(ctx, "https://example.com", wait="complete")


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot(client: object, context: object) -> None:
    """Screenshot returns base64 data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.screenshot(context)
    decoded = base64.b64decode(result.data)
    assert len(decoded) > 0
    assert decoded[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree(client: object, context: object) -> None:
    """getTree returns the context tree."""
    tree = await client.browsing.get_tree()
    assert "contexts" in tree
    assert len(tree["contexts"]) >= 1
