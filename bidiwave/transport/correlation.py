"""Correlation of commands with responses via ID."""

import asyncio
from typing import Any


class Correlator:
    """Associates commands with their responses via ID."""

    def __init__(self) -> None:
        self._next_id: int = 0
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def register(self, command_id: int) -> asyncio.Future[dict[str, Any]]:
        fut: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[command_id] = fut
        return fut

    def resolve(self, command_id: int, result: dict[str, Any]) -> bool:
        """Resolves the pending future for command_id. Returns False if unknown."""
        fut = self._pending.pop(command_id, None)
        if fut and not fut.done():
            fut.set_result(result)
            return True
        return False

    def reject(self, command_id: int, error: Exception) -> bool:
        """Rejects the pending future for command_id. Returns False if unknown."""
        fut = self._pending.pop(command_id, None)
        if fut and not fut.done():
            fut.set_exception(error)
            return True
        return False

    def reject_all(self, error: Exception) -> None:
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(error)
        self._pending.clear()