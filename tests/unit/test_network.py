"""Unit tests for NetworkModule."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.network import NetworkModule
from bidiwave.protocol.results import InterceptResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def network_module(mock_connection: MockConn) -> NetworkModule:
    return NetworkModule(mock_connection)


class TestAddIntercept:
    async def test_add_intercept_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"intercept": "intercept-1"}
        result = await network_module.add_intercept(phases=["beforeRequestSent"])
        assert isinstance(result, InterceptResult)
        assert result.intercept == "intercept-1"
        mock_connection.send_command.assert_called_once_with(
            "network.addIntercept", {"phases": ["beforeRequestSent"]}
        )

    async def test_add_intercept_with_contexts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"intercept": "intercept-2"}
        await network_module.add_intercept(
            phases=["responseStarted"],
            contexts=["ctx-1", "ctx-2"],
        )
        mock_connection.send_command.assert_called_once_with(
            "network.addIntercept",
            {"phases": ["responseStarted"], "contexts": ["ctx-1", "ctx-2"]},
        )

    async def test_add_intercept_with_url_patterns(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"intercept": "intercept-3"}
        await network_module.add_intercept(
            phases=["beforeRequestSent", "authRequired"],
            url_patterns=["*api*"],
        )
        mock_connection.send_command.assert_called_once_with(
            "network.addIntercept",
            {"phases": ["beforeRequestSent", "authRequired"], "urlPatterns": ["*api*"]},
        )


class TestRemoveIntercept:
    async def test_remove_intercept(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.remove_intercept("intercept-1")
        mock_connection.send_command.assert_called_once_with(
            "network.removeIntercept", {"intercept": "intercept-1"}
        )


class TestContinueRequest:
    async def test_continue_request_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_request("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.continueRequest", {"request": "req-1"}
        )

    async def test_continue_request_with_url(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_request("req-1", url="https://modified.com")
        mock_connection.send_command.assert_called_once_with(
            "network.continueRequest",
            {"request": "req-1", "url": "https://modified.com"},
        )

    async def test_continue_request_with_all_params(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_request(
            "req-1",
            url="https://modified.com",
            method="POST",
            headers=[{"name": "X-Test", "value": {"text": "true"}}],
            cookies=[{"name": "session", "value": {"text": "abc"}}],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.continueRequest"
        assert call_args.args[1]["request"] == "req-1"
        assert call_args.args[1]["url"] == "https://modified.com"
        assert call_args.args[1]["method"] == "POST"
        assert len(call_args.args[1]["headers"]) == 1
        assert len(call_args.args[1]["cookies"]) == 1


class TestContinueResponse:
    async def test_continue_response_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_response("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.continueResponse", {"request": "req-1"}
        )

    async def test_continue_response_with_status(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_response(
            "req-1", status_code=404, reason_phrase="Not Found"
        )
        mock_connection.send_command.assert_called_once_with(
            "network.continueResponse",
            {"request": "req-1", "statusCode": 404, "reasonPhrase": "Not Found"},
        )

    async def test_continue_response_with_body(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_response(
            "req-1", status_code=200, body="SGVsbG8="
        )
        mock_connection.send_command.assert_called_once_with(
            "network.continueResponse",
            {"request": "req-1", "statusCode": 200, "body": "SGVsbG8="},
        )


class TestFailRequest:
    async def test_fail_request_default(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.fail_request("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.failRequest",
            {"request": "req-1", "error": "Failed"},
        )

    async def test_fail_request_custom_error(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.fail_request("req-1", error="ConnectionRefused")
        mock_connection.send_command.assert_called_once_with(
            "network.failRequest",
            {"request": "req-1", "error": "ConnectionRefused"},
        )


class TestProvideResponse:
    async def test_provide_response_default(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.provide_response("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.provideResponse",
            {"request": "req-1", "statusCode": 200, "reasonPhrase": "OK"},
        )

    async def test_provide_response_with_headers_and_body(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.provide_response(
            "req-1",
            status_code=201,
            reason_phrase="Created",
            headers=[{"name": "Content-Type", "value": {"text": "application/json"}}],
            body="eyJ0ZXN0IjogdHJ1ZX0=",
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.provideResponse"
        assert call_args.args[1]["statusCode"] == 201
        assert call_args.args[1]["reasonPhrase"] == "Created"
        assert len(call_args.args[1]["headers"]) == 1
        assert call_args.args[1]["body"] == "eyJ0ZXN0IjogdHJ1ZX0="
