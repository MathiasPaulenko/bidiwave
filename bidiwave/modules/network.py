"""Módulo network del protocolo BiDi."""

from __future__ import annotations

from typing import Any, Literal

from bidiwave.protocol.constants import (
    NETWORK_ADD_INTERCEPT,
    NETWORK_CANCEL_AUTH,
    NETWORK_CONTINUE_REQUEST,
    NETWORK_CONTINUE_RESPONSE,
    NETWORK_CONTINUE_WITH_AUTH,
    NETWORK_FAIL_REQUEST,
    NETWORK_PROVIDE_RESPONSE,
    NETWORK_REMOVE_INTERCEPT,
)
from bidiwave.protocol.results import InterceptResult
from bidiwave.transport.connection import Connection

InterceptPhase = Literal["beforeRequestSent", "responseStarted", "authRequired"]


class NetworkModule:
    """Módulo para monitorear e interceptar requests de red.

    Comandos:
        - add_intercept / remove_intercept — interceptación de requests
        - continue_request / continue_response — continuar un request/response interceptado
        - fail_request — fallar un request interceptado
        - provide_response — proveer una respuesta sintética

    Eventos (vía subscribe):
        - network.beforeRequestSent — antes de enviar un request
        - network.responseCompleted — cuando un response se completa
        - network.fetchError — cuando un request falla
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def add_intercept(
        self,
        phases: list[InterceptPhase],
        contexts: list[str] | None = None,
        url_patterns: list[str] | None = None,
    ) -> InterceptResult:
        """Registra un intercept para bloquear requests en las fases indicadas.

        Args:
            phases: Fases en las que interceptar (beforeRequestSent, responseStarted, authRequired).
            contexts: Lista de context IDs donde aplicar. None = todos.
            url_patterns: Patrones de URL a interceptar. None = todas.

        Returns:
            InterceptResult con el ID del intercept.
        """
        params: dict[str, Any] = {"phases": phases}
        if contexts:
            params["contexts"] = contexts
        if url_patterns:
            params["urlPatterns"] = url_patterns
        result = await self._connection.send_command(NETWORK_ADD_INTERCEPT, params)
        return InterceptResult.model_validate(result)

    async def remove_intercept(self, intercept: str) -> None:
        """Elimina un intercept previamente registrado.

        Args:
            intercept: ID del intercept a eliminar.
        """
        await self._connection.send_command(
            NETWORK_REMOVE_INTERCEPT, {"intercept": intercept}
        )

    async def continue_request(
        self,
        request: str,
        url: str | None = None,
        method: str | None = None,
        headers: list[dict[str, str]] | None = None,
        cookies: list[dict[str, Any]] | None = None,
    ) -> None:
        """Continúa un request interceptado, opcionalmente modificando sus parámetros.

        Args:
            request: ID del request a continuar.
            url: URL modificada (opcional).
            method: método HTTP modificado (opcional).
            headers: headers modificados (opcional).
            cookies: cookies modificadas (opcional).
        """
        params: dict[str, Any] = {"request": request}
        if url is not None:
            params["url"] = url
        if method is not None:
            params["method"] = method
        if headers is not None:
            params["headers"] = headers
        if cookies is not None:
            params["cookies"] = cookies
        await self._connection.send_command(NETWORK_CONTINUE_REQUEST, params)

    async def continue_response(
        self,
        request: str,
        status_code: int | None = None,
        reason_phrase: str | None = None,
        headers: list[dict[str, str]] | None = None,
        body: str | None = None,
    ) -> None:
        """Continúa un response interceptado, opcionalmente modificándolo.

        Args:
            request: ID del request.
            status_code: código de status HTTP (opcional).
            reason_phrase: reason phrase (opcional).
            headers: headers del response (opcional).
            body: body del response en base64 (opcional).
        """
        params: dict[str, Any] = {"request": request}
        if status_code is not None:
            params["statusCode"] = status_code
        if reason_phrase is not None:
            params["reasonPhrase"] = reason_phrase
        if headers is not None:
            params["headers"] = headers
        if body is not None:
            params["body"] = body
        await self._connection.send_command(NETWORK_CONTINUE_RESPONSE, params)

    async def fail_request(
        self,
        request: str,
        error: str = "Failed",
    ) -> None:
        """Falla un request interceptado.

        Args:
            request: ID del request.
            error: Mensaje de error.
        """
        await self._connection.send_command(
            NETWORK_FAIL_REQUEST, {"request": request, "error": error}
        )

    async def provide_response(
        self,
        request: str,
        status_code: int = 200,
        reason_phrase: str = "OK",
        headers: list[dict[str, str]] | None = None,
        body: str | None = None,
    ) -> None:
        """Provee una respuesta sintética sin hacer el request real.

        Args:
            request: ID del request.
            status_code: código de status HTTP.
            reason_phrase: reason phrase.
            headers: headers del response.
            body: body del response en base64.
        """
        params: dict[str, Any] = {
            "request": request,
            "statusCode": status_code,
            "reasonPhrase": reason_phrase,
        }
        if headers is not None:
            params["headers"] = headers
        if body is not None:
            params["body"] = body
        await self._connection.send_command(NETWORK_PROVIDE_RESPONSE, params)

    async def continue_with_auth(
        self,
        request: str,
        action: Literal["default", "cancel", "provideCredentials"],
        credentials: dict[str, str] | None = None,
    ) -> None:
        """Continúa un request interceptado en fase authRequired.

        Args:
            request: ID del request.
            action: "default" (usar credenciales del browser),
                "cancel" (cancelar la auth), o
                "provideCredentials" (usar credentials provistas).
            credentials: Dict con "type" ("password"), "username", "password".
                Solo usado con action="provideCredentials".
        """
        params: dict[str, Any] = {"request": request, "action": action}
        if credentials is not None:
            params["credentials"] = credentials
        await self._connection.send_command(NETWORK_CONTINUE_WITH_AUTH, params)

    async def cancel_auth(self, request: str) -> None:
        """Cancela un request interceptado en fase authRequired.

        Atajo para continue_with_auth(request, action="cancel").
        """
        await self._connection.send_command(
            NETWORK_CANCEL_AUTH, {"request": request}
        )
