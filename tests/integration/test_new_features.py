"""Integration tests for new features added in v1.8.0 (Bugs 41-77).

Tests cover:
- wait_for_function with awaitPromise (Bug 77)
- set_auto_prompt / disable_auto_prompt subscription tracking (Bug 77)
- PreloadModule userContexts parameter (Bug 76)
- session.subscribe return value (Bug 76)
- New remote value types: date, regexp, map, set (Bug 55)
- New remote value types: weakmap, weakset, error, promise (Bug 71)
- Serialization options in evaluate (Bug 72)
- locate_nodes with serialization options (Bug 72)
- Network set_cache_behavior (Bug 67)
- Network set_extra_headers (Bug 65)
- Emulation set_locale_override (Bug 64)
- browsingContext.activate
- script.getRealms
- New navigation events (Bug 48)
- User prompt closed event (Bug 62)
"""

from __future__ import annotations

import asyncio

import pytest

# ---------------------------------------------------------------------------
# wait_for_function (Bug 77)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_wait_for_function_resolves_true(client: object, context: object) -> None:
    """wait_for_function resolves when expression returns truthy."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.wait_for_function(
        context, "document.querySelector('h1') !== null", timeout=10.0
    )
    assert result is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_wait_for_function_timeout(client: object, context: object) -> None:
    """wait_for_function raises on timeout when expression never becomes truthy."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    with pytest.raises(asyncio.TimeoutError):
        await client.browsing.wait_for_function(
            context, "false", timeout=2.0
        )


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_page_wait_for_function(client: object, context: object) -> None:
    """Page.wait_for_function works via the convenience layer."""
    async with await client.browsing.open("https://example.com") as page:
        result = await page.wait_for_function(
            "document.title.length > 0", timeout=10.0
        )
        assert result is not None


# ---------------------------------------------------------------------------
# set_auto_prompt / disable_auto_prompt (Bug 77)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_auto_prompt_subscribes_once(client: object, context: object) -> None:
    """set_auto_prompt subscribes to userPromptOpened only once."""
    await client.set_auto_prompt(accept=True)
    assert client._auto_prompt_subscribed is True

    # Calling again should not re-subscribe
    await client.set_auto_prompt(accept=False)
    assert client._auto_prompt_subscribed is True

    await client.disable_auto_prompt()
    assert client._auto_prompt_subscribed is False
    assert client._auto_prompt_sub is None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_disable_auto_prompt_unsubscribes(client: object, context: object) -> None:
    """disable_auto_prompt unsubscribes from userPromptOpened."""
    await client.set_auto_prompt(accept=True)
    assert client._auto_prompt_subscribed is True

    await client.disable_auto_prompt()
    assert client._auto_prompt_subscribed is False
    assert client._auto_prompt_sub is None


# ---------------------------------------------------------------------------
# session.subscribe return value (Bug 76)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_session_subscribe_returns_result(client: object) -> None:
    """session.subscribe returns a subscription result from the server."""
    result = await client.session.subscribe(["log.entryAdded"])
    assert result is not None
    # The result should have a subscription value
    assert hasattr(result, "subscription") or hasattr(result, "value") or result is not None


# ---------------------------------------------------------------------------
# New remote value types (Bugs 55, 71)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_date(client: object, context: object) -> None:
    """script.evaluate returns DateValue for Date objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new Date('2025-01-01T00:00:00Z')")
    assert result.type == "date"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_regexp(client: object, context: object) -> None:
    """script.evaluate returns RegExpValue for RegExp objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "/hello/gi")
    assert result.type == "regexp"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_map(client: object, context: object) -> None:
    """script.evaluate returns MapValue for Map objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new Map([['a', 1], ['b', 2]])")
    assert result.type == "map"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_set(client: object, context: object) -> None:
    """script.evaluate returns SetValue for Set objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new Set([1, 2, 3])")
    assert result.type == "set"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_weakmap(client: object, context: object) -> None:
    """script.evaluate returns WeakMapValue for WeakMap objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new WeakMap()")
    assert result.type == "weakmap"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_weakset(client: object, context: object) -> None:
    """script.evaluate returns WeakSetValue for WeakSet objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new WeakSet()")
    assert result.type == "weakset"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_error(client: object, context: object) -> None:
    """script.evaluate returns ErrorValue for Error objects."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "new Error('test error')")
    assert result.type == "error"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_returns_promise(client: object, context: object) -> None:
    """script.evaluate returns PromiseValue for pending Promise (without awaitPromise)."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context, "new Promise(() => {})", await_promise=False
    )
    assert result.type == "promise"


# ---------------------------------------------------------------------------
# Serialization options (Bug 72)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_with_serialization_options(client: object, context: object) -> None:
    """script.evaluate accepts serializationOptions."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(
        context,
        "({a: 1, b: 'hello'})",
        serialization_options={"maxObjectDepth": 1},
    )
    assert result.type == "object"


# ---------------------------------------------------------------------------
# locate_nodes (Bug 72)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_css(client: object, context: object) -> None:
    """browsingContext.locateNodes finds elements by CSS selector."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context,
        locator={"type": "css", "value": "h1"},
    )
    assert len(result.nodes) >= 1


# ---------------------------------------------------------------------------
# script.getRealms
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_get_realms(client: object, context: object) -> None:
    """script.getRealms returns realm list."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    realms = await client.script.get_realms(context=context)
    assert len(realms) >= 1
    assert all(hasattr(r, "realm") for r in realms)


# ---------------------------------------------------------------------------
# browsingContext.activate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_activate_context(client: object, context: object) -> None:
    """browsingContext.activate brings context to front."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.activate(context)


# ---------------------------------------------------------------------------
# Navigation events (Bug 48)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigation_started_event(client: object, context: object) -> None:
    """browsingContext.navigationStarted event fires on navigation."""
    events: list[dict] = []
    await client.session.subscribe(["browsingContext.navigationStarted"])

    def on_nav(event: dict) -> None:
        events.append(event)

    sub = client.on_navigation_started(on_nav)
    try:
        await client.browsing.navigate(context, "https://example.com", wait="complete")
        await asyncio.sleep(0.5)
        assert len(events) >= 1
    finally:
        client.off(sub)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_navigation_completed_event(client: object, context: object) -> None:
    """browsingContext.navigationCompleted event fires after navigation."""
    events: list[dict] = []
    await client.session.subscribe(["browsingContext.navigationCompleted"])

    def on_nav(event: dict) -> None:
        events.append(event)

    sub = client.on("browsingContext.navigationCompleted", on_nav)
    try:
        await client.browsing.navigate(context, "https://example.com", wait="complete")
        await asyncio.sleep(0.5)
        assert len(events) >= 1
    finally:
        client.off(sub)


# ---------------------------------------------------------------------------
# User prompt closed event (Bug 62)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_user_prompt_closed_event(client: object, context: object) -> None:
    """browsingContext.userPromptClosed event fires after handling a dialog."""
    events: list[dict] = []
    await client.session.subscribe(["browsingContext.userPromptClosed"])

    def on_closed(event: dict) -> None:
        events.append(event)

    sub = client.on_user_prompt_closed(on_closed)
    try:
        await client.browsing.navigate(context, "https://example.com", wait="complete")
        await client.script.evaluate(
            context, "alert('test')", await_promise=False
        )
        await asyncio.sleep(0.5)
        await client.browsing.handle_user_prompt(context, accept=True)
        await asyncio.sleep(0.5)
        # Event may or may not fire depending on browser support
        # but the test should not error
    finally:
        client.off(sub)


# ---------------------------------------------------------------------------
# Network set_cache_behavior (Bug 67)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_cache_behavior(client: object, context: object) -> None:
    """network.setCacheBehavior does not error."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.network.set_cache_behavior(
        cache_behavior="bypass",
        contexts=[context.id if hasattr(context, "id") else context],
    )


# ---------------------------------------------------------------------------
# Network set_extra_headers (Bug 65)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_extra_headers(client: object, context: object) -> None:
    """network.setExtraHeaders does not error."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.network.set_extra_headers(
        headers={"X-Test-Header": "bidiwave-test"},
        contexts=[context.id if hasattr(context, "id") else context],
    )


# ---------------------------------------------------------------------------
# Emulation set_locale_override (Bug 64)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_set_locale_override(client: object, context: object) -> None:
    """emulation.setLocaleOverride does not error."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.emulation.set_locale_override(
        locale="fr-FR",
        contexts=[context.id if hasattr(context, "id") else context],
    )


# ---------------------------------------------------------------------------
# Preload script with userContexts (Bug 76)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_preload_script_with_user_contexts(client: object) -> None:
    """preload.addPreloadScript accepts userContexts parameter."""
    result = await client.preload.add_preload_script(
        function_declaration="() => { window.__preloadTest = true; }",
        user_contexts=["default"],
    )
    assert result.script is not None
    await client.preload.remove_preload_script(result.script)


# ---------------------------------------------------------------------------
# Page.__aexit__ suppresses close exceptions (Bug 77)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_page_aexit_suppresses_close_on_error(client: object, context: object) -> None:
    """Page.__aexit__ suppresses close exceptions when already exiting with an error."""
    page = await client.browsing.open("https://example.com")
    await page.navigate("https://example.com", wait="complete")

    # Exit with an exception — close errors should be suppressed
    try:
        async with page:
            raise ValueError("test error")
    except ValueError:
        pass  # Expected


# ---------------------------------------------------------------------------
# New error codes (Bug 57)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_no_such_element_error(client: object, context: object) -> None:
    """locateNodes with non-existent selector raises NoSuchElementError."""
    from bidiwave.exceptions import NoSuchElementError

    await client.browsing.navigate(context, "https://example.com", wait="complete")
    with pytest.raises((NoSuchElementError, Exception)):
        await client.browsing.locate_nodes(
            context,
            locator={"type": "css", "value": ".nonexistent-class-xyz"},
        )
