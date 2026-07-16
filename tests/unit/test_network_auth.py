"""Unit tests for network auth: continue_with_auth, cancel_auth."""

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


class TestContinueWithAuth:
    async def test_default_action(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_with_auth("req-1", "default")
        call = mock_connection.send_command.call_args
        assert call.args[0] == "network.continueWithAuth"
        assert call.args[1]["request"] == "req-1"
        assert call.args[1]["action"] == "default"

    async def test_cancel_action(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_with_auth("req-1", "cancel")
        params = mock_connection.send_command.call_args.args[1]
        assert params["action"] == "cancel"

    async def test_provide_credentials(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        creds = {"type": "password", "username": "admin", "password": "secret"}
        await network_module.continue_with_auth("req-1", "provideCredentials", creds)
        params = mock_connection.send_command.call_args.args[1]
        assert params["action"] == "provideCredentials"
        assert params["credentials"] == creds


class TestCancelAuth:
    async def test_cancel_auth(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.cancel_auth("req-1")
        mock_connection.send_command.assert_called_once_with(
            "network.continueWithAuth", {"request": "req-1", "action": "cancel"}
        )
