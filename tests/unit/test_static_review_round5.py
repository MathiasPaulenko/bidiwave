"""Regression tests for the round-5 deep audit fixes."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets
from pydantic import ValidationError

from bidiwave.config import ClientConfig
from bidiwave.exceptions import (
    BiDiConnectionError,
    BiDiTimeoutError,
    NoSuchNetworkCollectorError,
    ProtocolError,
    map_error,
)
from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.emulation import EmulationModule
from bidiwave.modules.input import InputModule
from bidiwave.modules.network import NetworkModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.session import SessionModule
from bidiwave.protocol.capabilities import detect_capabilities
from bidiwave.protocol.events import LogEntryAddedEvent
from bidiwave.protocol.remote_value import (
    NodeValue,
    NumberValue,
    ObjectValue,
    RemoteValue,
)
from bidiwave.transport.connection import Connection, TransportConfig


def _mock_conn() -> MagicMock:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


class TestPopulateByName:
    """Aliased fields must be settable by their Python name too."""

    def test_node_value_shared_id_by_name(self) -> None:
        node = NodeValue(shared_id="abc")
        assert node.shared_id == "abc"

    def test_node_value_shared_id_by_alias(self) -> None:
        node = NodeValue(sharedId="abc")
        assert node.shared_id == "abc"

    def test_log_event_stack_trace_by_name(self) -> None:
        event = LogEntryAddedEvent(
            level="info",
            text="msg",
            timestamp=1,
            source={},
            stack_trace={"callFrames": []},
        )
        assert event.stack_trace == {"callFrames": []}


class TestDetectCapabilitiesRobust:
    """detect_capabilities must not crash on malformed responses."""

    def test_none_browser_name(self) -> None:
        caps = detect_capabilities(
            {"result": {"capabilities": {"browserName": None}}}
        )
        assert caps.browser_name == ""
        assert caps.supports_script is False

    def test_non_dict_capabilities(self) -> None:
        caps = detect_capabilities({"result": {"capabilities": "garbage"}})
        assert caps.browser_name == ""
        assert caps.supports_browsing is False

    def test_non_dict_response(self) -> None:
        caps = detect_capabilities("not a dict")  # type: ignore[arg-type]
        assert caps.supports_browsing is False

    def test_non_dict_result(self) -> None:
        caps = detect_capabilities({"result": 42})
        assert caps.supports_script is False

    def test_normal_response_still_works(self) -> None:
        caps = detect_capabilities(
            {
                "result": {
                    "capabilities": {
                        "browserName": "edge",
                        "browserVersion": "157",
                    }
                }
            }
        )
        assert caps.browser_name == "edge"
        assert caps.supports_script is True


class TestRemoteValueParseValidation:
    """RemoteValue.parse must raise a meaningful error on non-dict input."""

    def test_parse_non_dict_raises_protocol_error(self) -> None:
        with pytest.raises(ProtocolError):
            RemoteValue.parse("not a dict")  # type: ignore[arg-type]

    def test_parse_none_raises_protocol_error(self) -> None:
        with pytest.raises(ProtocolError):
            RemoteValue.parse(None)  # type: ignore[arg-type]

    def test_parse_success_with_non_dict_result(self) -> None:
        with pytest.raises(ProtocolError):
            RemoteValue.parse({"type": "success", "result": 42})

    def test_parse_exception_with_non_dict_details(self) -> None:
        from bidiwave.exceptions import JavaScriptError

        with pytest.raises(JavaScriptError):
            RemoteValue.parse({"type": "exception", "exceptionDetails": "x"})


class TestObjectValueKeys:
    """RemoteValue dict keys must be unwrapped, not stringified."""

    def test_remote_value_key_unwrapped(self) -> None:
        obj = ObjectValue(
            value=[
                [{"type": "string", "value": "mykey"}, {"type": "number", "value": 1}]
            ]
        )
        assert "mykey" in obj.value
        assert isinstance(obj.value["mykey"], NumberValue)

    def test_plain_string_key(self) -> None:
        obj = ObjectValue(value=[["k", {"type": "number", "value": 5}]])
        assert isinstance(obj.value["k"], NumberValue)
        assert obj.value["k"].value == 5


class TestNumberValueSpecials:
    """Non-finite numbers arrive as strings per spec and must be coerced."""

    def test_nan_string(self) -> None:
        import math

        assert math.isnan(NumberValue(value="NaN").value)

    def test_infinity_string(self) -> None:
        import math

        assert math.isinf(NumberValue(value="Infinity").value)

    def test_negative_infinity_string(self) -> None:
        import math

        v = NumberValue(value="-Infinity").value
        assert math.isinf(v) and v < 0

    def test_negative_zero(self) -> None:
        v = NumberValue(value="-0").value
        assert v == 0


class TestErrorMapping:
    def test_no_such_network_collector(self) -> None:
        err = map_error("no such network collector", "gone")
        assert isinstance(err, NoSuchNetworkCollectorError)


class TestConfigValidation:
    """ClientConfig/TransportConfig must reject nonsensical values."""

    @pytest.mark.parametrize("timeout", [0, -5])
    def test_invalid_timeout(self, timeout: float) -> None:
        with pytest.raises(ValidationError):
            ClientConfig(timeout=timeout)
        with pytest.raises(ValidationError):
            TransportConfig(timeout=timeout)

    def test_invalid_max_retries(self) -> None:
        with pytest.raises(ValidationError):
            ClientConfig(max_retries=-1)
        with pytest.raises(ValidationError):
            TransportConfig(max_retries=-1)

    def test_zero_max_retries_allowed(self) -> None:
        assert ClientConfig(max_retries=0).max_retries == 0
        assert TransportConfig(max_retries=0).max_retries == 0

    @pytest.mark.parametrize("delay", [-1.0, -0.01])
    def test_invalid_retry_delay(self, delay: float) -> None:
        with pytest.raises(ValidationError):
            ClientConfig(retry_delay=delay)

    def test_invalid_retry_backoff(self) -> None:
        with pytest.raises(ValidationError):
            ClientConfig(retry_backoff=-1)


class TestSendCommandLeak:
    """send_command must not leak correlation futures on early failure."""

    async def test_serialization_failure_no_leak(self) -> None:
        conn = Connection("ws://localhost:9999")
        conn._ws = AsyncMock()
        with pytest.raises(TypeError):
            await conn.send_command("x.y", {"bad": object()})
        assert conn._correlator._pending == {}

    async def test_non_dict_params_type_error(self) -> None:
        conn = Connection("ws://localhost:9999")
        conn._ws = AsyncMock()
        with pytest.raises(TypeError, match="params must be a dict"):
            await conn.send_command("x.y", ["nope"])  # type: ignore[arg-type]
        assert conn._correlator._pending == {}


class TestConnectErrorWrapping:
    async def test_connect_timeout_is_bidi_timeout(self) -> None:
        conn = Connection(
            "ws://localhost:9999", config=TransportConfig(timeout=0.05)
        )

        async def slow(*args: object, **kwargs: object) -> None:
            await asyncio.sleep(30)

        with (
            patch.object(websockets, "connect", side_effect=slow),
            pytest.raises(BiDiTimeoutError),
        ):
            await conn.connect()

    async def test_connect_failure_wrapped(self) -> None:
        conn = Connection("ws://localhost:9999")
        with (
            patch.object(
                websockets, "connect", AsyncMock(side_effect=OSError("refused"))
            ),
            pytest.raises(BiDiConnectionError, match="Failed to connect"),
        ):
            await conn.connect()


class TestReceiveLoopRobustness:
    async def test_non_dict_result_rejects_with_protocol_error(self) -> None:
        conn = Connection("ws://localhost:9999")
        ws = AsyncMock()
        ws.__aiter__ = MagicMock(return_value=ws)

        async def anext() -> str:
            await asyncio.sleep(0.05)
            return json.dumps({"id": 1, "type": "success", "result": [1, 2]})

        ws.__anext__ = AsyncMock(side_effect=anext)

        with patch.object(
            websockets, "connect", AsyncMock(return_value=ws)
        ):
            await conn.connect()
            with pytest.raises(ProtocolError):
                await asyncio.wait_for(conn.send_command("x.y", {}), timeout=5)
        await conn.close()

    async def test_pending_command_fails_fast_on_disconnect(self) -> None:
        """In-flight futures must be rejected when the socket dies even
        if a reconnect succeeds — never hang until the send timeout."""
        conn = Connection(
            "ws://localhost:9999",
            config=TransportConfig(
                max_retries=1, retry_delay=0.01, retry_backoff=1.0
            ),
        )
        ws1 = AsyncMock()
        ws1.__aiter__ = MagicMock(return_value=ws1)

        async def anext1() -> str:
            await asyncio.sleep(0.05)
            raise websockets.ConnectionClosed(None, None)

        ws1.__anext__ = AsyncMock(side_effect=anext1)

        ws2 = AsyncMock()
        ws2.__aiter__ = MagicMock(return_value=ws2)

        async def anext2() -> str:
            await asyncio.sleep(60)
            return ""

        ws2.__anext__ = AsyncMock(side_effect=anext2)

        with patch.object(
            websockets, "connect", AsyncMock(side_effect=[ws1, ws2])
        ):
            await conn.connect()
            with pytest.raises(BiDiConnectionError):
                await asyncio.wait_for(conn.send_command("x.y", {}), timeout=5)
        await conn.close()

    async def test_ws_close_error_suppressed_on_close(self) -> None:
        conn = Connection("ws://localhost:9999")
        ws = AsyncMock()
        ws.close = AsyncMock(side_effect=RuntimeError("boom"))
        conn._ws = ws
        await conn.close()  # must not raise


class TestNetworkValidation:
    async def test_continue_with_auth_credentials_wrong_action(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        conn = _mock_conn()
        net = NetworkModule(conn)
        with caplog.at_level(logging.WARNING, logger="bidiwave.network"):
            await net.continue_with_auth(
                "req-1", action="default", credentials={"type": "password"}
            )
        params = conn.send_command.call_args.args[1]
        assert "credentials" not in params
        assert "credentials ignored" in caplog.text

    async def test_continue_with_auth_credentials_ok(self) -> None:
        conn = _mock_conn()
        net = NetworkModule(conn)
        await net.continue_with_auth(
            "req-1",
            action="provideCredentials",
            credentials={"type": "password"},
        )
        params = conn.send_command.call_args.args[1]
        assert params["credentials"] == {"type": "password"}

    async def test_data_collector_mutually_exclusive_scopes(self) -> None:
        net = NetworkModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await net.add_data_collector(
                ["response"], 1024, contexts=["c"], user_contexts=["u"]
            )

    async def test_extra_headers_mutually_exclusive_scopes(self) -> None:
        net = NetworkModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await net.set_extra_headers(
                [{"name": "x", "value": "y"}],
                contexts=["c"],
                user_contexts=["u"],
            )


class TestSessionUnsubscribe:
    async def test_events_and_subscriptions_raises(self) -> None:
        session = SessionModule(_mock_conn())
        with pytest.raises(ValueError, match="cannot be combined"):
            await session.unsubscribe(events=["e"], subscriptions=["s"])

    async def test_contexts_and_subscriptions_raises(self) -> None:
        session = SessionModule(_mock_conn())
        with pytest.raises(ValueError, match="cannot be combined"):
            await session.unsubscribe(subscriptions=["s"], contexts=["c"])

    async def test_subscriptions_alone_ok(self) -> None:
        conn = _mock_conn()
        session = SessionModule(conn)
        await session.unsubscribe(subscriptions=["s1"])
        params = conn.send_command.call_args.args[1]
        assert params == {"subscriptions": ["s1"]}


class TestScriptTargetValidation:
    async def test_realm_and_sandbox_raises(self) -> None:
        script = ScriptModule(_mock_conn())
        with pytest.raises(ValueError, match="sandbox"):
            await script.evaluate("ctx", "1+1", realm="r", sandbox="s")

    async def test_preload_script_mutually_exclusive_scopes(self) -> None:
        script = ScriptModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await script.add_preload_script(
                "() => {}", contexts=["c"], user_contexts=["u"]
            )


class TestBrowsingValidation:
    async def test_screenshot_quality_range(self) -> None:
        browsing = BrowsingModule(_mock_conn())
        with pytest.raises(ValueError, match="quality"):
            await browsing.screenshot("ctx", format="jpeg", quality=-1)
        with pytest.raises(ValueError, match="quality"):
            await browsing.screenshot("ctx", format="jpeg", quality=101)

    async def test_print_scale_range(self) -> None:
        browsing = BrowsingModule(_mock_conn())
        with pytest.raises(ValueError, match="scale"):
            await browsing.print("ctx", scale=0.05)
        with pytest.raises(ValueError, match="scale"):
            await browsing.print("ctx", scale=3.0)

    async def test_viewport_mutually_exclusive_scopes(self) -> None:
        browsing = BrowsingModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await browsing.set_viewport(
                context="c", viewport={"width": 1, "height": 1},
                user_contexts=["u"],
            )
        with pytest.raises(ValueError, match="mutually exclusive"):
            await browsing.reset_viewport(context="c", user_contexts=["u"])

    async def test_wait_for_selector_malformed_result(self) -> None:
        conn = _mock_conn()
        conn.send_command.return_value = {
            "type": "success",
            "result": "not-a-dict",
        }
        browsing = BrowsingModule(conn)
        with pytest.raises(ProtocolError):
            await browsing.wait_for_selector("ctx", "#x", timeout=0.5)

    async def test_wait_for_function_malformed_result(self) -> None:
        conn = _mock_conn()
        conn.send_command.return_value = {
            "type": "success",
            "result": ["nope"],
        }
        browsing = BrowsingModule(conn)
        with pytest.raises(ProtocolError):
            await browsing.wait_for_function("ctx", "true", timeout=0.5)


class TestEmulationValidation:
    async def test_mutually_exclusive_scopes(self) -> None:
        emu = EmulationModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await emu.set_timezone("UTC", contexts=["c"], user_contexts=["u"])
        with pytest.raises(ValueError, match="mutually exclusive"):
            await emu.set_user_agent("ua", contexts=["c"], user_contexts=["u"])
        with pytest.raises(ValueError, match="mutually exclusive"):
            await emu.set_geolocation(
                coordinates={"latitude": 1.0, "longitude": 2.0},
                contexts=["c"],
                user_contexts=["u"],
            )


class TestPageClose:
    async def test_close_retryable_after_failure(self) -> None:
        from bidiwave.convenience.page import Page
        from bidiwave.modules.browsing import BrowsingContext

        browsing = MagicMock(spec=BrowsingModule)
        browsing.close = AsyncMock(side_effect=BiDiConnectionError("gone"))
        page = Page(browsing, None, BrowsingContext(id="ctx"))

        with pytest.raises(BiDiConnectionError):
            await page.close()
        assert page._closed is False

        browsing.close = AsyncMock()
        await page.close()
        assert page._closed is True


class TestSetFiles:
    async def test_dict_element_accepted(self) -> None:
        conn = _mock_conn()
        inp = InputModule(conn)
        ref = {"sharedId": "e1", "handle": "h1"}
        await inp.set_files("ctx", ref, ["/tmp/f.txt"])
        params = conn.send_command.call_args.args[1]
        assert params["element"] == ref

    async def test_str_element_wrapped(self) -> None:
        conn = _mock_conn()
        inp = InputModule(conn)
        await inp.set_files("ctx", "shared-1", ["/tmp/f.txt"])
        params = conn.send_command.call_args.args[1]
        assert params["element"] == {"sharedId": "shared-1"}


class TestSetupLogging:
    def test_user_handlers_not_reformatted(self) -> None:
        from bidiwave._internal.logging import setup_logging

        logger = logging.getLogger("bidiwave")
        user_handler = logging.StreamHandler()
        user_formatter = logging.Formatter("USER %(message)s")
        user_handler.setFormatter(user_formatter)
        logger.addHandler(user_handler)
        try:
            setup_logging("DEBUG", structured=True)
            assert user_handler.formatter is user_formatter
        finally:
            logger.removeHandler(user_handler)

    def test_int_level_accepted(self) -> None:
        from bidiwave._internal.logging import setup_logging

        logger = logging.getLogger("bidiwave")
        setup_logging(logging.DEBUG)  # type: ignore[arg-type]
        assert logger.level == logging.DEBUG


class TestClientConnect:
    async def test_connect_closes_socket_when_no_session(self) -> None:
        """If session.new AND session.status fail, the socket must be
        closed and the original error surfaced — not a broken client."""
        from bidiwave.client import BiDiClient
        from bidiwave.transport.connection import Connection

        conn = MagicMock(spec=Connection)
        conn._dispatcher = MagicMock()
        conn.connect = AsyncMock()
        conn.close = AsyncMock()
        conn.send_command = AsyncMock(
            side_effect=BiDiConnectionError("dead")
        )
        with (
            patch("bidiwave.client.Connection", return_value=conn),
            pytest.raises(BiDiConnectionError, match="dead"),
        ):
            await BiDiClient.connect("ws://localhost:9999")
        conn.close.assert_awaited_once()

    async def test_connect_survives_session_new_rejection(self) -> None:
        """session.status fallback keeps the client when new is rejected."""
        from bidiwave.client import BiDiClient
        from bidiwave.exceptions import CommandError
        from bidiwave.transport.connection import Connection

        conn = MagicMock(spec=Connection)
        conn._dispatcher = MagicMock()
        conn.connect = AsyncMock()
        conn.close = AsyncMock()
        conn.send_command = AsyncMock(
            side_effect=[
                CommandError("unsupported operation", "no new"),
                {"ready": True, "message": "ok"},
            ]
        )
        with patch("bidiwave.client.Connection", return_value=conn):
            client = await BiDiClient.connect("ws://localhost:9999")
        conn.close.assert_not_awaited()
        assert client.session is not None


class TestAutoPrompt:
    async def test_subscribe_failure_leaves_clean_state(self) -> None:
        from bidiwave.client import BiDiClient
        from bidiwave.exceptions import CommandError
        from bidiwave.transport.connection import Connection

        conn = MagicMock(spec=Connection)
        conn._dispatcher = MagicMock()
        conn.send_command = AsyncMock(
            side_effect=CommandError("unknown error", "sub failed")
        )
        client = BiDiClient(conn)
        with pytest.raises(CommandError):
            await client.set_auto_prompt(accept=True)
        assert client._auto_prompt_subscribed is False
        assert client._auto_prompt_accept is None
        assert client._auto_prompt_sub is None


class TestBrowsingOpen:
    async def test_close_failure_does_not_mask_nav_error(self) -> None:
        from bidiwave.exceptions import CommandError

        conn = _mock_conn()
        conn.send_command.side_effect = [
            {"context": "c1", "url": ""},
            CommandError("unknown error", "nav failed"),
            CommandError("unknown error", "close also failed"),
        ]
        browsing = BrowsingModule(conn)
        with pytest.raises(CommandError, match="nav failed"):
            await browsing.open("https://example.com")


class TestScopeMutualExclusionRemaining:
    async def test_subscribe_mutually_exclusive_scopes(self) -> None:
        session = SessionModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await session.subscribe(
                ["ev"], contexts=["c"], user_contexts=["u"]
            )

    async def test_preload_module_mutually_exclusive_scopes(self) -> None:
        from bidiwave.modules.preload import PreloadModule

        preload = PreloadModule(_mock_conn())
        with pytest.raises(ValueError, match="mutually exclusive"):
            await preload.add_script(
                "() => {}", contexts=["c"], user_contexts=["u"]
            )

    async def test_data_collector_zero_size_rejected(self) -> None:
        net = NetworkModule(_mock_conn())
        with pytest.raises(ValueError, match="max_encoded_data_size"):
            await net.add_data_collector(["request"], 0)
        with pytest.raises(ValueError, match="max_encoded_data_size"):
            await net.add_data_collector(["request"], -5)

    async def test_geolocation_altitude_accuracy_requires_altitude(
        self,
    ) -> None:
        emu = EmulationModule(_mock_conn())
        with pytest.raises(ValueError, match="altitude"):
            await emu.set_geolocation(
                coordinates={
                    "latitude": 1.0,
                    "longitude": 2.0,
                    "altitudeAccuracy": 3.0,
                }
            )


class TestSendCommandTimeout:
    async def test_timeout_clears_pending(self) -> None:
        conn = Connection(
            "ws://localhost:9999",
            config=TransportConfig(timeout=0.05),
        )
        conn._ws = AsyncMock()
        with pytest.raises(BiDiTimeoutError):
            await conn.send_command("x.y", {})
        assert conn._correlator._pending == {}


async def _hang(*args: object, **kwargs: object) -> None:
    await asyncio.sleep(30)


class TestTimeoutErrorConsistency:
    """BiDiTimeoutError must unify with builtin TimeoutError, and
    wait_for_* must raise it instead of a bare asyncio TimeoutError."""

    def test_bidi_timeout_is_builtin_timeout(self) -> None:
        assert issubclass(BiDiTimeoutError, TimeoutError)
        assert issubclass(BiDiTimeoutError, Exception)

    async def test_wait_for_selector_raises_bidi_timeout(self) -> None:
        conn = _mock_conn()
        conn.send_command = AsyncMock(side_effect=_hang)
        browsing = BrowsingModule(conn)
        with pytest.raises(BiDiTimeoutError):
            await browsing.wait_for_selector("ctx", "#x", timeout=0.05)

    async def test_wait_for_function_raises_bidi_timeout(self) -> None:
        conn = _mock_conn()
        conn.send_command = AsyncMock(side_effect=_hang)
        browsing = BrowsingModule(conn)
        with pytest.raises(BiDiTimeoutError):
            await browsing.wait_for_function("ctx", "false", timeout=0.05)

    async def test_bidi_timeout_catchable_as_builtin(self) -> None:
        conn = _mock_conn()
        conn.send_command = AsyncMock(side_effect=_hang)
        browsing = BrowsingModule(conn)
        with pytest.raises(TimeoutError):
            await browsing.wait_for_selector("ctx", "#x", timeout=0.05)


class TestSendFailureAndEventParams:
    """send_command must surface a BiDiConnectionError (not a raw websockets
    exception) when the socket send fails, and the receive loop must not
    forward non-dict event params to handlers."""

    async def test_send_failure_raises_bidi_connection_error(self) -> None:
        conn = Connection("ws://localhost:9999", config=TransportConfig())
        ws = AsyncMock()
        ws.send = AsyncMock(side_effect=RuntimeError("socket gone"))
        conn._ws = ws
        with pytest.raises(BiDiConnectionError):
            await conn.send_command("x.y", {})
        assert conn._correlator._pending == {}

    async def test_event_with_non_dict_params_becomes_empty(self) -> None:
        conn = Connection("ws://localhost:9999", config=TransportConfig())
        seen: list = []

        async def handler(evt: object) -> None:
            seen.append(evt)

        conn._dispatcher.on("log.entryAdded", handler)
        conn._ws = AsyncMock()

        async def fake_recv():
            yield json.dumps(
                {
                    "type": "event",
                    "method": "log.entryAdded",
                    "params": ["not", "a", "dict"],
                }
            )
            await asyncio.Event().wait()

        conn._ws.__aiter__ = lambda self: fake_recv()
        task = asyncio.create_task(conn._receive_loop())
        await asyncio.sleep(0.2)
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        if conn._background_tasks:
            await asyncio.gather(*conn._background_tasks, return_exceptions=True)
        assert seen
        assert all(isinstance(e, dict) for e in seen)


class TestSessionNewValidation:
    async def test_on_new_not_called_on_malformed_result(self) -> None:
        from bidiwave.modules.session import SessionModule

        conn = _mock_conn()
        conn.send_command = AsyncMock(return_value={"not": "a session"})
        sm = SessionModule(conn)
        called: list = []
        sm.on_new = lambda result: called.append(result)
        with pytest.raises(ValidationError):
            await sm.new()
        assert called == []
