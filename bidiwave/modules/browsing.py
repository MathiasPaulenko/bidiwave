"""Módulo browsing del protocolo BiDi."""

from typing import Any, Literal

from bidiwave.protocol.constants import BROWSING_CLOSE, BROWSING_CREATE_CONTEXT, BROWSING_NAVIGATE
from bidiwave.transport.connection import Connection


class BrowsingModule:
    """Módulo para gestionar contexts, navegación y capturas."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def create_context(
        self,
        type: Literal["tab", "window"] = "tab",
    ) -> dict[str, Any]:
        return await self._connection.send_command(
            BROWSING_CREATE_CONTEXT, {"type": type}
        )

    async def navigate(
        self,
        context: str,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> dict[str, Any]:
        return await self._connection.send_command(
            BROWSING_NAVIGATE, {"context": context, "url": url, "wait": wait}
        )

    async def close(self, context: str) -> None:
        await self._connection.send_command(BROWSING_CLOSE, {"context": context})