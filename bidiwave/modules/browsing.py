"""Módulo browsing del protocolo BiDi."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from bidiwave.protocol.constants import (
    BROWSING_CAPTURE_SCREENSHOT,
    BROWSING_CLOSE,
    BROWSING_CREATE_CONTEXT,
    BROWSING_GET_TREE,
    BROWSING_NAVIGATE,
)
from bidiwave.protocol.results import Navigation, Screenshot
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.convenience.page import Page
    from bidiwave.modules.script import ScriptModule


@dataclass
class BrowsingContext:
    """Representa un context (tab/window) del browser."""

    id: str
    url: str = ""
    _module: BrowsingModule | None = field(default=None, repr=False)

    async def __aenter__(self) -> BrowsingContext:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self._module:
            await self._module.close(self.id)


class BrowsingModule:
    """Módulo para gestionar contexts, navegación y capturas."""

    def __init__(
        self,
        connection: Connection,
        script_module: ScriptModule | None = None,
    ) -> None:
        self._connection = connection
        self._script_module = script_module

    async def create_context(
        self,
        type: Literal["tab", "window"] = "tab",
    ) -> BrowsingContext:
        result = await self._connection.send_command(
            BROWSING_CREATE_CONTEXT, {"type": type}
        )
        return BrowsingContext(
            id=result["context"],
            url=result.get("url", ""),
            _module=self,
        )

    async def navigate(
        self,
        context: BrowsingContext | str,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Navigation:
        ctx_id = context.id if isinstance(context, BrowsingContext) else context
        result = await self._connection.send_command(
            BROWSING_NAVIGATE, {"context": ctx_id, "url": url, "wait": wait}
        )
        return Navigation.model_validate(result)

    async def close(self, context: BrowsingContext | str) -> None:
        ctx_id = context.id if isinstance(context, BrowsingContext) else context
        await self._connection.send_command(BROWSING_CLOSE, {"context": ctx_id})

    async def screenshot(
        self,
        context: BrowsingContext | str,
        format: Literal["png", "jpeg"] = "png",
        quality: int | None = None,
    ) -> Screenshot:
        ctx_id = context.id if isinstance(context, BrowsingContext) else context
        params: dict[str, Any] = {"context": ctx_id, "format": format}
        if quality is not None:
            params["quality"] = quality
        result = await self._connection.send_command(BROWSING_CAPTURE_SCREENSHOT, params)
        return Screenshot.model_validate(result)

    async def get_tree(
        self,
        root: str | None = None,
        max_depth: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if root:
            params["root"] = root
        if max_depth is not None:
            params["maxDepth"] = max_depth
        return await self._connection.send_command(BROWSING_GET_TREE, params)

    async def wait_for_selector(
        self,
        context: BrowsingContext | str,
        selector: str,
        timeout: float = 10.0,
    ) -> bool:
        """Espera a que un elemento exista en el DOM."""
        ctx_id = context.id if isinstance(context, BrowsingContext) else context
        result = await asyncio.wait_for(
            self._connection.send_command(
                "script.callFunction",
                {
                    "target": {"context": ctx_id},
                    "functionDeclaration": (
                        "(sel) => new Promise(resolve => {{"
                        " const el = document.querySelector(sel);"
                        " if (el) return resolve(true);"
                        " new MutationObserver((_, obs) => {{"
                        " if (document.querySelector(sel)) {{"
                        " obs.disconnect();"
                        " resolve(true);"
                        " }}"
                        " }}).observe(document.body, {{childList: true, subtree: true}});"
                        "}})"
                    ),
                    "args": [{"type": "string", "value": selector}],
                    "awaitPromise": True,
                },
            ),
            timeout=timeout,
        )
        return result.get("value") is True

    async def wait_for_function(
        self,
        context: BrowsingContext | str,
        expression: str,
        timeout: float = 10.0,
    ) -> Any:
        """Espera a que una función JS retorne true."""
        ctx_id = context.id if isinstance(context, BrowsingContext) else context

        async def check() -> Any:
            while True:
                result = await self._connection.send_command(
                    "script.evaluate",
                    {
                        "target": {"context": ctx_id},
                        "expression": expression,
                        "awaitPromise": False,
                    },
                )
                if result.get("value"):
                    return result.get("value")
                await asyncio.sleep(0.1)

        return await asyncio.wait_for(check(), timeout=timeout)

    async def open(
        self,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Page:
        """Crea un context, navega a la URL y retorna un Page object."""
        from bidiwave.convenience.page import Page

        ctx = await self.create_context()
        await self.navigate(ctx, url, wait)
        return Page(self, self._script_module, ctx)