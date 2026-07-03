"""EventDispatcher — distribuye eventos a handlers suscritos."""

import logging
from collections.abc import Callable
from typing import Any, Self

from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.protocol.events import parse_event

logger = logging.getLogger("bidiwave.events")


class EventDispatcher:
    """Distribuye eventos a handlers registrados.

    Características:
    - Múltiples handlers por event type
    - Error isolation: un handler que falla no afecta a otros
    - off() para desuscribirse
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
        """Registra un handler para un event type.

        Si handler es None, actúa como decorator.
        Si handler es proporcionado, registra y retorna Subscription.

        Args:
            event_type: Tipo de evento (ej: "log.entryAdded").
            handler: Función async que recibe el evento.

        Returns:
            Subscription si handler es proporcionado, decorator si no.
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
        """Desuscribe un handler."""
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
        """Dispatcha un evento a todos los handlers suscritos.

        Si un handler falla, se loguea el error pero no se propaga
        (error isolation).
        """
        event = parse_event(method, params)
        handlers = self._handlers.get(method, [])

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
