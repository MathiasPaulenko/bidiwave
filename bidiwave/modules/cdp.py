"""CDP bridge module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    BROWSER_CDP_GET_SESSION,
    BROWSER_CDP_SEND_COMMAND,
)
from bidiwave.protocol.results import CDPGetSessionResult
from bidiwave.transport.connection import Connection


class CDPModule:
    """Module for sending CDP commands directly (Chrome-only).

    Allows access to Chrome DevTools Protocol APIs that are not
    yet covered by WebDriver BiDi.

    Example:
        cdp_session = await client.cdp.get_session()
        result = await client.cdp.send_command("Page.reload", {})
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def get_session(self) -> str | None:
        """Gets the current CDP session ID.

        Returns:
            CDP session ID or None if no active session.
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
        """Sends a CDP command directly to the browser.

        Args:
            cmd: CDP command name (e.g. "Page.reload", "Network.enable").
            params: Command parameters.

        Returns:
            CDP command result as dict.
        """
        send_params: dict[str, Any] = {"cmd": cmd}
        if params is not None:
            send_params["params"] = params
        return await self._connection.send_command(
            BROWSER_CDP_SEND_COMMAND, send_params
        )
