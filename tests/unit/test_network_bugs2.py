"""Regression tests for network module bug fixes — round 2."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.network import NetworkModule
from bidiwave.protocol.results import ResponseBodyResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def network_module(mock_connection: MockConn) -> NetworkModule:
    return NetworkModule(mock_connection)


class TestContinueResponseCookies:
    """Bug 19: continue_response missing cookies parameter per W3C spec."""

    async def test_continue_response_with_cookies(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_response(
            "req-1",
            status_code=200,
            cookies=[{"name": "session", "value": {"text": "abc"}}],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert "cookies" in params
        assert len(params["cookies"]) == 1


class TestResponseBodyResultTotalSizeDefault:
    """Bug 20: ResponseBodyResult.total_size has no default — crashes if browser omits it."""

    def test_response_body_result_without_total_size(self) -> None:
        result = ResponseBodyResult.model_validate({"body": "SGVsbG8="})
        assert result.body == "SGVsbG8="
        assert result.total_size == 0

    def test_response_body_result_with_total_size(self) -> None:
        result = ResponseBodyResult.model_validate({"body": "SGVsbG8=", "totalSize": 5})
        assert result.total_size == 5


class TestContinueWithAuthCredentialsValidation:
    """Bug 21: continue_with_auth should raise when action='provideCredentials' but no credentials."""  # noqa: E501

    async def test_provide_credentials_without_credentials_raises(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        with pytest.raises(ValueError, match="credentials"):
            await network_module.continue_with_auth("req-1", "provideCredentials")

    async def test_provide_credentials_with_credentials_ok(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        creds = {"type": "password", "username": "admin", "password": "secret"}
        await network_module.continue_with_auth("req-1", "provideCredentials", creds)
        params = mock_connection.send_command.call_args.args[1]
        assert params["credentials"] == creds


class TestDeadImportCheck:
    """Bug 18: NETWORK_CANCEL_AUTH should no longer be imported in network.py."""

    def test_no_dead_import(self) -> None:
        import inspect

        import bidiwave.modules.network as net_mod

        source = inspect.getsource(net_mod)
        lines = [line for line in source.splitlines() if "NETWORK_CANCEL_AUTH" in line]
        assert len(lines) == 0

    def test_constant_removed_from_constants(self) -> None:
        import bidiwave.protocol.constants as const

        assert not hasattr(const, "NETWORK_CANCEL_AUTH")


class TestAddInterceptEmptyPhases:
    """Bug 22: add_intercept should reject empty phases list."""

    async def test_empty_phases_raises(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        with pytest.raises(ValueError, match="phases"):
            await network_module.add_intercept(phases=[])

    async def test_non_empty_phases_ok(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"intercept": "i-1"}
        await network_module.add_intercept(phases=["beforeRequestSent"])
        mock_connection.send_command.assert_called_once()


class TestNetworkEventModelFixes:
    """Bug 23-25: Event model fixes — headers type, data_size default, authRequired response."""

    def test_request_data_headers_accepts_structured_values(self) -> None:
        from bidiwave.protocol.events import NetworkRequestData

        data = NetworkRequestData.model_validate({
            "request": "req-1",
            "url": "https://example.com",
            "method": "GET",
            "headers": [{"name": "X-Test", "value": {"text": "true"}}],
        })
        assert data.headers[0]["value"] == {"text": "true"}

    def test_response_data_headers_accepts_structured_values(self) -> None:
        from bidiwave.protocol.events import NetworkResponseData

        data = NetworkResponseData.model_validate({
            "url": "https://example.com",
            "status": 200,
            "headers": [{"name": "Content-Type", "value": {"text": "application/json"}}],
        })
        assert data.headers[0]["value"] == {"text": "application/json"}

    def test_data_received_event_without_data_size(self) -> None:
        from bidiwave.protocol.events import NetworkDataReceivedEvent

        event = NetworkDataReceivedEvent.model_validate({
            "request": "req-1",
            "data": "SGVsbG8=",
        })
        assert event.data_size == 0

    def test_auth_required_event_with_response(self) -> None:
        from bidiwave.protocol.events import NetworkAuthRequiredEvent

        event = NetworkAuthRequiredEvent.model_validate({
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
            "response": {
                "url": "https://example.com",
                "status": 401,
                "statusText": "Unauthorized",
            },
        })
        assert event.response is not None
        assert event.response.status == 401

    def test_auth_required_event_without_response(self) -> None:
        from bidiwave.protocol.events import NetworkAuthRequiredEvent

        event = NetworkAuthRequiredEvent.model_validate({
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
        })
        assert event.response is None


class TestProvideResponseCookies:
    """Bug 26: provide_response missing cookies parameter per W3C spec."""

    async def test_provide_response_with_cookies(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.provide_response(
            "req-1",
            status_code=200,
            cookies=[{"name": "session", "value": {"text": "abc"}}],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert "cookies" in params
        assert len(params["cookies"]) == 1

    async def test_provide_response_without_cookies_omits_field(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.provide_response("req-1")
        params = mock_connection.send_command.call_args.args[1]
        assert "cookies" not in params
