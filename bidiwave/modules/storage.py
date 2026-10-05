"""Storage module — cookie operations.

Wire format follows the W3C BiDi spec: commands take an optional
`filter` (CookieFilter) and `partition` (PartitionDescriptor). A
browsing context can be scoped via `partition = {"type": "context",
"context": <id>}` — the `context` argument does that for you.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import (
    STORAGE_DELETE_COOKIES,
    STORAGE_GET_COOKIES,
    STORAGE_SET_COOKIE,
)
from bidiwave.protocol.results import Cookie, GetCookiesResult

if TYPE_CHECKING:
    from bidiwave.transport.connection import Connection


class StorageModule:
    """Cookie storage operations."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def get_cookies(
        self,
        context: Any | None = None,
        filter: dict[str, Any] | None = None,
        partition: dict[str, Any] | None = None,
    ) -> list[Cookie]:
        """Gets cookies, optionally filtered.

        Args:
            context: Context to scope to (mapped to a context partition).
            filter: CookieFilter dict, e.g. {"name": "...", "domain": "..."}.
            partition: PartitionDescriptor dict
                ({"type": "context", ...} or {"type": "storageKey", ...}).
        """
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if partition is not None:
            params["partition"] = partition
        elif context is not None:
            ctx_id = context.id if hasattr(context, "id") else str(context)
            params["partition"] = {"type": "context", "context": ctx_id}
        result = await self._connection.send_command(STORAGE_GET_COOKIES, params)
        parsed = GetCookiesResult.model_validate(result)
        return parsed.cookies

    async def set_cookie(
        self,
        context: Any | None,
        cookie: Cookie,
        partition: dict[str, Any] | None = None,
    ) -> None:
        """Sets a cookie.

        Args:
            context: Context to scope to (ignored when `partition` is given).
            cookie: Cookie model to store.
            partition: PartitionDescriptor dict.
        """
        cookie_dict = cookie.model_dump(by_alias=True, exclude_none=True)
        # Spec: cookie value is a network.BytesValue, not a raw string.
        cookie_dict["value"] = {"type": "string", "value": cookie.value}
        params: dict[str, Any] = {"cookie": cookie_dict}
        if partition is not None:
            params["partition"] = partition
        elif context is not None:
            ctx_id = context.id if hasattr(context, "id") else str(context)
            params["partition"] = {"type": "context", "context": ctx_id}
        await self._connection.send_command(STORAGE_SET_COOKIE, params)

    async def delete_cookies(
        self,
        context: Any | None = None,
        name: str | None = None,
        domain: str | None = None,
        path: str | None = None,
        partition: dict[str, Any] | None = None,
    ) -> None:
        """Deletes cookies matching the filter.

        Args:
            context: Context to scope to (ignored when `partition` is given).
            name: Delete only cookies with this name.
            domain: Delete only cookies for this domain.
            path: Delete only cookies with this path.
            partition: PartitionDescriptor dict.
        """
        params: dict[str, Any] = {}
        cookie_filter = {
            k: v
            for k, v in {"name": name, "domain": domain, "path": path}.items()
            if v is not None
        }
        if cookie_filter:
            params["filter"] = cookie_filter
        if partition is not None:
            params["partition"] = partition
        elif context is not None:
            ctx_id = context.id if hasattr(context, "id") else str(context)
            params["partition"] = {"type": "context", "context": ctx_id}
        await self._connection.send_command(STORAGE_DELETE_COOKIES, params)

    async def delete_cookie(self, context: Any | None, name: str) -> None:
        """Deletes a single cookie by name."""
        await self.delete_cookies(context, name=name)
