"""Módulo storage del protocolo BiDi."""

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
    """Módulo para manejar cookies del browser.

    Comandos:
        - get_cookies — obtiene cookies de un context
        - set_cookie — crea o actualiza una cookie
        - delete_cookies — elimina cookies

    Ejemplo:
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
        """Obtiene todas las cookies de un browsing context.

        Args:
            context: BrowsingContext o context ID.

        Returns:
            Lista de Cookie.
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
        """Crea o actualiza una cookie en un browsing context.

        Args:
            context: BrowsingContext o context ID.
            cookie: Cookie a establecer.
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
        """Elimina cookies de un browsing context.

        Si no se especifica name, domain o path, elimina todas las cookies.

        Args:
            context: BrowsingContext o context ID.
            name: Nombre de la cookie a eliminar. None = todas.
            domain: Dominio de las cookies a eliminar.
            path: Path de las cookies a eliminar.
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
