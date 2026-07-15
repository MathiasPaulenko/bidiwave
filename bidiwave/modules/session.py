"""Session module for the WebDriver BiDi protocol."""

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
    """Module for managing the BiDi session."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def new(self, capabilities: dict[str, Any] | None = None) -> Session:
        params = {
            "capabilities": {
                "alwaysMatch": capabilities if capabilities is not None else {"webSocketUrl": True},
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
        """Closes the current BiDi session."""
        await self._connection.send_command(SESSION_END, {})

    async def subscribe(
        self,
        events: list[str],
        contexts: list[str] | None = None,
    ) -> None:
        """Subscribes to browser events."""
        params: dict[str, Any] = {"events": events}
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(SESSION_SUBSCRIBE, params)

    async def unsubscribe(
        self,
        events: list[str],
        contexts: list[str] | None = None,
    ) -> None:
        """Unsubscribes from events."""
        params: dict[str, Any] = {"events": events}
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(SESSION_UNSUBSCRIBE, params)