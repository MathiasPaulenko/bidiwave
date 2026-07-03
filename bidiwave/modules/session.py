"""Módulo session del protocolo BiDi."""

from typing import Any

from bidiwave.protocol.constants import (
    SESSION_END,
    SESSION_NEW,
    SESSION_STATUS,
    SESSION_SUBSCRIBE,
    SESSION_UNSUBSCRIBE,
)
from bidiwave.protocol.results import Session, SessionStatus
from bidiwave.transport.connection import Connection


class SessionModule:
    """Módulo para gestionar la sesión BiDi."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def new(self, capabilities: dict[str, Any] | None = None) -> Session:
        params = {
            "capabilities": {
                "alwaysMatch": capabilities or {"webSocketUrl": True},
            }
        }
        result = await self._connection.send_command(SESSION_NEW, params)
        return Session.model_validate({
            "session_id": result.get("sessionId", ""),
            "capabilities": result.get("capabilities", {}),
        })

    async def status(self) -> SessionStatus:
        result = await self._connection.send_command(SESSION_STATUS, {})
        return SessionStatus.model_validate(result)

    async def end(self) -> None:
        """Cierra la sesión BiDi actual."""
        await self._connection.send_command(SESSION_END, {})

    async def subscribe(
        self,
        events: list[str],
        contexts: list[str] | None = None,
    ) -> None:
        """Suscribe a eventos del browser."""
        params: dict[str, Any] = {"events": events}
        if contexts:
            params["contexts"] = contexts
        await self._connection.send_command(SESSION_SUBSCRIBE, params)

    async def unsubscribe(
        self,
        events: list[str],
        contexts: list[str] | None = None,
    ) -> None:
        """Desuscribe de eventos."""
        params: dict[str, Any] = {"events": events}
        if contexts:
            params["contexts"] = contexts
        await self._connection.send_command(SESSION_UNSUBSCRIBE, params)