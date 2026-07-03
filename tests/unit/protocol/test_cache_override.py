"""Unit tests for cache override commands and new event models.

Covers: addCacheOverride, removeCacheOverride, network.dataReceived,
browsingContext.navigationCompleted.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.network import NetworkModule
from bidiwave.protocol.events import (
    BrowsingContextNavigationCompletedEvent,
    NetworkDataReceivedEvent,
    parse_event,
)

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def network_module(mock_connection: MockConn) -> NetworkModule:
    return NetworkModule(mock_connection)


class TestAddCacheOverride:
    async def test_add_cache_override_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cache": "cache-1"}
        result = await network_module.add_cache_override(
            url="https://example.com/api",
        )
        assert result == "cache-1"
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.addCacheOverride"
        assert call_args.args[1]["url"] == "https://example.com/api"
        assert call_args.args[1]["method"] == "GET"
        assert call_args.args[1]["statusCode"] == 200

    async def test_add_cache_override_with_body(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cache": "cache-2"}
        result = await network_module.add_cache_override(
            url="https://example.com/data",
            method="POST",
            status_code=201,
            headers=[{"name": "Content-Type", "value": {"value": "application/json"}}],
            body="eyJkYXRhIjogInRlc3QifQ==",
            contexts=["ctx-1"],
        )
        assert result == "cache-2"
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["method"] == "POST"
        assert call_args.args[1]["statusCode"] == 201
        assert call_args.args[1]["body"] == "eyJkYXRhIjogInRlc3QifQ=="
        assert call_args.args[1]["contexts"] == ["ctx-1"]


class TestRemoveCacheOverride:
    async def test_remove_cache_override(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.remove_cache_override("cache-1")
        mock_connection.send_command.assert_called_once_with(
            "network.removeCacheOverride", {"cache": "cache-1"}
        )


class TestNetworkDataReceivedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "request": "req-1",
            "data": "SGVsbG8=",
            "dataSize": 5,
        }
        event = parse_event("network.dataReceived", params)
        assert isinstance(event, NetworkDataReceivedEvent)
        assert event.context == "ctx-1"
        assert event.request == "req-1"
        assert event.data == "SGVsbG8="
        assert event.data_size == 5
        assert event.redirect_count == 0

    def test_parse_with_redirect(self) -> None:
        params = {
            "request": "req-2",
            "data": "Qm9uam91cg==",
            "dataSize": 8,
            "redirectCount": 1,
        }
        event = parse_event("network.dataReceived", params)
        assert isinstance(event, NetworkDataReceivedEvent)
        assert event.redirect_count == 1
        assert event.context is None


class TestBrowsingContextNavigationCompletedEvent:
    def test_parse_complete(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com",
            "navigation": "nav-1",
            "status": "complete",
        }
        event = parse_event("browsingContext.navigationCompleted", params)
        assert isinstance(event, BrowsingContextNavigationCompletedEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com"
        assert event.navigation == "nav-1"
        assert event.status == "complete"

    def test_parse_canceled(self) -> None:
        params = {
            "context": "ctx-2",
            "url": "https://canceled.com",
            "status": "canceled",
        }
        event = parse_event("browsingContext.navigationCompleted", params)
        assert isinstance(event, BrowsingContextNavigationCompletedEvent)
        assert event.status == "canceled"
        assert event.navigation is None
