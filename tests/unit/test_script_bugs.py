"""Regression tests for script module bug fixes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.exceptions import JavaScriptError
from bidiwave.modules.script import ScriptModule
from bidiwave.protocol.remote_value import RemoteValue

CTX_ID = "ctx-123"

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def script_module(mock_connection: MockConn) -> ScriptModule:
    return ScriptModule(mock_connection)


class TestRemoteValueParseException:
    """Bug 6: RemoteValue.parse silently swallows JS exceptions."""

    def test_parse_exception_type_raises(self) -> None:
        data = {
            "type": "exception",
            "exceptionDetails": {
                "text": "SyntaxError: unexpected token",
                "lineNumber": 1,
                "columnNumber": 0,
            },
        }
        with pytest.raises(JavaScriptError, match="SyntaxError"):
            RemoteValue.parse(data)

    def test_parse_exception_with_exception_details(self) -> None:
        data = {
            "type": "exception",
            "exceptionDetails": {"text": "ReferenceError: x is not defined"},
        }
        with pytest.raises(JavaScriptError, match="ReferenceError"):
            RemoteValue.parse(data)

    def test_parse_exception_with_no_text(self) -> None:
        data = {"type": "exception", "exceptionDetails": {}}
        with pytest.raises(JavaScriptError):
            RemoteValue.parse(data)

    def test_parse_exception_no_exception_details(self) -> None:
        data = {"type": "exception"}
        with pytest.raises(JavaScriptError):
            RemoteValue.parse(data)


class TestEvaluateRaisesOnException:
    """Bug 7: script.evaluate must raise JavaScriptError on exception results."""

    async def test_evaluate_exception_raises(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "exception",
            "exceptionDetails": {"text": "TypeError: cannot read property"},
        }
        with pytest.raises(JavaScriptError, match="TypeError"):
            await script_module.evaluate(CTX_ID, "bad.code()")

    async def test_call_function_exception_raises(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "exception",
            "exceptionDetails": {"text": "SyntaxError: invalid syntax"},
        }
        with pytest.raises(JavaScriptError, match="SyntaxError"):
            await script_module.call_function(CTX_ID, "() => { bad }")


class TestDisownSandbox:
    """Bug 8: script.disown missing sandbox parameter support."""

    async def test_disown_with_sandbox(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        await script_module.disown(CTX_ID, ["handle-1"], sandbox="my-sandbox")
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"]["sandbox"] == "my-sandbox"

    async def test_disown_without_sandbox_omits_it(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        await script_module.disown(CTX_ID, ["handle-1"])
        params = mock_connection.send_command.call_args.args[1]
        assert "sandbox" not in params["target"]
