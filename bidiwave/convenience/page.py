"""Page object — capa de conveniencia sobre BrowsingContext."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, Literal

from bidiwave.protocol.remote_value import RemoteValue

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext, BrowsingModule
    from bidiwave.modules.script import ScriptModule


class Page:
    """Wrapper de conveniencia sobre un BrowsingContext.

    Ejemplo:
        async with await client.browsing.open("https://example.com") as page:
            title = await page.evaluate("document.title")
            await page.wait_for_selector("h1")
            screenshot = await page.screenshot()
    """

    def __init__(
        self,
        browsing: BrowsingModule,
        script: ScriptModule | None,
        context: BrowsingContext,
    ) -> None:
        self._browsing = browsing
        self._script = script
        self._context = context

    @property
    def id(self) -> str:
        return self._context.id

    @property
    def url(self) -> str:
        return self._context.url

    async def evaluate(self, expression: str, await_promise: bool = False) -> RemoteValue:
        if self._script is None:
            raise RuntimeError("ScriptModule not available")
        return await self._script.evaluate(self._context, expression, await_promise)

    async def call(
        self,
        function_declaration: str,
        args: list[dict[str, Any]] | None = None,
        await_promise: bool = False,
    ) -> RemoteValue:
        if self._script is None:
            raise RuntimeError("ScriptModule not available")
        return await self._script.call_function(
            self._context, function_declaration, args, await_promise,
        )

    async def navigate(
        self,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Any:
        return await self._browsing.navigate(self._context, url, wait)

    async def screenshot(
        self,
        format: Literal["png", "jpeg"] = "png",
        quality: int | None = None,
    ) -> bytes:
        result = await self._browsing.screenshot(self._context, format, quality)
        return base64.b64decode(result.data)

    async def wait_for_selector(self, selector: str, timeout: float = 10.0) -> bool:
        return await self._browsing.wait_for_selector(self._context, selector, timeout)

    async def wait_for_function(self, expression: str, timeout: float = 10.0) -> Any:
        return await self._browsing.wait_for_function(self._context, expression, timeout)

    async def disown(self, handles: list[str]) -> None:
        if self._script is None:
            raise RuntimeError("ScriptModule not available")
        await self._script.disown(self._context, handles)

    async def close(self) -> None:
        await self._browsing.close(self._context)

    async def __aenter__(self) -> Page:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
