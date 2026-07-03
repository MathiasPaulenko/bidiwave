"""Network module for the WebDriver BiDi protocol."""

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
    """Module for monitoring and intercepting network requests.

    Commands:
        - add_intercept / remove_intercept — request interception
        - continue_request / continue_response — continue an intercepted request/response
        - fail_request — fail an intercepted request
        - provide_response — provide a synthetic response

    Events (via subscribe):
        - network.beforeRequestSent — before a request is sent
        - network.responseCompleted — when a response completes
        - network.fetchError — when a request fails
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def add_intercept(
        self,
        phases: list[InterceptPhase],
        contexts: list[str] | None = None,
        url_patterns: list[str] | None = None,
    ) -> InterceptResult:
        """Registers an intercept to block requests at the given phases.

        Args:
            phases: Phases to intercept at (beforeRequestSent, responseStarted, authRequired).
            contexts: List of context IDs to apply to. None = all.
            url_patterns: URL patterns to intercept. None = all.

        Returns:
            InterceptResult with the intercept ID.
        """
        params: dict[str, Any] = {"phases": phases}
        if contexts:
            params["contexts"] = contexts
        if url_patterns:
            params["urlPatterns"] = url_patterns
        result = await self._connection.send_command(NETWORK_ADD_INTERCEPT, params)
        return InterceptResult.model_validate(result)

    async def remove_intercept(self, intercept: str) -> None:
        """Removes a previously registered intercept.

        Args:
            intercept: ID of the intercept to remove.
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
        """Continues an intercepted request, optionally modifying its parameters.

        Args:
            request: ID of the request to continue.
            url: Modified URL (optional).
            method: Modified HTTP method (optional).
            headers: Modified headers (optional).
            cookies: Modified cookies (optional).
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
        """Continues an intercepted response, optionally modifying it.

        Args:
            request: ID of the request.
            status_code: HTTP status code (optional).
            reason_phrase: Reason phrase (optional).
            headers: Response headers (optional).
            body: Response body in base64 (optional).
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
        """Fails an intercepted request.

        Args:
            request: ID of the request.
            error: Error message.
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
        """Provides a synthetic response without making the actual request.

        Args:
            request: ID of the request.
            status_code: HTTP status code.
            reason_phrase: Reason phrase.
            headers: Response headers.
            body: Response body in base64.
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
        """Continues an intercepted request in the authRequired phase.

        Args:
            request: ID of the request.
            action: "default" (use browser credentials),
                "cancel" (cancel auth), or
                "provideCredentials" (use provided credentials).
            credentials: Dict with "type" ("password"), "username", "password".
                Only used with action="provideCredentials".
        """
        params: dict[str, Any] = {"request": request, "action": action}
        if credentials is not None:
            params["credentials"] = credentials
        await self._connection.send_command(NETWORK_CONTINUE_WITH_AUTH, params)

    async def cancel_auth(self, request: str) -> None:
        """Cancels an intercepted request in the authRequired phase.

        Shortcut for continue_with_auth(request, action="cancel").
        """
        await self._connection.send_command(
            NETWORK_CANCEL_AUTH, {"request": request}
        )
