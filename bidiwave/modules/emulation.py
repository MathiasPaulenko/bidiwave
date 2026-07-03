"""Emulation module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    EMULATION_SET_GEOLOCATION,
    EMULATION_SET_NETWORK_CONDITIONS,
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
    ) -> None:
        """Overrides the geolocation coordinates.

        Args:
            coordinates: Dict with 'latitude' and 'longitude' keys.
                None to clear the override.
            contexts: Context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {}
        if coordinates is not None:
            params["coordinates"] = coordinates
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(EMULATION_SET_GEOLOCATION, params)

    async def set_network_conditions(
        self,
        offline: bool | None = None,
        download_throughput: int | None = None,
        upload_throughput: int | None = None,
        latency: int | None = None,
        contexts: list[str] | None = None,
    ) -> None:
        """Overrides network conditions (throttling or offline).

        Args:
            offline: True to simulate offline mode.
            download_throughput: Max download throughput in bytes/sec.
            upload_throughput: Max upload throughput in bytes/sec.
            latency: Additional latency in milliseconds.
            contexts: Context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {}
        if offline is not None:
            params["offline"] = offline
        if download_throughput is not None:
            params["downloadThroughput"] = download_throughput
        if upload_throughput is not None:
            params["uploadThroughput"] = upload_throughput
        if latency is not None:
            params["latency"] = latency
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(
            EMULATION_SET_NETWORK_CONDITIONS, params
        )

    async def set_timezone(
        self,
        timezone: str,
        contexts: list[str] | None = None,
    ) -> None:
        """Overrides the browser timezone.

        Args:
            timezone: IANA timezone identifier (e.g. "America/New_York").
            contexts: Context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"timezone": timezone}
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(EMULATION_SET_TIMEZONE, params)

    async def set_user_agent(
        self,
        user_agent: str,
        accept_language: str | None = None,
        platform: str | None = None,
        contexts: list[str] | None = None,
    ) -> None:
        """Overrides the User-Agent string.

        Args:
            user_agent: User-Agent string to set.
            accept_language: Accept-Language header value.
            platform: Platform string to report.
            contexts: Context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"userAgent": user_agent}
        if accept_language is not None:
            params["acceptLanguage"] = accept_language
        if platform is not None:
            params["platform"] = platform
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(EMULATION_SET_USER_AGENT, params)
