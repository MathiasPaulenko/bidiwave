"""Permissions module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any, Literal

from bidiwave.protocol.constants import PERMISSIONS_SET
from bidiwave.transport.connection import Connection


class PermissionsModule:
    """Module for managing browser permissions.

    Commands:
        - set_permission — set a permission state (granted, denied, prompt)

    Example:
        await client.permissions.set_permission(
            descriptor={"name": "geolocation"},
            state="granted",
            origin="https://example.com",
        )
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def set_permission(
        self,
        descriptor: dict[str, Any],
        state: Literal["granted", "denied", "prompt"],
        origin: str,
        embedded_origin: str | None = None,
        user_context: str | None = None,
    ) -> None:
        """Sets the state of a browser permission.

        Args:
            descriptor: Permission descriptor (e.g. {"name": "geolocation"}).
            state: Permission state to set.
            origin: Top-level origin to apply the permission to. Required
                per the W3C Permissions spec.
            embedded_origin: Origin of a document embedded in `origin`
                (optional).
            user_context: User context ID to scope to (optional).
        """
        params: dict[str, Any] = {
            "descriptor": descriptor,
            "state": state,
            "origin": origin,
        }
        if embedded_origin is not None:
            params["embeddedOrigin"] = embedded_origin
        if user_context is not None:
            params["userContext"] = user_context
        await self._connection.send_command(PERMISSIONS_SET, params)
