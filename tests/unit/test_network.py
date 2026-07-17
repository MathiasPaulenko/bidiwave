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
            {
                "phases": ["beforeRequestSent", "authRequired"],
                "urlPatterns": [{"type": "string", "pattern": "*api*"}],
            },
        )

    async def test_add_intercept_with_url_pattern_dicts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"intercept": "intercept-4"}
        await network_module.add_intercept(
            phases=["beforeRequestSent"],
            url_patterns=[
                {"type": "string", "pattern": "https://example.com/*"},
                {"type": "regex", "pattern": ".*\\.png$"},
            ],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["urlPatterns"] == [
            {"type": "string", "pattern": "https://example.com/*"},
            {"type": "regex", "pattern": ".*\\.png$"},
        ]


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

    async def test_continue_response_with_credentials(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_response(
            "req-1",
            status_code=200,
            credentials={"type": "password", "username": "u", "password": "p"},
        )
        mock_connection.send_command.assert_called_once_with(
            "network.continueResponse",
            {
                "request": "req-1",
                "statusCode": 200,
                "credentials": {"type": "password", "username": "u", "password": "p"},
            },
        )


class TestFailRequest:
    async def test_fail_request_sends_only_request_id(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        """Per spec, network.failRequest takes only the request ID."""
        await network_module.fail_request("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.failRequest",
            {"request": "req-1"},
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
        assert call_args.args[1]["body"] == {
            "type": "base64",
            "value": "eyJ0ZXN0IjogdHJ1ZX0=",
        }


class TestSetExtraHeaders:
    async def test_set_extra_headers_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_extra_headers(
            [{"name": "X-Custom", "value": {"text": "test"}}],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.setExtraHeaders"
        assert len(call_args.args[1]["headers"]) == 1
        assert call_args.args[1]["headers"][0]["name"] == "X-Custom"

    async def test_set_extra_headers_with_contexts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_extra_headers(
            [{"name": "Authorization", "value": {"text": "Bearer token"}}],
            contexts=["ctx-1", "ctx-2"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.setExtraHeaders"
        assert call_args.args[1]["contexts"] == ["ctx-1", "ctx-2"]

    async def test_set_extra_headers_with_user_contexts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_extra_headers(
            [{"name": "X-Trace", "value": {"text": "abc"}}],
            user_contexts=["uc-1"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["userContexts"] == ["uc-1"]


class TestSetCacheBehavior:
    async def test_set_cache_behavior_bypass(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_cache_behavior("bypass")
        mock_connection.send_command.assert_called_once_with(
            "network.setCacheBehavior", {"cacheBehavior": "bypass"}
        )

    async def test_set_cache_behavior_default_with_contexts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_cache_behavior(
            "default", contexts=["ctx-1"], user_contexts=["uc-1"]
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.setCacheBehavior"
        assert call_args.args[1]["cacheBehavior"] == "default"
        assert call_args.args[1]["contexts"] == ["ctx-1"]
        assert call_args.args[1]["userContexts"] == ["uc-1"]

    async def test_set_cache_behavior_clear(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_cache_behavior()
        mock_connection.send_command.assert_called_once_with(
            "network.setCacheBehavior", {}
        )


class TestAddDataCollector:
    async def test_add_data_collector_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"collector": "dc-1"}
        result = await network_module.add_data_collector(
            data_types=["response"],
            max_encoded_data_size=4096,
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.addDataCollector"
        assert call_args.args[1]["dataTypes"] == ["response"]
        assert call_args.args[1]["maxEncodedDataSize"] == 4096
        assert result == "dc-1"

    async def test_add_data_collector_with_contexts(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"collector": "dc-2"}
        await network_module.add_data_collector(
            data_types=["request", "response"],
            max_encoded_data_size=8192,
            collector_type="blob",
            contexts=["ctx-1"],
            user_contexts=["uc-1"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["dataTypes"] == ["request", "response"]
        assert call_args.args[1]["maxEncodedDataSize"] == 8192
        assert call_args.args[1]["collectorType"] == "blob"
        assert call_args.args[1]["contexts"] == ["ctx-1"]
        assert call_args.args[1]["userContexts"] == ["uc-1"]


class TestRemoveDataCollector:
    async def test_remove_data_collector(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.remove_data_collector("dc-1")
        mock_connection.send_command.assert_called_once_with(
            "network.removeDataCollector", {"collector": "dc-1"}
        )


class TestGetData:
    async def test_get_data_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"bytes": {"type": "base64", "value": ""}}
        result = await network_module.get_data("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.getData",
            {"request": "req-1", "dataType": "response"},
        )
        assert "bytes" in result

    async def test_get_data_with_collector_and_disown(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"bytes": {"type": "base64", "value": ""}}
        await network_module.get_data(
            "req-1", data_type="request", collector_id="dc-1", disown=True
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["request"] == "req-1"
        assert call_args.args[1]["dataType"] == "request"
        assert call_args.args[1]["collector"] == "dc-1"
        assert call_args.args[1]["disown"] is True


class TestDisownData:
    async def test_disown_data_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.disown_data("dc-1", "req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.disownData",
            {"dataType": "response", "collector": "dc-1", "request": "req-1"},
        )

    async def test_disown_data_with_data_type(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.disown_data("dc-1", "req-1", data_type="request")
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.disownData"
        assert call_args.args[1]["dataType"] == "request"
        assert call_args.args[1]["collector"] == "dc-1"
        assert call_args.args[1]["request"] == "req-1"
