"""Integration test: hello world BiDi contra Chrome via ChromeDriver."""

from __future__ import annotations

import pytest

from bidiwave import StringValue


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_hello_world(client: object, context: object) -> None:
    """Ciclo completo: navegar, evaluar JS, verificar título."""
    await client.browsing.navigate(context, "https://example.com", wait="complete")

    result = await client.script.evaluate(context, "document.title")
    assert isinstance(result, StringValue)
    assert result.value == "Example Domain"
