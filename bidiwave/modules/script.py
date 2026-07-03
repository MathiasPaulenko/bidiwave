"""Módulo script del protocolo BiDi."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import (
    SCRIPT_CALL_FUNCTION,
    SCRIPT_DISOWN,
    SCRIPT_EVALUATE,
    SCRIPT_GET_REALMS,
)
from bidiwave.protocol.remote_value import RemoteValue
from bidiwave.protocol.results import GetRealmsResult, RealmInfo
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
        sandbox: str | None = None,
    ) -> RemoteValue:
        ctx_id = context.id if hasattr(context, "id") else context
        target: dict[str, Any] = {"context": ctx_id}
        if sandbox is not None:
            target["sandbox"] = sandbox
        params = {
            "target": target,
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
        sandbox: str | None = None,
    ) -> RemoteValue:
        ctx_id = context.id if hasattr(context, "id") else context
        target: dict[str, Any] = {"context": ctx_id}
        if sandbox is not None:
            target["sandbox"] = sandbox
        params = {
            "target": target,
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

    async def get_realms(
        self,
        context: BrowsingContext | str | None = None,
        type: str | None = None,
    ) -> list[RealmInfo]:
        """Obtiene información sobre los realms disponibles.

        Args:
            context: Filtrar por context ID. None = todos los realms.
            type: Filtrar por tipo de realm ("window", "dedicated-worker",
                "shared-worker", "service-worker"). None = todos.

        Returns:
            Lista de RealmInfo.
        """
        params: dict[str, Any] = {}
        if context is not None:
            ctx_id = context.id if hasattr(context, "id") else context
            params["context"] = ctx_id
        if type is not None:
            params["type"] = type
        result = await self._connection.send_command(SCRIPT_GET_REALMS, params)
        parsed = GetRealmsResult.model_validate(result)
        return parsed.realms