"""Unit tests for user contexts, sandbox, CDP bridge, and auto-prompt."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.cdp import CDPModule
from bidiwave.modules.script import ScriptModule
from bidiwave.protocol.results import UserContextInfo

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


CTX_ID = "ctx-1"


class TestCreateUserContext:
    async def test_create_user_context(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"userContext": "uc-1"}
        browsing = BrowsingModule(mock_connection)
        result = await browsing.create_user_context()
        assert isinstance(result, UserContextInfo)
        assert result.user_context == "uc-1"
        mock_connection.send_command.assert_called_once_with(
            "browser.createUserContext", {}
        )


class TestRemoveUserContext:
    async def test_remove_user_context(
        self,
        mock_connection: MockConn,
    ) -> None:
        browsing = BrowsingModule(mock_connection)
        await browsing.remove_user_context("uc-1")
        mock_connection.send_command.assert_called_once_with(
            "browser.removeUserContext", {"userContext": "uc-1"}
        )


class TestGetUserContexts:
    async def test_get_user_contexts(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "userContexts": [
                {"userContext": "default"},
                {"userContext": "uc-1"},
            ]
        }
        browsing = BrowsingModule(mock_connection)
        result = await browsing.get_user_contexts()
        assert len(result) == 2
        assert result[0].user_context == "default"
        assert result[1].user_context == "uc-1"

    async def test_get_user_contexts_empty(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        browsing = BrowsingModule(mock_connection)
        result = await browsing.get_user_contexts()
        assert result == []


class TestCreateContextWithUserContext:
    async def test_create_context_with_user_context(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "context": "ctx-2",
            "url": "",
        }
        browsing = BrowsingModule(mock_connection)
        ctx = await browsing.create_context(user_context="uc-1")
        assert ctx.id == "ctx-2"
        params = mock_connection.send_command.call_args.args[1]
        assert params["userContext"] == "uc-1"


class TestSandboxEvaluate:
    async def test_evaluate_with_sandbox(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"type": "undefined"}
        script = ScriptModule(mock_connection)
        await script.evaluate(CTX_ID, "window.foo", sandbox="my-sandbox")
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"]["sandbox"] == "my-sandbox"

    async def test_evaluate_without_sandbox(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"type": "undefined"}
        script = ScriptModule(mock_connection)
        await script.evaluate(CTX_ID, "window.foo")
        params = mock_connection.send_command.call_args.args[1]
        assert "sandbox" not in params["target"]


class TestSandboxCallFunction:
    async def test_call_with_sandbox(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"type": "undefined"}
        script = ScriptModule(mock_connection)
        await script.call_function(
            CTX_ID, "() => 42", sandbox="isolated"
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"]["sandbox"] == "isolated"


class TestCDPGetSession:
    async def test_get_session(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"session": "cdp-session-1"}
        cdp = CDPModule(mock_connection)
        result = await cdp.get_session()
        assert result == "cdp-session-1"
        mock_connection.send_command.assert_called_once_with(
            "browser.cdp.getSession", {}
        )

    async def test_get_session_none(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        cdp = CDPModule(mock_connection)
        result = await cdp.get_session()
        assert result is None


class TestCDPSendCommand:
    async def test_send_command_basic(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"result": {}}
        cdp = CDPModule(mock_connection)
        await cdp.send_command("Page.reload")
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browser.cdp.sendCommand"
        assert call.args[1]["cmd"] == "Page.reload"

    async def test_send_command_with_params(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"result": {}}
        cdp = CDPModule(mock_connection)
        await cdp.send_command("Network.enable", {"maxTotalBufferSize": 10000})
        params = mock_connection.send_command.call_args.args[1]
        assert params["params"] == {"maxTotalBufferSize": 10000}

    async def test_send_command_no_params(
        self,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"result": {}}
        cdp = CDPModule(mock_connection)
        await cdp.send_command("Page.enable")
        params = mock_connection.send_command.call_args.args[1]
        assert "params" not in params
