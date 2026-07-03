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

    async def evaluate(
        self,
        expression: str,
        await_promise: bool = False,
        sandbox: str | None = None,
    ) -> RemoteValue:
        if self._script is None:
            raise RuntimeError("ScriptModule not available")
        return await self._script.evaluate(
            self._context, expression, await_promise, sandbox=sandbox
        )

    async def call(
        self,
        function_declaration: str,
        args: list[dict[str, Any]] | None = None,
        await_promise: bool = False,
        sandbox: str | None = None,
    ) -> RemoteValue:
        if self._script is None:
            raise RuntimeError("ScriptModule not available")
        return await self._script.call_function(
            self._context, function_declaration, args, await_promise,
            sandbox=sandbox,
        )

    async def navigate(
        self,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Any:
        return await self._browsing.navigate(self._context, url, wait)

    async def reload(
        self,
        wait: Literal["none", "interactive", "complete"] = "complete",
        ignore_cache: bool | None = None,
    ) -> Any:
        return await self._browsing.reload(self._context, wait, ignore_cache)

    async def back(self) -> Any:
        return await self._browsing.traverse_history(self._context, "back")

    async def forward(self) -> Any:
        return await self._browsing.traverse_history(self._context, "forward")

    async def handle_user_prompt(
        self,
        accept: bool | None = None,
        user_text: str | None = None,
    ) -> None:
        await self._browsing.handle_user_prompt(self._context, accept, user_text)

    async def print(
        self,
        background: bool = False,
        margin: dict[str, Any] | None = None,
        orientation: Literal["portrait", "landscape"] = "portrait",
        page: dict[str, Any] | None = None,
        page_ranges: list[str] | None = None,
        scale: float = 1.0,
        shrink_to_fit: bool = True,
    ) -> bytes:
        result = await self._browsing.print(
            self._context,
            background=background,
            margin=margin,
            orientation=orientation,
            page=page,
            page_ranges=page_ranges,
            scale=scale,
            shrink_to_fit=shrink_to_fit,
        )
        return base64.b64decode(result.data)

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

    async def activate(self) -> None:
        await self._browsing.activate(self._context)

    async def set_viewport(
        self,
        width: int,
        height: int,
        device_pixel_ratio: float | None = None,
    ) -> None:
        await self._browsing.set_viewport(
            self._context,
            viewport={"width": width, "height": height},
            device_pixel_ratio=device_pixel_ratio,
        )

    async def locate_nodes(
        self,
        locator: dict[str, Any],
        max_node_count: int | None = None,
    ) -> list[dict[str, Any]]:
        result = await self._browsing.locate_nodes(
            self._context, locator, max_node_count=max_node_count
        )
        return result.nodes

    async def __aenter__(self) -> Page:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
