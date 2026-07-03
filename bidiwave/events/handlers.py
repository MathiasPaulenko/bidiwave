"""Types and utilities for event handlers."""

from __future__ import annotations

import weakref
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bidiwave.events.dispatcher import EventDispatcher

AsyncHandler = Callable[[Any], Awaitable[None]]
"""Type for an async handler that receives an event."""


@dataclass
class Subscription:
    """Handle to unsubscribe from an event."""

    event_type: str
    handler: AsyncHandler
    _dispatcher_ref: weakref.ReferenceType[EventDispatcher] = field(
        repr=False, compare=False
    )

    def __init__(
        self, event_type: str, handler: AsyncHandler, dispatcher: EventDispatcher
    ) -> None:
        self.event_type = event_type
        self.handler = handler
        self._dispatcher_ref = weakref.ref(dispatcher)
