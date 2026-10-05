"""Regression tests for network module bug fixes."""

from __future__ import annotations

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


class TestContinueWithAuthCredentialsLeak:
    """Bug 13: continue_with_auth sends credentials even when action != 'provideCredentials'."""

    async def test_default_action_no_credentials(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_with_auth(
            "req-1", "default", credentials={"type": "password", "username": "a", "password": "b"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert "credentials" not in params

    async def test_cancel_action_no_credentials(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_with_auth(
            "req-1", "cancel", credentials={"type": "password", "username": "a", "password": "b"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert "credentials" not in params

    async def test_provide_credentials_includes_credentials(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        creds = {"type": "password", "username": "admin", "password": "secret"}
        await network_module.continue_with_auth("req-1", "provideCredentials", creds)
        params = mock_connection.send_command.call_args.args[1]
        assert params["credentials"] == creds


class TestCancelAuthCommand:
    """Bug 14: cancel_auth uses 'network.cancelAuth' which is not a valid BiDi command.

    The W3C spec uses 'network.continueWithAuth' with action='cancel'.
    There is no separate 'network.cancelAuth' command.
    """

    async def test_cancel_auth_uses_continue_with_auth(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.cancel_auth("req-1")
        method = mock_connection.send_command.call_args.args[0]
        assert method == "network.continueWithAuth"
        params = mock_connection.send_command.call_args.args[1]
        assert params["action"] == "cancel"


class TestContinueRequestPostData:
    """Bug 17: continue_request missing post_data parameter per W3C spec.

    Per spec, the request body is sent as ``body`` with a BytesValue,
    not as a raw ``postData`` string.
    """

    async def test_continue_request_with_post_data(
        self,
        network_module: NetworkModule,
        mock_connection: MockConn,
    ) -> None:
        await network_module.continue_request(
            "req-1", post_data="SGVsbG8="
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["body"] == {"type": "base64", "value": "SGVsbG8="}
        assert "postData" not in params
