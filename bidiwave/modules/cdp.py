"""Módulo CDP bridge del protocolo BiDi."""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    BROWSER_CDP_GET_SESSION,
    BROWSER_CDP_SEND_COMMAND,
)
from bidiwave.protocol.results import CDPGetSessionResult
from bidiwave.transport.connection import Connection


class CDPModule:
    """Módulo para enviar comandos CDP directamente (Chrome-only).

    Permite acceder a APIs de Chrome DevTools Protocol que aún
    no están cubiertas por WebDriver BiDi.

    Ejemplo:
        cdp_session = await client.cdp.get_session()
        result = await client.cdp.send_command("Page.reload", {})
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def get_session(self) -> str | None:
        """Obtiene el ID de la sesión CDP actual.

        Returns:
            ID de la sesión CDP o None si no hay una activa.
        """
        result = await self._connection.send_command(
            BROWSER_CDP_GET_SESSION, {}
        )
        parsed = CDPGetSessionResult.model_validate(result)
        return parsed.session

    async def send_command(
        self,
        cmd: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Envía un comando CDP directamente al browser.

        Args:
            cmd: Nombre del comando CDP (ej. "Page.reload", "Network.enable").
            params: Parámetros del comando.

        Returns:
            Resultado del comando CDP como dict.
        """
        send_params: dict[str, Any] = {"cmd": cmd}
        if params is not None:
            send_params["params"] = params
        return await self._connection.send_command(
            BROWSER_CDP_SEND_COMMAND, send_params
        )
