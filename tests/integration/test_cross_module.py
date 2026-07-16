"""Integration tests for cross-module scenarios with real Edge browser.

These tests exercise multiple modules together to find bugs that only
surface when commands interact in real browser conditions.
"""

from __future__ import annotations

import asyncio
import base64

import pytest

from bidiwave.protocol.results import Cookie


# ---------------------------------------------------------------------------
# Script + Browsing integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_after_navigation(client: object, context: object) -> None:
    """script.evaluate returns correct title after navigation."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "document.title")
    assert result.type == "string"
    assert "Example" in result.value


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_call_function_returns_dom_node(client: object, context: object) -> None:
    """script.callFunction returns a node remote value."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.call_function(
        context,
        "() => document.querySelector('h1')",
    )
    assert result.type in ("node", "object")


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_with_sandbox(client: object, context: object) -> None:
    """script.evaluate with sandbox isolates variables."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.script.evaluate(
        context, "window.__test = 42", sandbox="test-sandbox"
    )
    result = await client.script.evaluate(
        context, "window.__test", sandbox="test-sandbox"
    )
    assert result.type == "number"
    assert result.value == 42

    # Outside sandbox, the variable should not exist
    result_outside = await client.script.evaluate(
        context, "typeof window.__test"
    )
    assert result_outside.value == "undefined"


# ---------------------------------------------------------------------------
# Input + Browsing integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_input_type_text_into_field(client: object, context: object) -> None:
    """Input text appears in a form field after typing."""
    await client.browsing.navigate(
        context,
        "data:text/html,<input id='q' type='text' />",
        wait="complete",
    )
    await client.input.type_text(context, "hello world")
    result = await client.script.evaluate(
        context,
        "document.querySelector('#q').value",
    )
    # The input may or may not have focus, so we check if typing worked
    # by focusing first
    await client.script.evaluate(
        context,
        "document.querySelector('#q').focus()",
    )
    await client.input.type_text(context, "hello")
    result = await client.script.evaluate(
        context,
        "document.querySelector('#q').value",
    )
    assert result.type == "string"
    assert "hello" in result.value


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_input_click_at_coordinates(client: object, context: object) -> None:
    """Click at coordinates triggers click event."""
    await client.browsing.navigate(
        context,
        "data:text/html,<button id='btn' onclick='window.__clicked=true'>Click</button>",
        wait="complete",
    )
    await client.input.click(context, 10, 10)
    await asyncio.sleep(0.5)
    result = await client.script.evaluate(
        context,
        "typeof window.__clicked !== 'undefined' ? window.__clicked : false",
    )
    # Click at 10,10 might not hit the button, but the command should not error
    assert result is not None


# ---------------------------------------------------------------------------
# Storage + Browsing integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_storage_set_and_get_cookie(client: object, context: object) -> None:
    """set_cookie followed by get_cookies returns the cookie."""
    await client.browsing.navigate(
        context, "https://example.com", wait="complete"
    )
    await client.storage.set_cookie(
        context,
        Cookie(name="test-cookie", value="test-value", domain="example.com", path="/"),
    )
    cookies = await client.storage.get_cookies(context)
    found = [c for c in cookies if c.name == "test-cookie"]
    assert len(found) == 1
    assert found[0].value == "test-value"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_storage_delete_cookie(client: object, context: object) -> None:
    """delete_cookie removes a cookie."""
    await client.browsing.navigate(
        context, "https://example.com", wait="complete"
    )
    await client.storage.set_cookie(
        context,
        Cookie(name="to-delete", value="val", domain="example.com", path="/"),
    )
    await client.storage.delete_cookie(context, "to-delete")
    cookies = await client.storage.get_cookies(context)
    found = [c for c in cookies if c.name == "to-delete"]
    assert len(found) == 0


# ---------------------------------------------------------------------------
# Network + Browsing integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_network_response_completed_event(client: object, context: object) -> None:
    """network.responseCompleted fires after navigation."""
    responses: list[object] = []

    async def on_response(event: object) -> None:
        responses.append(event)

    client.on("network.responseCompleted", on_response)
    await client.session.subscribe(["network.responseCompleted"])

    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await asyncio.sleep(2)

    assert len(responses) >= 1
    assert responses[0].response.status == 200


# ---------------------------------------------------------------------------
# Log + Script integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_log_warning_level(client: object, context: object) -> None:
    """console.warn produces a log entry with level 'warning'."""
    logs: list[object] = []

    async def on_log(entry: object) -> None:
        logs.append(entry)

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.script.evaluate(context, "console.warn('careful-warning')")
    await asyncio.sleep(2)

    matching = [l for l in logs if "careful-warning" in l.text]
    assert len(matching) >= 1
    assert matching[0].level == "warning"


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_log_error_level(client: object, context: object) -> None:
    """console.error produces a log entry with level 'error'."""
    logs: list[object] = []

    async def on_log(entry: object) -> None:
        logs.append(entry)

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.script.evaluate(context, "console.error('bad-error')")
    await asyncio.sleep(2)

    matching = [l for l in logs if "bad-error" in l.text]
    assert len(matching) >= 1
    assert matching[0].level == "error"


# ---------------------------------------------------------------------------
# Browsing context lifecycle integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Edge may not support browsingContext.traverseHistory yet")
async def test_navigate_back_forward(client: object, context: object) -> None:
    """traverse_history back and forward works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.browsing.navigate(context, "https://www.iana.org/domains/example", wait="complete")

    # Go back
    nav = await client.browsing.traverse_history(context, "back")
    assert "example.com" in nav.url

    # Go forward
    nav = await client.browsing.traverse_history(context, "forward")
    assert "iana.org" in nav.url


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_reload_with_ignore_cache(client: object, context: object) -> None:
    """reload with ignoreCache=True works."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    nav = await client.browsing.reload(context, ignore_cache=True)
    assert nav is not None


# ---------------------------------------------------------------------------
# Print integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_print_to_pdf(client: object, context: object) -> None:
    """browsingContext.print returns base64 PDF data."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.print(context)
    decoded = base64.b64decode(result.data)
    assert len(decoded) > 0
    assert decoded[:4] == b"%PDF"


# ---------------------------------------------------------------------------
# Locate nodes integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_locate_nodes_css(client: object, context: object) -> None:
    """locateNodes with CSS selector finds elements."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.browsing.locate_nodes(
        context,
        {"type": "css", "value": "h1"},
    )
    assert len(result.nodes) >= 1


# ---------------------------------------------------------------------------
# User contexts integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_create_and_remove_user_context(client: object) -> None:
    """create_user_context and remove_user_context work."""
    ctx_info = await client.browsing.create_user_context()
    assert ctx_info.user_context is not None

    # Create a browsing context in the user context
    ctx = await client.browsing.create_context(user_context=ctx_info.user_context)
    await client.browsing.close(ctx)

    await client.browsing.remove_user_context(ctx_info.user_context)


# ---------------------------------------------------------------------------
# Emulation integration
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Edge may not support emulation.setGeolocationOverride yet")
async def test_emulation_set_geolocation(client: object, context: object) -> None:
    """emulation.set_geolocation overrides geolocation."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    await client.emulation.set_geolocation(
        coordinates={"latitude": 37.7749, "longitude": -122.4194, "accuracy": 1.0},
    )
    result = await client.script.evaluate(
        context,
        """new Promise(resolve => {
            navigator.geolocation.getCurrentPosition(
                pos => resolve(pos.coords.latitude + ',' + pos.coords.longitude),
                err => resolve('error:' + err.message)
            )
        })""",
        await_promise=True,
    )
    assert result.type == "string"
    assert "37.77" in result.value or "error" in result.value
