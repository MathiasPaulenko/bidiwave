"""Módulo script del protocolo BiDi."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import SCRIPT_CALL_FUNCTION, SCRIPT_DISOWN, SCRIPT_EVALUATE
from bidiwave.protocol.remote_value import RemoteValue
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext


class ScriptModule:
    """Módulo para ejecutar JavaScript en el browser."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def evaluate(
        self,
        context: BrowsingContext | str,
        expression: str,
        await_promise: bool = False,
    ) -> RemoteValue:
        ctx_id = context.id if hasattr(context, "id") else context
        params = {
            "target": {"context": ctx_id},
            "expression": expression,
            "awaitPromise": await_promise,
        }
        result = await self._connection.send_command(SCRIPT_EVALUATE, params)
        return RemoteValue.parse(result)

    async def call_function(
        self,
        context: BrowsingContext | str,
        function_declaration: str,
        args: list[dict[str, Any]] | None = None,
        await_promise: bool = False,
    ) -> RemoteValue:
        ctx_id = context.id if hasattr(context, "id") else context
        params = {
            "target": {"context": ctx_id},
            "functionDeclaration": function_declaration,
            "args": args or [],
            "awaitPromise": await_promise,
        }
        result = await self._connection.send_command(SCRIPT_CALL_FUNCTION, params)
        return RemoteValue.parse(result)

    async def disown(self, context: BrowsingContext | str, handles: list[str]) -> None:
        ctx_id = context.id if hasattr(context, "id") else context
        params = {
            "target": {"context": ctx_id},
            "handles": handles,
        }
        await self._connection.send_command(SCRIPT_DISOWN, params)