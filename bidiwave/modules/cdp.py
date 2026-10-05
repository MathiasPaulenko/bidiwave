"""CDP bridge module.

Not part of the W3C WebDriver BiDi spec — these commands are Chromium
extensions (``cdp.sendCommand`` / ``cdp.getSession``) implemented by
ChromeDriver and EdgeDriver. They are not available on Firefox.
"""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    BROWSER_CDP_GET_SESSION,
    BROWSER_CDP_SEND_COMMAND,
)
from bidiwave.protocol.results import CDPGetSessionResult
from bidiwave.transport.connection import Connection


class CDPModule:
    """Module for sending CDP commands directly (Chromium only).

    Allows access to Chrome DevTools Protocol APIs that are not
    covered by WebDriver BiDi.

    Example:
        cdp_session = await client.cdp.get_session("context-id")
        result = await client.cdp.send_command("Page.reload", {})
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def get_session(self, context: str) -> str | None:
        """Gets the CDP session ID for a browsing context.

        Args:
            context: Browsing context ID. Required by the driver.

        Returns:
            CDP session ID or None if no active session.
        """
        result = await self._connection.send_command(
            BROWSER_CDP_GET_SESSION, {"context": context}
        )
        parsed = CDPGetSessionResult.model_validate(result)
        return parsed.session

    async def send_command(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        session: str | None = None,
    ) -> dict[str, Any]:
        """Sends a CDP command directly to the browser.

        Args:
            method: CDP method name (e.g. "Page.reload", "Network.enable").
            params: Command parameters.
            session: CDP session ID to target (from get_session).

        Returns:
            CDP command result as dict.
        """
        send_params: dict[str, Any] = {"method": method}
        if params is not None:
            send_params["params"] = params
        if session is not None:
            send_params["session"] = session
        return await self._connection.send_command(
            BROWSER_CDP_SEND_COMMAND, send_params
        )
