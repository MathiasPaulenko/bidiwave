"""Módulo script del protocolo BiDi."""

from typing import Any

from bidiwave.protocol.constants import SCRIPT_EVALUATE
from bidiwave.transport.connection import Connection


class ScriptModule:
    """Módulo para ejecutar JavaScript en el browser."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def evaluate(
        self,
        context: str,
        expression: str,
        await_promise: bool = False,
    ) -> dict[str, Any]:
        params = {
            "target": {"context": context},
            "expression": expression,
            "awaitPromise": await_promise,
        }
        return await self._connection.send_command(SCRIPT_EVALUATE, params)