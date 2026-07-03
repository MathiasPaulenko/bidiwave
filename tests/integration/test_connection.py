"""Tests de conexión y ciclo de vida del client."""

from __future__ import annotations

import pytest

from bidiwave import BiDiClient


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_connect_and_close(client: object) -> None:
    """Conectar y cerrar funciona sin errores."""
    assert client is not None


@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)
@pytest.mark.asyncio
async def test_context_manager(client: object, chrome_bidi: str) -> None:
    """async with cierra la conexión automáticamente."""
    async with await BiDiClient.connect(chrome_bidi) as c:
        await c.session.new()
        assert c is not None
