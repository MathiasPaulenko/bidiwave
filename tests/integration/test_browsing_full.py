"""Integration tests for browsingContext module against real Edge browser."""

from __future__ import annotations

import base64

import pytest

from bidiwave.exceptions import CommandError


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_create_context_type_tab(client: object) -> None:
    """Creating a tab context returns a valid context."""
    ctx = await client.browsing.create_context(type="tab")
    assert ctx.id is not None
    assert len(ctx.id) > 0
    await client.browsing.close(ctx)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_create_context_type_window(client: object) -> None:
    """Creating a window context returns a valid context."""
    ctx = await client.browsing.create_context(type="window")
    assert ctx.id is not None
    await client.browsing.close(ctx)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_wait_none(client: object, context: object) -> None:
    """navigate with wait='none' returns immediately without waiting for load."""
    result = await client.browsing.navigate(
        context, "https://example.com", wait="none"
    )
    assert result is not None
    assert result.url is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_wait_interactive(client: object, context: object) -> None:
    """navigate with wait='interactive' waits for DOMContentLoaded."""
    result = await client.browsing.navigate(
        context, "https://example.com", wait="interactive"
    )
    assert result is not None
    assert "example.com" in result.url


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_wait_complete(client: object, context: object) -> None:
    """navigate with wait='complete' waits for full page load."""
    result = await client.browsing.navigate(
        context, "https://example.com", wait="complete"
    )
    assert result is not None
    assert result.url == "https://example.com/"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_about_blank(client: object, context: object) -> None:
    """Navigating to about:blank works."""
    result = await client.browsing.navigate(context, "about:blank", wait="complete")
    assert result.url == "about:blank"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_data_url(client: object, context: object) -> None:
    """Navigating to a data: URL works."""
    result = await client.browsing.navigate(
        context, "data:text/html,<html><body><h1>Test</h1></body></html>", wait="complete"
    )
    assert "data:" in result.url or "Test" in result.url


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_returns_navigation_id(client: object, context: object) -> None:
    """Navigation result includes a navigation id."""
    result = await client.browsing.navigate(
        context, "https://example.com", wait="complete"
    )
    assert result.navigation is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_close_context(client: object) -> None:
    """Closing a context works and removes it from the tree."""
    ctx = await client.browsing.create_context()
    ctx_id = ctx.id
    await client.browsing.close(ctx)
    tree = await client.browsing.get_tree()
    context_ids = [c.context for c in tree.contexts]
    assert ctx_id not in context_ids


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot_png(client: object, context: object) -> None:
    """Screenshot returns valid PNG data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.screenshot(context)
    decoded = base64.b64decode(result.data)
    assert len(decoded) > 0
    assert decoded[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot_jpeg(client: object, context: object) -> None:
    """Screenshot with JPEG format returns valid JPEG data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    try:
        result = await client.browsing.screenshot(context, format="jpeg", quality=50)
    except CommandError as e:
        if "invalid argument" in str(e).lower():
            pytest.skip("EdgeDriver does not support JPEG screenshots")
        raise
    decoded = base64.b64decode(result.data)
    assert len(decoded) > 0
    assert decoded[:3] == b"\xff\xd8\xff"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot_empty_context(client: object) -> None:
    """Screenshot of an empty (about:blank) context works."""
    ctx = await client.browsing.create_context()
    try:
        await client.browsing.navigate(ctx, "about:blank", wait="complete")
        result = await client.browsing.screenshot(ctx)
        decoded = base64.b64decode(result.data)
        assert len(decoded) > 0
    finally:
        await client.browsing.close(ctx)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree_no_params(client: object, context: object) -> None:
    """getTree with no params returns all contexts."""
    tree = await client.browsing.get_tree()
    assert len(tree.contexts) >= 1


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree_with_root(client: object, context: object) -> None:
    """getTree with root returns only that subtree."""
    tree = await client.browsing.get_tree(root=context.id)
    assert len(tree.contexts) >= 1
    assert tree.contexts[0].context == context.id


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree_with_max_depth(client: object, context: object) -> None:
    """getTree with maxDepth=0 returns only the root."""
    tree = await client.browsing.get_tree(root=context.id, max_depth=0)
    assert len(tree.contexts) == 1
    assert tree.contexts[0].context == context.id


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree_max_depth_1(client: object, context: object) -> None:
    """getTree with maxDepth=1 returns root + immediate children."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    tree = await client.browsing.get_tree(root=context.id, max_depth=1)
    assert len(tree.contexts) >= 1


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_reload_default(client: object, context: object) -> None:
    """Reload with default wait='complete' works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.reload(context)
    assert result is not None
    assert "example.com" in result.url


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_reload_wait_none(client: object, context: object) -> None:
    """Reload with wait='none' returns immediately."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.reload(context, wait="none")
    assert result is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_reload_ignore_cache(client: object, context: object) -> None:
    """Reload with ignoreCache=True works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.reload(context, ignore_cache=True)
    assert result is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_traverse_history_back_forward(client: object, context: object) -> None:
    """Navigate to two pages, then traverse back and forward."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.navigate(
        context, "https://www.iana.org/domains/reserved", wait="complete"
    )

    try:
        back_result = await client.browsing.traverse_history(context, "back")
    except CommandError as e:
        if "invalid argument" in str(e).lower():
            pytest.skip("EdgeDriver does not support traverseHistory in this state")
        raise
    assert "example.com" in back_result.url

    forward_result = await client.browsing.traverse_history(context, "forward")
    assert "iana.org" in forward_result.url or "reserved" in forward_result.url


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_traverse_history_back_no_history(client: object, context: object) -> None:
    """Traversing back with no history returns error or same page."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    try:
        result = await client.browsing.traverse_history(context, "back")
    except CommandError as e:
        if "invalid argument" in str(e).lower():
            pytest.skip("EdgeDriver does not support traverseHistory with no history")
        raise
    assert result is not None
    assert result.url is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_default(client: object, context: object) -> None:
    """Print returns valid PDF data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(context)
    decoded = base64.b64decode(result.data)
    assert len(decoded) > 0
    assert decoded[:5] == b"%PDF-"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_landscape(client: object, context: object) -> None:
    """Print with landscape orientation returns valid PDF."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(context, orientation="landscape")
    decoded = base64.b64decode(result.data)
    assert decoded[:5] == b"%PDF-"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_with_margins(client: object, context: object) -> None:
    """Print with custom margins returns valid PDF."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(
        context,
        margin={"top": 0.5, "bottom": 0.5, "left": 0.5, "right": 0.5},
    )
    decoded = base64.b64decode(result.data)
    assert decoded[:5] == b"%PDF-"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_with_page_ranges(client: object, context: object) -> None:
    """Print with page ranges returns valid PDF."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(context, page_ranges=["1"])
    decoded = base64.b64decode(result.data)
    assert decoded[:5] == b"%PDF-"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_with_scale(client: object, context: object) -> None:
    """Print with custom scale returns valid PDF."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(context, scale=0.5)
    decoded = base64.b64decode(result.data)
    assert decoded[:5] == b"%PDF-"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_css(client: object, context: object) -> None:
    """Locate nodes by CSS selector returns matching nodes."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context, {"type": "css", "value": "h1"}
    )
    assert len(result.nodes) >= 1


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_xpath(client: object, context: object) -> None:
    """Locate nodes by XPath returns matching nodes."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context, {"type": "xpath", "value": "//h1"}
    )
    assert len(result.nodes) >= 1


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_inner_text(client: object, context: object) -> None:
    """Locate nodes by innerText returns matching nodes."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context, {"type": "innerText", "value": "Example Domain"}
    )
    assert len(result.nodes) >= 1


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_max_count(client: object, context: object) -> None:
    """maxNodeCount limits the number of returned nodes."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context, {"type": "css", "value": "*"}, max_node_count=3
    )
    assert len(result.nodes) <= 3


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_no_match(client: object, context: object) -> None:
    """Locating non-existent selector returns empty list."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context, {"type": "css", "value": ".nonexistent-class-xyz"}
    )
    assert result.nodes == []


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_activate_context(client: object, context: object) -> None:
    """Activating a context does not error."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.activate(context)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_and_get_viewport(client: object, context: object) -> None:
    """set_viewport followed by get_viewport returns the set values."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.set_viewport(
        context, viewport={"width": 800, "height": 600}, device_pixel_ratio=2.0
    )
    try:
        vp = await client.browsing.get_viewport(context)
    except CommandError as e:
        if "unknown command" in str(e).lower():
            pytest.skip("EdgeDriver does not support browsingContext.getViewport")
        raise
    assert vp.width == 800
    assert vp.height == 600
    assert vp.device_pixel_ratio == 2.0


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_viewport_reset(client: object, context: object) -> None:
    """set_viewport with None resets to default."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.set_viewport(
        context, viewport={"width": 400, "height": 300}
    )
    await client.browsing.set_viewport(context, viewport=None)
    try:
        vp = await client.browsing.get_viewport(context)
    except CommandError as e:
        if "unknown command" in str(e).lower():
            pytest.skip("EdgeDriver does not support browsingContext.getViewport")
        raise
    assert vp.width != 400 or vp.height != 300


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_context_manager_closes_on_exit(client: object) -> None:
    """BrowsingContext as async context manager closes automatically."""
    async with await client.browsing.create_context() as ctx:
        await client.browsing.navigate(ctx, "https://example.com", wait="complete")
    tree = await client.browsing.get_tree()
    context_ids = [c.context for c in tree.contexts]
    assert ctx.id not in context_ids


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_open_page_helper(client: object) -> None:
    """open() creates context, navigates, and returns a Page."""
    page = await client.browsing.open("https://example.com")
    try:
        assert page is not None
        result = await page.evaluate("document.title")
        assert "Example" in result.value
    finally:
        await page.close()


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_multiple_contexts(client: object) -> None:
    """Multiple contexts can coexist."""
    ctx1 = await client.browsing.create_context()
    ctx2 = await client.browsing.create_context()
    try:
        assert ctx1.id != ctx2.id
        await client.browsing.navigate(ctx1, "https://example.com", wait="complete")
        await client.browsing.navigate(
            ctx2, "https://www.iana.org/domains/reserved", wait="complete"
        )
        tree = await client.browsing.get_tree()
        context_ids = [c.context for c in tree.contexts]
        assert ctx1.id in context_ids
        assert ctx2.id in context_ids
    finally:
        await client.browsing.close(ctx1)
        await client.browsing.close(ctx2)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_create_user_context_and_use(client: object) -> None:
    """Creating a user context and using it in a browsing context works."""
    uc = await client.browsing.create_user_context()
    assert uc.user_context is not None
    try:
        ctx = await client.browsing.create_context(user_context=uc.user_context)
        await client.browsing.navigate(ctx, "https://example.com", wait="complete")
        await client.browsing.close(ctx)
    finally:
        await client.browsing.remove_user_context(uc.user_context)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_user_contexts_includes_default(client: object) -> None:
    """get_user_contexts returns at least the default context."""
    contexts = await client.browsing.get_user_contexts()
    assert len(contexts) >= 1
    assert any(uc.user_context == "default" for uc in contexts)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_handle_user_prompt_no_dialog(client: object, context: object) -> None:
    """handle_user_prompt on a context with no dialog raises no such alert."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    with pytest.raises(CommandError, match="no such alert"):
        await client.browsing.handle_user_prompt(context)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_and_reload_cycle(client: object, context: object) -> None:
    """Navigate, reload, navigate again — full cycle works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.reload(context, wait="complete")
    result = await client.browsing.navigate(
        context, "https://www.iana.org/domains/reserved", wait="complete"
    )
    assert "iana.org" in result.url or "reserved" in result.url
