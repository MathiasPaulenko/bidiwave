"""Regression tests for script module bug fixes — round 2."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.exceptions import JavaScriptError
from bidiwave.modules.script import ScriptModule
from bidiwave.protocol.remote_value import (
    NumberValue,
    RemoteValue,
    StringValue,
)

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


class TestCallFunctionMissingThis:
    """Bug 9: call_function doesn't send 'this' parameter per W3C spec."""

    async def test_call_function_includes_this(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "number", "value": 42},
        }
        await script_module.call_function(CTX_ID, "() => 42")
        params = mock_connection.send_command.call_args.args[1]
        assert "this" in params
        assert params["this"] == {"type": "undefined"}


class TestNumberValueNaN:
    """Bug 10: NumberValue crashes on NaN/Infinity which come as strings."""

    def test_parse_nan(self) -> None:
        data = {"type": "success", "result": {"type": "number", "value": "NaN"}}
        result = RemoteValue.parse(data)
        assert isinstance(result, NumberValue)
        import math
        assert math.isnan(result.value)

    def test_parse_infinity(self) -> None:
        data = {"type": "success", "result": {"type": "number", "value": "Infinity"}}
        result = RemoteValue.parse(data)
        assert isinstance(result, NumberValue)
        assert result.value == float("inf")

    def test_parse_negative_infinity(self) -> None:
        data = {"type": "success", "result": {"type": "number", "value": "-Infinity"}}
        result = RemoteValue.parse(data)
        assert isinstance(result, NumberValue)
        assert result.value == float("-inf")


class TestAddPreloadScriptEmptyArguments:
    """Bug 11: add_preload_script always sends arguments: [] which some browsers reject."""

    async def test_no_arguments_omits_field(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "pre-1"}
        await script_module.add_preload_script("() => {}")
        params = mock_connection.send_command.call_args.args[1]
        assert "arguments" not in params


class TestRemoteValueParseSuccessNoResult:
    """Bug 12: RemoteValue.parse on {type: 'success'} without result key returns bare RemoteValue."""

    def test_parse_success_without_result_returns_undefined(self) -> None:
        data = {"type": "success"}
        result = RemoteValue.parse(data)
        # Should not be a bare RemoteValue with type='success'
        assert result.type != "success"


class TestEvaluateWithSandbox:
    """Ensure evaluate passes sandbox in target."""

    async def test_evaluate_with_sandbox(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.evaluate(CTX_ID, "1+1", sandbox="my-sandbox")
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"]["sandbox"] == "my-sandbox"

    async def test_evaluate_without_sandbox_omits_it(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.evaluate(CTX_ID, "1+1")
        params = mock_connection.send_command.call_args.args[1]
        assert "sandbox" not in params["target"]


class TestCallFunctionWithSandbox:
    """Ensure call_function passes sandbox in target."""

    async def test_call_function_with_sandbox(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.call_function(CTX_ID, "() => 'ok'", sandbox="sb")
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"]["sandbox"] == "sb"


class TestEvaluateWithRealm:
    """evaluate should support realm target per spec."""

    async def test_evaluate_with_realm(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.evaluate(realm="realm-123", expression="1+1")
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"] == {"realm": "realm-123"}

    async def test_evaluate_with_serialization_options(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.evaluate(
            CTX_ID, "1+1", serialization_options={"maxObjectDepth": 2}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["serializationOptions"] == {"maxObjectDepth": 2}

    async def test_evaluate_with_user_activation(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.evaluate(CTX_ID, "1+1", user_activation=True)
        params = mock_connection.send_command.call_args.args[1]
        assert params["userActivation"] is True


class TestCallFunctionWithThis:
    """call_function should accept custom this parameter per spec."""

    async def test_call_function_with_custom_this(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        this_val = {"type": "number", "value": 42}
        await script_module.call_function(
            CTX_ID, "function() { return this; }", this=this_val
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["this"] == this_val

    async def test_call_function_default_this_undefined(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "type": "success",
            "result": {"type": "string", "value": "ok"},
        }
        await script_module.call_function(CTX_ID, "() => 'ok'")
        params = mock_connection.send_command.call_args.args[1]
        assert params["this"] == {"type": "undefined"}


class TestRemovePreloadScript:
    """script.removePreloadScript should be supported per spec."""

    async def test_remove_preload_script(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        await script_module.remove_preload_script("script-123")
        method = mock_connection.send_command.call_args.args[0]
        params = mock_connection.send_command.call_args.args[1]
        assert method == "script.removePreloadScript"
        assert params == {"script": "script-123"}


class TestDisownWithRealm:
    """disown should support realm target per spec."""

    async def test_disown_with_realm(
        self,
        script_module: ScriptModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        await script_module.disown(realm="realm-456", handles=["h1"])
        params = mock_connection.send_command.call_args.args[1]
        assert params["target"] == {"realm": "realm-456"}
        assert params["handles"] == ["h1"]
