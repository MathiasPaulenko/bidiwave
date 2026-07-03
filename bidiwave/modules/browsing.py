"""Browsing module for the WebDriver BiDi protocol."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from bidiwave.protocol.constants import (
    BROWSING_ACTIVATE,
    BROWSING_CAPTURE_SCREENSHOT,
    BROWSING_CLOSE,
    BROWSING_CREATE_CONTEXT,
    BROWSING_CREATE_USER_CONTEXT,
    BROWSING_GET_TREE,
    BROWSING_GET_USER_CONTEXTS,
    BROWSING_HANDLE_USER_PROMPT,
    BROWSING_LOCATE_NODES,
    BROWSING_NAVIGATE,
    BROWSING_PRINT,
    BROWSING_RELOAD,
    BROWSING_REMOVE_USER_CONTEXT,
    BROWSING_SET_VIEWPORT,
    BROWSING_TRAVERSE_HISTORY,
)
from bidiwave.protocol.results import (
    GetUserContextsResult,
    LocateNodesResult,
    Navigation,
    PrintResult,
    Screenshot,
    UserContextInfo,
)
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.convenience.page import Page
    from bidiwave.modules.script import ScriptModule


@dataclass
class BrowsingContext:
    """Represents a browsing context (tab/window)."""

    id: str
    url: str = ""
    _module: BrowsingModule | None = field(default=None, repr=False)

    async def __aenter__(self) -> BrowsingContext:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self._module:
            await self._module.close(self.id)


class BrowsingModule:
    """Module for managing browsing contexts, navigation and screenshots."""

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
        user_context: str | None = None,
    ) -> BrowsingContext:
        params: dict[str, Any] = {"type": type}
        if user_context is not None:
            params["userContext"] = user_context
        result = await self._connection.send_command(
            BROWSING_CREATE_CONTEXT, params
        )
        return BrowsingContext(
            id=result["context"],
            url=result.get("url", ""),
            _module=self,
        )

    async def create_user_context(self) -> UserContextInfo:
        """Creates an isolated user context (profile with its own cookies).

        Returns:
            UserContextInfo with the ID of the created user context.
        """
        result = await self._connection.send_command(
            BROWSING_CREATE_USER_CONTEXT, {}
        )
        return UserContextInfo.model_validate(result)

    async def remove_user_context(self, user_context: str) -> None:
        """Removes a user context and all its browsing contexts.

        Args:
            user_context: ID of the user context to remove.
        """
        await self._connection.send_command(
            BROWSING_REMOVE_USER_CONTEXT, {"userContext": user_context}
        )

    async def get_user_contexts(self) -> list[UserContextInfo]:
        """Lists all available user contexts.

        Returns:
            List of UserContextInfo.
        """
        result = await self._connection.send_command(
            BROWSING_GET_USER_CONTEXTS, {}
        )
        parsed = GetUserContextsResult.model_validate(result)
        return parsed.user_contexts

    async def navigate(
        self,
        context: BrowsingContext | str,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Navigation:
        ctx_id = context.id if hasattr(context, "id") else context
        result = await self._connection.send_command(
            BROWSING_NAVIGATE, {"context": ctx_id, "url": url, "wait": wait}
        )
        return Navigation.model_validate(result)

    async def close(self, context: BrowsingContext | str) -> None:
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(BROWSING_CLOSE, {"context": ctx_id})

    async def screenshot(
        self,
        context: BrowsingContext | str,
        format: Literal["png", "jpeg"] = "png",
        quality: int | None = None,
    ) -> Screenshot:
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if format != "png":
            params["format"] = format
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
        """Waits for an element to exist in the DOM."""
        ctx_id = context.id if hasattr(context, "id") else context
        # Use evaluate instead of callFunction (driver bug with primitive args)
        expression = (
            f"new Promise(resolve => {{"
            f" const el = document.querySelector({selector!r});"
            f" if (el) return resolve(true);"
            f" new MutationObserver((_, obs) => {{"
            f" if (document.querySelector({selector!r})) {{"
            f" obs.disconnect();"
            f" resolve(true);"
            f" }}"
            f" }}).observe(document.body, {{childList: true, subtree: true}});"
            f"}})"
        )
        result = await asyncio.wait_for(
            self._connection.send_command(
                "script.evaluate",
                {
                    "target": {"context": ctx_id},
                    "expression": expression,
                    "awaitPromise": True,
                },
            ),
            timeout=timeout,
        )
        # Unwrap script success wrapper
        inner = result.get("result", result)
        return inner.get("value") is True

    async def wait_for_function(
        self,
        context: BrowsingContext | str,
        expression: str,
        timeout: float = 10.0,
    ) -> Any:
        """Waits for a JS function to return true."""
        ctx_id = context.id if hasattr(context, "id") else context

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
                # Unwrap script success wrapper
                inner = result.get("result", result)
                if inner.get("value"):
                    return inner.get("value")
                await asyncio.sleep(0.1)

        return await asyncio.wait_for(check(), timeout=timeout)

    async def reload(
        self,
        context: BrowsingContext | str,
        wait: Literal["none", "interactive", "complete"] = "complete",
        ignore_cache: bool | None = None,
    ) -> Navigation:
        """Reloads the current context."""
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id, "wait": wait}
        if ignore_cache is not None:
            params["ignoreCache"] = ignore_cache
        result = await self._connection.send_command(
            BROWSING_RELOAD, params
        )
        return Navigation.model_validate(result)

    async def traverse_history(
        self,
        context: BrowsingContext | str,
        direction: Literal["back", "forward"],
    ) -> Navigation:
        """Navigates back or forward in history."""
        ctx_id = context.id if hasattr(context, "id") else context
        result = await self._connection.send_command(
            BROWSING_TRAVERSE_HISTORY,
            {"context": ctx_id, "direction": direction},
        )
        return Navigation.model_validate(result)

    async def handle_user_prompt(
        self,
        context: BrowsingContext | str,
        accept: bool | None = None,
        user_text: str | None = None,
    ) -> None:
        """Accepts or dismisses a dialog (alert, confirm, prompt)."""
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if accept is not None:
            params["accept"] = accept
        if user_text is not None:
            params["userText"] = user_text
        await self._connection.send_command(
            BROWSING_HANDLE_USER_PROMPT, params
        )

    async def print(
        self,
        context: BrowsingContext | str,
        background: bool = False,
        margin: dict[str, Any] | None = None,
        orientation: Literal["portrait", "landscape"] = "portrait",
        page: dict[str, Any] | None = None,
        page_ranges: list[str] | None = None,
        scale: float = 1.0,
        shrink_to_fit: bool = True,
    ) -> PrintResult:
        """Exports the context to PDF and returns base64 data."""
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "background": background,
            "orientation": orientation,
            "scale": scale,
            "shrinkToFit": shrink_to_fit,
        }
        if margin is not None:
            params["margin"] = margin
        if page is not None:
            params["page"] = page
        if page_ranges is not None:
            params["pageRanges"] = page_ranges
        result = await self._connection.send_command(BROWSING_PRINT, params)
        return PrintResult.model_validate(result)

    async def locate_nodes(
        self,
        context: BrowsingContext | str,
        locator: dict[str, Any],
        max_node_count: int | None = None,
        start_nodes: list[dict[str, Any]] | None = None,
    ) -> LocateNodesResult:
        """Locates elements in the DOM using a locator.

        Args:
            context: BrowsingContext or context ID.
            locator: Dict with the locator type, e.g.:
                {"type": "css", "value": "div.product"}
                {"type": "xpath", "value": "//div[@id='foo']"}
                {"type": "innerText", "value": "Click me"}
            max_node_count: Maximum number of nodes to return.
            start_nodes: Nodes to search from (e.g. iframes).
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id, "locator": locator}
        if max_node_count is not None:
            params["maxNodeCount"] = max_node_count
        if start_nodes is not None:
            params["startNodes"] = start_nodes
        result = await self._connection.send_command(
            BROWSING_LOCATE_NODES, params
        )
        return LocateNodesResult.model_validate(result)

    async def activate(self, context: BrowsingContext | str) -> None:
        """Activates a browsing context (brings it to front)."""
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(
            BROWSING_ACTIVATE, {"context": ctx_id}
        )

    async def set_viewport(
        self,
        context: BrowsingContext | str,
        viewport: dict[str, int] | None = None,
        device_pixel_ratio: float | None = None,
    ) -> None:
        """Sets the viewport and device pixel ratio of a context.

        Args:
            context: BrowsingContext or context ID.
            viewport: Dict with "width" and "height" in CSS pixels.
                Pass None to reset to the original viewport.
            device_pixel_ratio: Ratio of physical pixels to CSS pixels.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if viewport is not None:
            params["viewport"] = viewport
        if device_pixel_ratio is not None:
            params["devicePixelRatio"] = device_pixel_ratio
        await self._connection.send_command(
            BROWSING_SET_VIEWPORT, params
        )

    async def open(
        self,
        url: str,
        wait: Literal["none", "interactive", "complete"] = "complete",
    ) -> Page:
        """Creates a context, navigates to the URL and returns a Page object."""
        from bidiwave.convenience.page import Page

        ctx = await self.create_context()
        await self.navigate(ctx, url, wait)
        return Page(self, self._script_module, ctx)