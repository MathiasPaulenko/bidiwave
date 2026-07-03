"""Unit tests for network.setCacheOverride command."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.network import NetworkModule

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def network_module(mock_connection: MockConn) -> NetworkModule:
    return NetworkModule(mock_connection)


class TestSetCacheOverride:
    async def test_set_cache_override_basic(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_cache_override(
            url="https://example.com/api",
        )
        mock_connection.send_command.assert_called_once()
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "network.setCacheOverride"
        assert call_args.args[1]["url"] == "https://example.com/api"
        assert call_args.args[1]["method"] == "GET"
        assert call_args.args[1]["statusCode"] == 200

    async def test_set_cache_override_with_body(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.set_cache_override(
            url="https://example.com/data",
            method="POST",
            status_code=201,
            headers=[{"name": "Content-Type", "value": {"value": "application/json"}}],
            body="eyJkYXRhIjogInRlc3QifQ==",
            contexts=["ctx-1"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["method"] == "POST"
        assert call_args.args[1]["statusCode"] == 201
        assert call_args.args[1]["body"] == "eyJkYXRhIjogInRlc3QifQ=="
        assert call_args.args[1]["contexts"] == ["ctx-1"]
