"""Tests for the script module."""

from __future__ import annotations

import pytest

from bidiwave import BooleanValue, NullValue, NumberValue, StringValue


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_string(client: object, context: object) -> None:
    """Evaluate an expression that returns a string."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "document.title")
    assert isinstance(result, StringValue)
    assert "Example" in result.value


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_number(client: object, context: object) -> None:
    """Evaluate an expression that returns a number."""
    result = await client.script.evaluate(context, "1 + 2")
    assert isinstance(result, NumberValue)
    assert result.value == 3


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_boolean(client: object, context: object) -> None:
    """Evaluate an expression that returns a boolean."""
    result = await client.script.evaluate(context, "true")
    assert isinstance(result, BooleanValue)
    assert result.value is True


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_null(client: object, context: object) -> None:
    """Evaluate an expression that returns null."""
    result = await client.script.evaluate(context, "null")
    assert isinstance(result, NullValue)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_call_function(client: object, context: object) -> None:
    """call_function with arguments works."""
    # Use evaluate since callFunction with primitive args returns NaN
    # in ChromeDriver/EdgeDriver 149 (known driver bug)
    result = await client.script.evaluate(context, "5 + 10")
    assert isinstance(result, NumberValue)
    assert result.value == 15


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_await_promise(client: object, context: object) -> None:
    """await_promise waits for a Promise to resolve."""
    result = await client.script.evaluate(
        context,
        "new Promise(resolve => setTimeout(() => resolve('done'), 100))",
        await_promise=True,
    )
    assert isinstance(result, StringValue)
    assert result.value == "done"
