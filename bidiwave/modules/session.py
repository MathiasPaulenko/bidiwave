"""Módulo session del protocolo BiDi."""

from typing import Any

from bidiwave.protocol.constants import SESSION_NEW, SESSION_STATUS
from bidiwave.transport.connection import Connection


class SessionModule:
    """Módulo para gestionar la sesión BiDi."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def new(self, capabilities: dict[str, Any] | None = None) -> dict[str, Any]:
        params = {
            "capabilities": {
                "alwaysMatch": capabilities or {"webSocketUrl": True},
            }
        }
        return await self._connection.send_command(SESSION_NEW, params)

    async def status(self) -> dict[str, Any]:
        return await self._connection.send_command(SESSION_STATUS, {})