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
            contexts=[ctx_id],
        )
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def set_permission(
        self,
        descriptor: dict[str, Any],
        state: Literal["granted", "denied", "prompt"],
        contexts: list[str] | None = None,
        origin: str | None = None,
    ) -> None:
        """Sets the state of a browser permission.

        Args:
            descriptor: Permission descriptor (e.g. {"name": "geolocation"}).
            state: Permission state to set.
            contexts: Context IDs to apply to. None = all.
            origin: Origin to apply the permission to. Required if no contexts.
        """
        params: dict[str, Any] = {
            "descriptor": descriptor,
            "state": state,
        }
        if contexts is not None:
            params["contexts"] = contexts
        if origin is not None:
            params["origin"] = origin
        await self._connection.send_command(PERMISSIONS_SET, params)
