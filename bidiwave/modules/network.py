"""Network module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import Any, Literal

from bidiwave.protocol.constants import (
    NETWORK_ADD_DATA_COLLECTOR,
    NETWORK_ADD_INTERCEPT,
    NETWORK_CONTINUE_REQUEST,
    NETWORK_CONTINUE_RESPONSE,
    NETWORK_CONTINUE_WITH_AUTH,
    NETWORK_DISOWN_DATA,
    NETWORK_FAIL_REQUEST,
    NETWORK_GET_DATA,
    NETWORK_PROVIDE_RESPONSE,
    NETWORK_REMOVE_DATA_COLLECTOR,
    NETWORK_REMOVE_INTERCEPT,
    NETWORK_SET_CACHE_BEHAVIOR,
    NETWORK_SET_EXTRA_HEADERS,
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
        - set_cache_behavior — control caching for intercepted requests
        - data collectors — collect request/response bodies per spec

    Events (via subscribe):
        - network.beforeRequestSent — before a request is sent
        - network.responseStarted — when response headers arrive
        - network.responseCompleted — when a response completes
        - network.fetchError — when a request fails
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def add_intercept(
        self,
        phases: list[InterceptPhase],
        contexts: list[str] | None = None,
        url_patterns: list[str | dict[str, str]] | None = None,
    ) -> InterceptResult:
        """Registers an intercept to block requests at the given phases.

        Args:
            phases: Phases to intercept at (beforeRequestSent, responseStarted, authRequired).
            contexts: List of context IDs to apply to. None = all.
            url_patterns: URL patterns to intercept. None = all.
                Accepts plain strings (normalized to
                {"type": "string", "pattern": ...} per spec) or
                NetworkUrlPattern dicts
                (e.g. {"type": "string", "pattern": "https://example.com/*"}
                or {"type": "pattern", "protocol": "https"}).

        Returns:
            InterceptResult with the intercept ID.
        """
        if not phases:
            raise ValueError("phases must not be empty")
        params: dict[str, Any] = {"phases": phases}
        if contexts is not None:
            params["contexts"] = contexts
        if url_patterns is not None:
            params["urlPatterns"] = [
                {"type": "string", "pattern": pattern}
                if isinstance(pattern, str)
                else pattern
                for pattern in url_patterns
            ]
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
        headers: list[dict[str, Any]] | None = None,
        cookies: list[dict[str, Any]] | None = None,
        post_data: str | None = None,
    ) -> None:
        """Continues an intercepted request, optionally modifying its parameters.

        Args:
            request: ID of the request to continue.
            url: Modified URL (optional).
            method: Modified HTTP method (optional).
            headers: Modified headers (optional).
            cookies: Modified cookies (optional).
            post_data: Modified request body in base64 (optional).
                Sent as the spec-compliant ``body`` BytesValue.
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
        if post_data is not None:
            params["body"] = {"type": "base64", "value": post_data}
        await self._connection.send_command(NETWORK_CONTINUE_REQUEST, params)

    async def continue_response(
        self,
        request: str,
        status_code: int | None = None,
        reason_phrase: str | None = None,
        headers: list[dict[str, Any]] | None = None,
        cookies: list[dict[str, Any]] | None = None,
        credentials: dict[str, str] | None = None,
    ) -> None:
        """Continues an intercepted response, optionally modifying it.

        Note: per the W3C BiDi spec, ``network.continueResponse`` does not
        accept a body. Use provide_response to supply a synthetic body.

        Args:
            request: ID of the request.
            status_code: HTTP status code (optional).
            reason_phrase: Reason phrase (optional).
            headers: Response headers (optional).
            cookies: Modified cookies (optional).
            credentials: Auth credentials dict with "type" ("password"),
                "username", "password" (optional).
        """
        params: dict[str, Any] = {"request": request}
        if status_code is not None:
            params["statusCode"] = status_code
        if reason_phrase is not None:
            params["reasonPhrase"] = reason_phrase
        if headers is not None:
            params["headers"] = headers
        if cookies is not None:
            params["cookies"] = cookies
        if credentials is not None:
            params["credentials"] = credentials
        await self._connection.send_command(NETWORK_CONTINUE_RESPONSE, params)

    async def fail_request(
        self,
        request: str,
    ) -> None:
        """Fails an intercepted request.

        Per the W3C BiDi spec, ``network.failRequest`` takes only the
        request ID — no error message parameter exists.

        Args:
            request: ID of the request.
        """
        await self._connection.send_command(
            NETWORK_FAIL_REQUEST, {"request": request}
        )

    async def provide_response(
        self,
        request: str,
        status_code: int = 200,
        reason_phrase: str = "OK",
        headers: list[dict[str, Any]] | None = None,
        body: str | None = None,
        cookies: list[dict[str, Any]] | None = None,
    ) -> None:
        """Provides a synthetic response without making the actual request.

        Args:
            request: ID of the request.
            status_code: HTTP status code.
            reason_phrase: Reason phrase.
            headers: Response headers.
            body: Response body in base64. Sent as the spec-compliant
                BytesValue ``{"type": "base64", "value": ...}``.
            cookies: Cookies to set (optional).
        """
        params: dict[str, Any] = {
            "request": request,
            "statusCode": status_code,
            "reasonPhrase": reason_phrase,
        }
        if headers is not None:
            params["headers"] = headers
        if body is not None:
            params["body"] = {"type": "base64", "value": body}
        if cookies is not None:
            params["cookies"] = cookies
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
        if action == "provideCredentials" and credentials is None:
            raise ValueError("credentials are required when action='provideCredentials'")
        params: dict[str, Any] = {"request": request, "action": action}
        if credentials is not None and action == "provideCredentials":
            params["credentials"] = credentials
        await self._connection.send_command(NETWORK_CONTINUE_WITH_AUTH, params)

    async def cancel_auth(self, request: str) -> None:
        """Cancels an intercepted request in the authRequired phase.

        Shortcut for continue_with_auth(request, action="cancel").
        """
        await self._connection.send_command(
            NETWORK_CONTINUE_WITH_AUTH, {"request": request, "action": "cancel"}
        )

    async def set_extra_headers(
        self,
        headers: list[dict[str, Any]],
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> None:
        """Sets extra headers on future network requests.

        Args:
            headers: List of header objects with 'name' and 'value' keys.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"headers": headers}
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        await self._connection.send_command(NETWORK_SET_EXTRA_HEADERS, params)

    async def set_cache_behavior(
        self,
        cache_behavior: Literal["bypass", "default"],
        contexts: list[str] | None = None,
    ) -> None:
        """Sets the cache behavior for future network requests.

        Args:
            cache_behavior: "bypass" to bypass cache, "default" for normal
                cache behavior. Required per spec — use "default" to
                clear a bypass override.
            contexts: Context IDs to apply to. None = all.
        """
        params: dict[str, Any] = {"cacheBehavior": cache_behavior}
        if contexts is not None:
            params["contexts"] = contexts
        await self._connection.send_command(
            NETWORK_SET_CACHE_BEHAVIOR, params
        )

    async def add_data_collector(
        self,
        data_types: list[Literal["request", "response"]],
        max_encoded_data_size: int,
        collector_type: Literal["blob"] | None = None,
        contexts: list[str] | None = None,
        user_contexts: list[str] | None = None,
    ) -> str:
        """Adds a network data collector for collecting request/response data.

        Args:
            data_types: Data types to collect ("request" and/or "response").
            max_encoded_data_size: Maximum encoded data size in bytes.
            collector_type: Collector type ("blob"). Optional per spec.
            contexts: Context IDs to apply to. None = all.
            user_contexts: User context IDs to apply to. None = all.

        Returns:
            Data collector ID.
        """
        params: dict[str, Any] = {
            "dataTypes": data_types,
            "maxEncodedDataSize": max_encoded_data_size,
        }
        if collector_type is not None:
            params["collectorType"] = collector_type
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        result = await self._connection.send_command(
            NETWORK_ADD_DATA_COLLECTOR, params
        )
        return str(result.get("collector", ""))

    async def remove_data_collector(self, collector_id: str) -> None:
        """Removes a previously added data collector.

        Args:
            collector_id: ID returned by add_data_collector.
        """
        await self._connection.send_command(
            NETWORK_REMOVE_DATA_COLLECTOR, {"collector": collector_id}
        )

    async def get_data(
        self,
        request: str,
        data_type: Literal["request", "response"] = "response",
        collector_id: str | None = None,
        disown: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieves data collected by a data collector.

        Args:
            request: ID of the request whose data to fetch.
            data_type: Data type to retrieve ("request" or "response").
            collector_id: ID of the data collector (optional per spec).
            disown: Whether to release the data after retrieval.

        Returns:
            Collected data dict (contains a BytesValue under "bytes").
        """
        params: dict[str, Any] = {
            "request": request,
            "dataType": data_type,
        }
        if collector_id is not None:
            params["collector"] = collector_id
        if disown is not None:
            params["disown"] = disown
        result = await self._connection.send_command(
            NETWORK_GET_DATA, params
        )
        return result

    async def disown_data(
        self,
        collector_id: str,
        request: str,
        data_type: Literal["request", "response"] = "response",
    ) -> None:
        """Disowns previously collected data.

        Per the spec, network.disownData requires the data type, the
        collector ID and the request ID.

        Args:
            collector_id: ID of the data collector.
            request: ID of the request whose data to disown.
            data_type: Data type to disown ("request" or "response").
        """
        params: dict[str, Any] = {
            "dataType": data_type,
            "collector": collector_id,
            "request": request,
        }
        await self._connection.send_command(
            NETWORK_DISOWN_DATA, params
        )
