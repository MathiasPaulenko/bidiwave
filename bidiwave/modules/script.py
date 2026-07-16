"""Script module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import (
    SCRIPT_ADD_PRELOAD_SCRIPT,
    SCRIPT_CALL_FUNCTION,
    SCRIPT_DISOWN,
    SCRIPT_EVALUATE,
    SCRIPT_GET_REALMS,
    SCRIPT_REMOVE_PRELOAD_SCRIPT,
)
from bidiwave.protocol.remote_value import RemoteValue
from bidiwave.protocol.results import (
    GetRealmsResult,
    RealmInfo,
    ScriptAddPreloadScriptResult,
)
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext


class ScriptModule:
    """Module for executing JavaScript in the browser."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def evaluate(
        self,
        context: BrowsingContext | str | None = None,
        expression: str = "",
        await_promise: bool = False,
        sandbox: str | None = None,
        realm: str | None = None,
        serialization_options: dict[str, Any] | None = None,
        user_activation: bool = False,
    ) -> RemoteValue:
        target = self._build_target(context, sandbox, realm)
        params: dict[str, Any] = {
            "target": target,
            "expression": expression,
            "awaitPromise": await_promise,
            "userActivation": user_activation,
        }
        if serialization_options is not None:
            params["serializationOptions"] = serialization_options
        result = await self._connection.send_command(SCRIPT_EVALUATE, params)
        return RemoteValue.parse(result)

    async def call_function(
        self,
        context: BrowsingContext | str | None = None,
        function_declaration: str = "",
        args: list[dict[str, Any]] | None = None,
        await_promise: bool = False,
        sandbox: str | None = None,
        realm: str | None = None,
        this: dict[str, Any] | None = None,
        serialization_options: dict[str, Any] | None = None,
        user_activation: bool = False,
    ) -> RemoteValue:
        target = self._build_target(context, sandbox, realm)
        params: dict[str, Any] = {
            "target": target,
            "functionDeclaration": function_declaration,
            "args": args or [],
            "awaitPromise": await_promise,
            "this": this if this is not None else {"type": "undefined"},
            "userActivation": user_activation,
        }
        if serialization_options is not None:
            params["serializationOptions"] = serialization_options
        result = await self._connection.send_command(SCRIPT_CALL_FUNCTION, params)
        return RemoteValue.parse(result)

    async def disown(
        self,
        context: BrowsingContext | str | None = None,
        handles: list[str] | None = None,
        sandbox: str | None = None,
        realm: str | None = None,
    ) -> None:
        target = self._build_target(context, sandbox, realm)
        params: dict[str, Any] = {
            "target": target,
            "handles": handles or [],
        }
        await self._connection.send_command(SCRIPT_DISOWN, params)

    async def get_realms(
        self,
        context: BrowsingContext | str | None = None,
        type: str | None = None,
    ) -> list[RealmInfo]:
        """Gets information about available realms.

        Args:
            context: Filter by context ID. None = all realms.
            type: Filter by realm type ("window", "dedicated-worker",
                "shared-worker", "service-worker"). None = all.

        Returns:
            List of RealmInfo.
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

    async def add_preload_script(
        self,
        function_declaration: str,
        arguments: list[dict[str, Any]] | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
        sandbox: str | None = None,
    ) -> ScriptAddPreloadScriptResult:
        """Adds a preload script with optional channel support.

        Unlike preload.addPreloadScript, this variant supports channels
        for bidirectional communication between the preload script and
        the client via script.message events.

        Args:
            function_declaration: JavaScript function to execute.
            arguments: Arguments to pass to the function.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to.
            sandbox: Sandbox name to run the script in.

        Returns:
            ScriptAddPreloadScriptResult with script ID and channel.
        """
        params: dict[str, Any] = {
            "functionDeclaration": function_declaration,
        }
        if arguments is not None:
            params["arguments"] = arguments
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        if sandbox is not None:
            params["sandbox"] = sandbox
        result = await self._connection.send_command(
            SCRIPT_ADD_PRELOAD_SCRIPT, params
        )
        return ScriptAddPreloadScriptResult.model_validate(result)

    async def remove_preload_script(
        self,
        script_id: str,
    ) -> None:
        """Removes a preload script by its ID.

        Args:
            script_id: ID of the preload script to remove.
        """
        params: dict[str, Any] = {"script": script_id}
        await self._connection.send_command(
            SCRIPT_REMOVE_PRELOAD_SCRIPT, params
        )

    @staticmethod
    def _build_target(
        context: BrowsingContext | str | None,
        sandbox: str | None,
        realm: str | None,
    ) -> dict[str, Any]:
        if realm is not None:
            return {"realm": realm}
        if context is None:
            raise ValueError("Either context or realm must be provided")
        ctx_id = context.id if hasattr(context, "id") else context
        target: dict[str, Any] = {"context": ctx_id}
        if sandbox is not None:
            target["sandbox"] = sandbox
        return target