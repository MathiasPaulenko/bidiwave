"""Storage module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import (
    STORAGE_DELETE_COOKIES,
    STORAGE_GET_COOKIES,
    STORAGE_SET_COOKIE,
)
from bidiwave.protocol.results import Cookie, GetCookiesResult
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext


class StorageModule:
    """Module for managing browser cookies.

    Commands:
        - get_cookies — gets cookies from a context
        - set_cookie — creates or updates a cookie
        - delete_cookies — deletes cookies by filter
        - delete_cookie — deletes a single cookie by name

    Example:
        cookies = await client.storage.get_cookies(context)
        for cookie in cookies:
            print(f"{cookie.name}={cookie.value}")

        await client.storage.set_cookie(
            context,
            cookie=Cookie(name="session", value="abc123", domain="example.com"),
        )
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def get_cookies(
        self,
        context: BrowsingContext | str,
        filter: dict[str, Any] | None = None,
        partition_key: dict[str, Any] | None = None,
    ) -> list[Cookie]:
        """Gets cookies from a browsing context, optionally filtered.

        Args:
            context: BrowsingContext or context ID.
            filter: Optional filter dict (e.g. {"name": "session"}).
            partition_key: Optional partition key with userContext/sourceOrigin.

        Returns:
            List of Cookie.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if filter is not None:
            params["filter"] = filter
        if partition_key is not None:
            params["partitionKey"] = partition_key
        result = await self._connection.send_command(
            STORAGE_GET_COOKIES, params
        )
        parsed = GetCookiesResult.model_validate(result)
        return parsed.cookies

    async def set_cookie(
        self,
        context: BrowsingContext | str,
        cookie: Cookie,
        partition_key: dict[str, Any] | None = None,
    ) -> None:
        """Creates or updates a cookie in a browsing context.

        Args:
            context: BrowsingContext or context ID.
            cookie: Cookie to set.
            partition_key: Optional partition key with userContext/sourceOrigin.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        cookie_dict = cookie.model_dump(by_alias=True, exclude_none=True)
        cookie_dict["value"] = {"type": "string", "value": cookie_dict["value"]}
        params: dict[str, Any] = {
            "context": ctx_id,
            "cookie": cookie_dict,
        }
        if partition_key is not None:
            params["partitionKey"] = partition_key
        await self._connection.send_command(STORAGE_SET_COOKIE, params)

    async def delete_cookies(
        self,
        context: BrowsingContext | str,
        name: str | None = None,
        domain: str | None = None,
        path: str | None = None,
        partition_key: dict[str, Any] | None = None,
    ) -> None:
        """Deletes cookies from a browsing context.

        If name, domain or path are not specified, deletes all cookies.

        Args:
            context: BrowsingContext or context ID.
            name: Name of the cookie to delete. None = all.
            domain: Domain of cookies to delete.
            path: Path of cookies to delete.
            partition_key: Optional partition key with userContext/sourceOrigin.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if name is not None:
            params["name"] = name
        if domain is not None:
            params["domain"] = domain
        if path is not None:
            params["path"] = path
        if partition_key is not None:
            params["partitionKey"] = partition_key
        await self._connection.send_command(STORAGE_DELETE_COOKIES, params)

    async def delete_cookie(
        self,
        context: BrowsingContext | str,
        name: str,
    ) -> None:
        """Deletes a single cookie by name from a browsing context.

        Convenience wrapper around delete_cookies with a name filter.

        Args:
            context: BrowsingContext or context ID.
            name: Name of the cookie to delete.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(
            STORAGE_DELETE_COOKIES,
            {"context": ctx_id, "name": name},
        )
