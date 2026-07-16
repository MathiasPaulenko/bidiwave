"""Preload script module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any

from bidiwave.protocol.constants import (
    PRELOAD_ADD_SCRIPT,
    PRELOAD_REMOVE_SCRIPT,
)
from bidiwave.protocol.results import AddPreloadScriptResult
from bidiwave.transport.connection import Connection


class PreloadModule:
    """Module for managing preload scripts.

    Preload scripts are injected into pages before any other script runs,
    allowing you to modify the page environment early.

    Commands:
        - add_preload_script — inject a script before page load
        - remove_preload_script — remove a previously added script

    Example:
        script_id = await client.preload.add_script(
            "() => { window.__injected = true; }",
        )
        # ... navigate and verify ...
        await client.preload.remove_script(script_id)
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def add_script(
        self,
        function_declaration: str,
        arguments: list[dict[str, Any]] | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
        sandbox: str | None = None,
    ) -> str:
        """Adds a preload script.

        Args:
            function_declaration: JS function to execute before page load.
            arguments: Arguments to pass to the function.
            contexts: Context IDs where the script should run. None = all.
            user_contexts: User context IDs where the script should run. None = all.
            sandbox: Sandbox name to run the script in.

        Returns:
            Preload script ID for later removal.
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
        result = await self._connection.send_command(PRELOAD_ADD_SCRIPT, params)
        parsed = AddPreloadScriptResult.model_validate(result)
        return parsed.script

    async def remove_script(self, script_id: str) -> None:
        """Removes a preload script.

        Args:
            script_id: ID returned by add_script.
        """
        await self._connection.send_command(
            PRELOAD_REMOVE_SCRIPT, {"script": script_id}
        )
