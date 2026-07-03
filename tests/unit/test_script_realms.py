"""Unit tests for script.get_realms."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.script import ScriptModule
from bidiwave.protocol.results import RealmInfo

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def script_module(mock_connection: MockConn) -> ScriptModule:
    return ScriptModule(mock_connection)


class TestGetRealms:
    async def test_get_all_realms(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "realms": [
                {"realm": "r1", "origin": "https://example.com", "type": "window"},
                {"realm": "r2", "origin": "https://other.com", "type": "dedicated-worker"},
            ]
        }
        result = await script_module.get_realms()
        assert len(result) == 2
        assert isinstance(result[0], RealmInfo)
        assert result[0].realm == "r1"
        assert result[0].type == "window"
        mock_connection.send_command.assert_called_once_with(
            "script.getRealms", {}
        )

    async def test_get_realms_by_context(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"realms": []}
        await script_module.get_realms(context="ctx-1")
        params = mock_connection.send_command.call_args.args[1]
        assert params["context"] == "ctx-1"

    async def test_get_realms_by_type(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"realms": []}
        await script_module.get_realms(type="service-worker")
        params = mock_connection.send_command.call_args.args[1]
        assert params["type"] == "service-worker"

    async def test_get_realms_empty(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        result = await script_module.get_realms()
        assert result == []
