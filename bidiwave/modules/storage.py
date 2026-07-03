"""Storage module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bidiwave.protocol.constants import (
    STORAGE_DELETE_COOKIE,
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
    ) -> list[Cookie]:
        """Gets all cookies from a browsing context.

        Args:
            context: BrowsingContext or context ID.

        Returns:
            List of Cookie.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        result = await self._connection.send_command(
            STORAGE_GET_COOKIES, {"context": ctx_id}
        )
        parsed = GetCookiesResult.model_validate(result)
        return parsed.cookies

    async def set_cookie(
        self,
        context: BrowsingContext | str,
        cookie: Cookie,
    ) -> None:
        """Creates or updates a cookie in a browsing context.

        Args:
            context: BrowsingContext or context ID.
            cookie: Cookie to set.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "cookie": cookie.model_dump(by_alias=True, exclude_none=True),
        }
        await self._connection.send_command(STORAGE_SET_COOKIE, params)

    async def delete_cookies(
        self,
        context: BrowsingContext | str,
        name: str | None = None,
        domain: str | None = None,
        path: str | None = None,
    ) -> None:
        """Deletes cookies from a browsing context.

        If name, domain or path are not specified, deletes all cookies.

        Args:
            context: BrowsingContext or context ID.
            name: Name of the cookie to delete. None = all.
            domain: Domain of cookies to delete.
            path: Path of cookies to delete.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {"context": ctx_id}
        if name is not None:
            params["name"] = name
        if domain is not None:
            params["domain"] = domain
        if path is not None:
            params["path"] = path
        await self._connection.send_command(STORAGE_DELETE_COOKIES, params)

    async def delete_cookie(
        self,
        context: BrowsingContext | str,
        name: str,
    ) -> None:
        """Deletes a single cookie by name from a browsing context.

        Unlike delete_cookies which can delete by filter, this targets
        a specific cookie by name.

        Args:
            context: BrowsingContext or context ID.
            name: Name of the cookie to delete.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(
            STORAGE_DELETE_COOKIE,
            {"context": ctx_id, "name": name},
        )
