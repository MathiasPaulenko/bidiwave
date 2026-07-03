"""Log module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bidiwave.protocol.constants import LOG_CLEAR
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext


class LogModule:
    """Module for managing browser logs.

    Commands:
        - clear — clears the log buffer for a context

    Example:
        await client.log.clear(context)
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def clear(self, context: BrowsingContext | str | None = None) -> None:
        """Clears the log buffer.

        Args:
            context: BrowsingContext or context ID. None = all contexts.
        """
        params: dict[str, str] = {}
        if context is not None:
            ctx_id = context.id if hasattr(context, "id") else context
            params["context"] = ctx_id
        await self._connection.send_command(LOG_CLEAR, params)
