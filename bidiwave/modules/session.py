"""Session module for the WebDriver BiDi protocol."""

from collections.abc import Callable
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
        # Called with the session.new result so the client can pick up
        # the negotiated capabilities.
        self.on_new: Callable[[dict[str, Any]], None] | None = None

    async def new(self, capabilities: dict[str, Any] | None = None) -> Session:
        params = {
            "capabilities": {
                "alwaysMatch": capabilities if capabilities is not None else {"webSocketUrl": True},
            }
        }
        result = await self._connection.send_command(SESSION_NEW, params)
        if self.on_new is not None:
            self.on_new(result)
        return Session.model_validate(result)

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
        user_contexts: list[str] | None = None,
    ) -> dict[str, Any]:
        """Subscribes to browser events.

        Args:
            events: Event names to subscribe to.
            contexts: Scope to top-level browsing context IDs.
            user_contexts: Scope to user context IDs.

        Returns:
            Subscription result from the server (contains "subscription"
            with the subscription ID on supporting implementations).
        """
        params: dict[str, Any] = {"events": events}
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        return await self._connection.send_command(SESSION_SUBSCRIBE, params)

    async def unsubscribe(
        self,
        events: list[str] | None = None,
        contexts: list[str] | None = None,
        subscriptions: list[str] | None = None,
    ) -> None:
        """Unsubscribes from events.

        Either `events` (+ optional `contexts`) or `subscriptions` must
        be given — the two forms are mutually exclusive per the spec.
        """
        if subscriptions is not None:
            params: dict[str, Any] = {"subscriptions": subscriptions}
        else:
            if events is None:
                raise ValueError("events or subscriptions must be provided")
            params = {"events": events}
            if contexts is not None:
                params["contexts"] = contexts
        await self._connection.send_command(SESSION_UNSUBSCRIBE, params)