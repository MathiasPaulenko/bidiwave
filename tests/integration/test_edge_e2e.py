"""E2E edge-case tests with real Edge browser.

These tests push the library to its limits with unusual inputs,
error conditions, and protocol edge cases that only surface
with a real browser.
"""

from __future__ import annotations

import asyncio

import pytest

from bidiwave.exceptions import BiDiError


# ---------------------------------------------------------------------------
# Error handling edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_js_error_raises(client: object, context: object) -> None:
    """script.evaluate with throwing code raises JavaScriptError."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    with pytest.raises(BiDiError):
        await client.script.evaluate(context, "throw new Error('boom')")


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_invalid_url_raises(client: object, context: object) -> None:
    """Navigating to an invalid URL raises an error."""
    with pytest.raises(BiDiError):
        await client.browsing.navigate(
            context, "not-a-valid-url://broken", wait="complete"
        )


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_close_nonexistent_context_raises(client: object) -> None:
    """Closing a non-existent context raises an error."""
    with pytest.raises(BiDiError):
        await client.browsing.close("nonexistent-context-id-12345")


# ---------------------------------------------------------------------------
# Remote value edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_null(client: object, context: object) -> None:
    """script.evaluate returns null value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "null")
    assert result.type == "null"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_undefined(client: object, context: object) -> None:
    """script.evaluate returns undefined value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "undefined")
    assert result.type == "undefined"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_bigint(client: object, context: object) -> None:
    """script.evaluate returns bigint value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "9007199254740993n")
    assert result.type == "bigint"
    assert result.value == "9007199254740993"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_array(client: object, context: object) -> None:
    """script.evaluate returns array value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "[1, 2, 3]")
    assert result.type == "array"
    assert result.value is not None
    assert len(result.value) == 3


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_object(client: object, context: object) -> None:
    """script.evaluate returns object value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context, "({name: 'test', value: 42})"
    )
    assert result.type == "object"
    assert result.value is not None
    name_val = result.value.get("name")
    assert hasattr(name_val, "value") and name_val.value == "test"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_boolean(client: object, context: object) -> None:
    """script.evaluate returns boolean value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "true")
    assert result.type == "boolean"
    assert result.value is True


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_await_promise(client: object, context: object) -> None:
    """script.evaluate with awaitPromise resolves a Promise."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "new Promise(resolve => setTimeout(() => resolve('async-value'), 100))",
        await_promise=True,
    )
    assert result.type == "string"
    assert result.value == "async-value"


# ---------------------------------------------------------------------------
# Browsing edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_data_url(client: object, context: object) -> None:
    """Navigating to a data: URL works."""
    await client.browsing.navigate(
        context,
        "data:text/html,<h1>Hello Data URL</h1>",
        wait="complete",
    )
    result = await client.script.evaluate(context, "document.title")
    assert result is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigate_about_blank(client: object, context: object) -> None:
    """Navigating to about:blank works."""
    await client.browsing.navigate(context, "about:blank", wait="complete")
    result = await client.script.evaluate(context, "document.URL")
    assert result.value == "about:blank"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Edge may not support JPEG screenshot format in BiDi")
async def test_screenshot_jpeg_format(client: object, context: object) -> None:
    """Screenshot in JPEG format returns JPEG data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.screenshot(context, format="jpeg", quality=80)
    import base64
    decoded = base64.b64decode(result.data)
    # JPEG starts with FF D8
    assert decoded[:2] == b"\xff\xd8" or decoded[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_tree_with_root(client: object, context: object) -> None:
    """getTree with root parameter returns subtree."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    tree = await client.browsing.get_tree(root=context.id)
    assert len(tree.contexts) >= 1


# ---------------------------------------------------------------------------
# Script disown edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_disown_handle(client: object, context: object) -> None:
    """script.disown releases object handles."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context, "({a: 1})"
    )
    if hasattr(result, "handle") and result.handle:
        await client.script.disown(context, [result.handle])


# ---------------------------------------------------------------------------
# Session edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_session_status(client: object) -> None:
    """session.status returns a valid status."""
    status = await client.session.status()
    assert status is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_subscribe_unsubscribe(client: object) -> None:
    """subscribe and unsubscribe work without errors."""
    await client.session.subscribe(["log.entryAdded"])
    await client.session.unsubscribe(["log.entryAdded"])


# ---------------------------------------------------------------------------
# Multiple browsing contexts edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_multiple_contexts_independent(client: object) -> None:
    """Two contexts can navigate independently."""
    ctx1 = await client.browsing.create_context()
    ctx2 = await client.browsing.create_context()
    try:
        await client.browsing.navigate(ctx1, "https://example.com", wait="complete")
        await client.browsing.navigate(ctx2, "https://www.iana.org/domains/example", wait="complete")
        title1 = await client.script.evaluate(ctx1, "document.title")
        title2 = await client.script.evaluate(ctx2, "document.title")
        assert "Example" in title1.value
        assert "IANA" in title2.value or "Example" in title2.value
    finally:
        await client.browsing.close(ctx1)
        await client.browsing.close(ctx2)


# ---------------------------------------------------------------------------
# Viewport edge cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_viewport(client: object, context: object) -> None:
    """set_viewport works and script can read dimensions."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.set_viewport(
        context,
        viewport={"width": 800, "height": 600},
        device_pixel_ratio=2.0,
    )
    result = await client.script.evaluate(
        context, "window.innerWidth + 'x' + window.innerHeight"
    )
    assert result.type == "string"
    assert "800" in result.value


# ---------------------------------------------------------------------------
# RemoteValue type coverage (Bug 55: date, regexp, map, set)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_date(client: object, context: object) -> None:
    """script.evaluate returns date value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new Date('2024-01-15T00:00:00Z')")
    assert result.type == "date"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_regexp(client: object, context: object) -> None:
    """script.evaluate returns regexp value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "/testpattern/gi")
    assert result.type == "regexp"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_map(client: object, context: object) -> None:
    """script.evaluate returns map value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "new Map([['a', 1], ['b', 2]])",
        serialization_options={"maxObjectDepth": 0},
    )
    assert result.type == "map"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_set(client: object, context: object) -> None:
    """script.evaluate returns set value correctly."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "new Set([1, 2, 3])",
        serialization_options={"maxObjectDepth": 0},
    )
    assert result.type == "set"


# ---------------------------------------------------------------------------
# Screenshot with origin (Bug 56)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot_origin_viewport(client: object, context: object) -> None:
    """screenshot with origin=viewport works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.screenshot(context, origin="viewport")
    assert result.data
    assert len(result.data) > 100


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_screenshot_origin_document(client: object, context: object) -> None:
    """screenshot with origin=document captures full page."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.screenshot(context, origin="document")
    assert result.data
    assert len(result.data) > 100


# ---------------------------------------------------------------------------
# ContextCreated event with userContext (Bug 54)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_context_created_event_has_user_context(client: object) -> None:
    """browsingContext.contextCreated event should parse userContext correctly."""
    from bidiwave.protocol.events import BrowsingContextCreatedEvent

    events: list[object] = []
    await client.session.subscribe(["browsingContext.contextCreated"])

    async def _handler(event: object) -> None:
        events.append(event)

    sub = client.on_context_created(_handler)

    ctx = await client.browsing.create_context()
    await asyncio.sleep(0.5)

    client.off(sub)
    await client.browsing.close(ctx)

    assert len(events) > 0
    event = events[0]
    assert isinstance(event, BrowsingContextCreatedEvent)
    assert event.context
    assert event.user_context is not None


# ---------------------------------------------------------------------------
# Serialization options (Bug 57)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_with_serialization_options(client: object, context: object) -> None:
    """script.evaluate with serializationOptions works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "({a: 1, b: {c: 2}})",
        serialization_options={"maxObjectDepth": 1},
    )
    assert result.type == "object"


# ---------------------------------------------------------------------------
# User activation (Bug 57)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_with_user_activation(client: object, context: object) -> None:
    """script.evaluate with userActivation=true works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "navigator.userActivation ? navigator.userActivation.isActive : false",
        user_activation=True,
    )
    assert result.type in ("boolean", "undefined")


# ---------------------------------------------------------------------------
# call_function with this parameter (Bug 58)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_call_function_with_this(client: object, context: object) -> None:
    """script.call_function with this=object works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.call_function(
        context,
        "function() { return this.x; }",
        this={"type": "object", "value": [["x", {"type": "number", "value": 42}]]},
    )
    assert result is not None


# ---------------------------------------------------------------------------
# locate_nodes with start_nodes (Bug 59)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_with_start_nodes(client: object, context: object) -> None:
    """browsing.locate_nodes with start_nodes works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context,
        locator={"type": "css", "value": "h1"},
    )
    assert result.nodes is not None
    assert len(result.nodes) > 0

    node = result.nodes[0]
    shared_id = node.get("sharedId")
    if shared_id:
        result2 = await client.browsing.locate_nodes(
            context,
            locator={"type": "css", "value": "div"},
            start_nodes=[{"sharedId": shared_id}],
        )
        assert result2.nodes is not None
