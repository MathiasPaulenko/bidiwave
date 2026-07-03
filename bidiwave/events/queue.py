"""Event queue with configurable backpressure."""

import asyncio
import contextlib
import logging
from typing import Any, Literal

logger = logging.getLogger("bidiwave.events")


class EventQueue:
    """Event queue with configurable backpressure.

    Drop policies:
    - "oldest": discards the oldest event when the queue is full
    - "newest": does not enqueue the newest event when the queue is full
    - "block": blocks put() until there is space
    """

    def __init__(
        self,
        max_size: int = 1000,
        drop_policy: Literal["oldest", "newest", "block"] = "oldest",
    ) -> None:
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=max_size)
        self._drop_policy = drop_policy
        self._dropped_count = 0

    async def put(self, event: dict[str, Any]) -> None:
        if self._drop_policy == "block":
            await self._queue.put(event)
            return

        if self._queue.full():
            if self._drop_policy == "oldest":
                with contextlib.suppress(asyncio.QueueEmpty):
                    self._queue.get_nowait()
                await self._queue.put(event)
                self._dropped_count += 1
                logger.warning(
                    "Event dropped (oldest). Total dropped: %d", self._dropped_count
                )
            elif self._drop_policy == "newest":
                self._dropped_count += 1
                logger.warning(
                    "Event dropped (newest). Total dropped: %d", self._dropped_count
                )
        else:
            await self._queue.put(event)

    async def get(self) -> dict[str, Any]:
        return await self._queue.get()

    def empty(self) -> bool:
        return self._queue.empty()

    def qsize(self) -> int:
        return self._queue.qsize()

    @property
    def dropped_count(self) -> int:
        return self._dropped_count
