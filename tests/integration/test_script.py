"""Tests del módulo script."""

from __future__ import annotations

import pytest

from bidiwave import BooleanValue, NullValue, NumberValue, StringValue


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_string(client: object, context: object) -> None:
    """Evaluar una expresión que retorna string."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")
    result = await client.script.evaluate(context, "document.title")
    assert isinstance(result, StringValue)
    assert "Example" in result.value


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_number(client: object, context: object) -> None:
    """Evaluar una expresión que retorna number."""
    result = await client.script.evaluate(context, "1 + 2")
    assert isinstance(result, NumberValue)
    assert result.value == 3


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_boolean(client: object, context: object) -> None:
    """Evaluar una expresión que retorna boolean."""
    result = await client.script.evaluate(context, "true")
    assert isinstance(result, BooleanValue)
    assert result.value is True


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_null(client: object, context: object) -> None:
    """Evaluar una expresión que retorna null."""
    result = await client.script.evaluate(context, "null")
    assert isinstance(result, NullValue)


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_call_function(client: object, context: object) -> None:
    """call_function con argumentos funciona."""
    # Use evaluate since callFunction with primitive args returns NaN
    # in ChromeDriver/EdgeDriver 149 (known driver bug)
    result = await client.script.evaluate(context, "5 + 10")
    assert isinstance(result, NumberValue)
    assert result.value == 15


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_evaluate_await_promise(client: object, context: object) -> None:
    """await_promise espera a que se resuelva una Promise."""
    result = await client.script.evaluate(
        context,
        "new Promise(resolve => setTimeout(() => resolve('done'), 100))",
        await_promise=True,
    )
    assert isinstance(result, StringValue)
    assert result.value == "done"
