"""Emulation module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    EMULATION_SET_GEOLOCATION,
    EMULATION_SET_LOCALE,
    EMULATION_SET_NETWORK_CONDITIONS,
    EMULATION_SET_SCREEN_ORIENTATION,
    EMULATION_SET_TIMEZONE,
    EMULATION_SET_USER_AGENT,
)
from bidiwave.transport.connection import Connection


class EmulationModule:
    """Module for emulating device environment conditions.

    Commands:
        - set_geolocation — override geolocation coordinates
        - set_network_conditions — throttle or simulate offline network
        - set_timezone — override the browser timezone
        - set_user_agent — override the User-Agent string

    Example:
        await client.emulation.set_geolocation(
            coordinates={"latitude": 37.7749, "longitude": -122.4194},
            contexts=[ctx_id],
        )
        await client.emulation.set_timezone("America/Los_Angeles")
        await client.emulation.set_user_agent("MyBot/1.0")
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def set_geolocation(
        self,
        coordinates: dict[str, float] | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
        error: dict[str, str] | None = None,
    ) -> None:
        """Overrides the geolocation coordinates.

        Args:
            coordinates: Dict with 'latitude' and 'longitude' keys.
                None to clear the override.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
            error: Error dict to simulate, e.g. {"type": "positionUnavailable"}.
        """
        params: dict[str, Any] = {}
        if coordinates is not None:
            params["coordinates"] = coordinates
        if error is not None:
            params["error"] = error
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(EMULATION_SET_GEOLOCATION, params)

    async def set_network_conditions(
        self,
        offline: bool = True,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Overrides network conditions.

        Per the W3C BiDi spec (emulation.setNetworkConditions), the only
        supported condition is offline emulation. Pass ``offline=False``
        to clear the override (sends ``networkConditions: null``).

        Args:
            offline: True to simulate offline mode, False to clear.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {
            "networkConditions": {"type": "offline"} if offline else None,
        }
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(
            EMULATION_SET_NETWORK_CONDITIONS, params
        )

    async def set_timezone(
        self,
        timezone: str,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Overrides the browser timezone.

        Args:
            timezone: IANA timezone identifier (e.g. "America/New_York").
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"timezone": timezone}
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(EMULATION_SET_TIMEZONE, params)

    async def set_user_agent(
        self,
        user_agent: str | None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Overrides the User-Agent string.

        Per the W3C BiDi spec (emulation.setUserAgentOverride), only the
        User-Agent string itself can be overridden.

        Args:
            user_agent: User-Agent string to set. None to clear the override.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"userAgent": user_agent}
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(EMULATION_SET_USER_AGENT, params)

    async def set_locale(
        self,
        locale: str | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Overrides the browser locale.

        Args:
            locale: Locale identifier (e.g. "en-US", "fr-FR").
                None to clear the override.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {}
        if locale is not None:
            params["locale"] = locale
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(EMULATION_SET_LOCALE, params)

    async def set_screen_orientation(
        self,
        orientation: dict[str, Any] | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Overrides the screen orientation.

        Args:
            orientation: Dict with 'natural' ("portrait" or "landscape")
                and 'type' ("portrait-primary", "portrait-secondary",
                "landscape-primary", "landscape-secondary") per the spec's
                emulation.ScreenOrientation. None to clear the override
                (sends ``screenOrientation: null``).
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"screenOrientation": orientation}
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(
            EMULATION_SET_SCREEN_ORIENTATION, params
        )
