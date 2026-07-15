"""EventDispatcher — dispatches events to subscribed handlers."""

import logging
from collections.abc import Callable
from typing import Any, Self

from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.protocol.events import parse_event

logger = logging.getLogger("bidiwave.events")


class EventDispatcher:
    """Dispatches events to registered handlers.

    Features:
    - Multiple handlers per event type
    - Error isolation: a failing handler does not affect others
    - off() to unsubscribe
    - Fluent API: dispatcher.on("a", h1).on("b", h2)
    - Decorator mode: @dispatcher.on("a")
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[AsyncHandler]] = {}

    def on(
        self,
        event_type: str,
        handler: AsyncHandler | None = None,
    ) -> Self | Subscription | Callable[[AsyncHandler], AsyncHandler]:
        """Registers a handler for an event type.

        If handler is None, acts as a decorator.
        If handler is provided, registers and returns a Subscription.

        Args:
            event_type: Event type (e.g: "log.entryAdded").
            handler: Async function that receives the event.

        Returns:
            Subscription if handler is provided, decorator if not.
        """
        if handler is not None:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            logger.debug(
                "Subscribed to %s (total: %d)",
                event_type,
                len(self._handlers[event_type]),
            )
            return Subscription(event_type, handler, self)

        def decorator(func: AsyncHandler) -> AsyncHandler:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            logger.debug(
                "Subscribed to %s (total: %d)",
                event_type,
                len(self._handlers[event_type]),
            )
            return func

        return decorator

    def off(self, subscription: Subscription) -> None:
        """Unsubscribes a handler."""
        handlers = self._handlers.get(subscription.event_type, [])
        if subscription.handler in handlers:
            handlers.remove(subscription.handler)
            logger.debug(
                "Unsubscribed from %s (remaining: %d)",
                subscription.event_type,
                len(handlers),
            )
            if not handlers:
                del self._handlers[subscription.event_type]

    async def dispatch(self, method: str, params: dict[str, Any]) -> None:
        """Dispatches an event to all subscribed handlers.

        If a handler fails, the error is logged but not propagated
        (error isolation).
        """
        try:
            event = parse_event(method, params)
        except Exception as e:
            logger.warning(
                "Failed to parse event %s: %s: %s — passing raw params",
                method,
                type(e).__name__,
                e,
            )
            event = params  # type: ignore[assignment]
        handlers = list(self._handlers.get(method, []))

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    "Handler error for %s: %s: %s",
                    method,
                    type(e).__name__,
                    e,
                    exc_info=True,
                )
