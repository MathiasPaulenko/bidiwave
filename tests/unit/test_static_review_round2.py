"""Regression tests for Phase 2 static review round 2 fixes."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.client import BiDiClient
from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.transport.connection import Connection, TransportConfig

# ---------------------------------------------------------------------------
# Bug: set_auto_prompt handler used .get() on Pydantic model events
# ---------------------------------------------------------------------------


class TestAutoPromptHandlerPydanticEvent:
    """The _handle_prompt callback must work with parsed Pydantic event models,
    not just plain dicts."""

    @pytest.mark.asyncio
    async def test_handle_prompt_with_pydantic_model(self) -> None:
        from bidiwave.protocol.events import BrowsingContextUserPromptOpenedEvent

        conn = MagicMock()
        conn._dispatcher = EventDispatcher()
        conn.on_reconnect = MagicMock()
        conn.on_disconnect = MagicMock()
        client = BiDiClient(conn)
        client._connection.send_command = AsyncMock(return_value={})

        await client.set_auto_prompt(accept=True, user_text="ok")
        assert client._auto_prompt_subscribed

        event = BrowsingContextUserPromptOpenedEvent.model_validate(
            {"context": "ctx-1", "type": "alert", "message": "hello"}
        )

        handlers = client._dispatcher._handlers.get(
            "browsingContext.userPromptOpened", []
        )
        assert len(handlers) == 1
        await handlers[0](event)

        # Two calls: session.subscribe + handleUserPrompt
        assert client._connection.send_command.call_count == 2
        call_args = client._connection.send_command.call_args
        assert call_args.args[0] == "browsingContext.handleUserPrompt"
        assert call_args.args[1]["context"] == "ctx-1"
        assert call_args.args[1]["accept"] is True
        assert call_args.args[1]["userText"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_prompt_with_dict_event(self) -> None:
        """Should also still work with plain dict events (fallback case)."""
        conn = MagicMock()
        conn._dispatcher = EventDispatcher()
        conn.on_reconnect = MagicMock()
        conn.on_disconnect = MagicMock()
        client = BiDiClient(conn)
        client._connection.send_command = AsyncMock(return_value={})

        await client.set_auto_prompt(accept=False)

        handlers = client._dispatcher._handlers.get(
            "browsingContext.userPromptOpened", []
        )
        await handlers[0]({"context": "ctx-2"})

        call_args = client._connection.send_command.call_args
        assert call_args.args[0] == "browsingContext.handleUserPrompt"
        assert call_args.args[1]["context"] == "ctx-2"
        assert call_args.args[1]["accept"] is False


# ---------------------------------------------------------------------------
# Bug: send_command leaked correlator futures on cancellation
# ---------------------------------------------------------------------------


class TestSendCommandCancellationCleansCorrelator:
    """When send_command is cancelled, the pending future must be rejected
    so it doesn't leak in the correlator's _pending dict."""

    @pytest.mark.asyncio
    async def test_cancelled_command_rejects_future(self) -> None:
        from bidiwave.transport.correlation import Correlator

        correlator = Correlator()
        config = TransportConfig(timeout=10.0)
        conn = Connection("ws://fake", config=config, correlator=correlator)
        conn._ws = MagicMock()
        conn._ws.send = AsyncMock()

        send_task = asyncio.create_task(
            conn.send_command("test.method", {})
        )
        await asyncio.sleep(0.05)
        send_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await send_task

        assert len(correlator._pending) == 0


# ---------------------------------------------------------------------------
# Bug: BiDiClient.close() didn't clean up auto-prompt subscription
# ---------------------------------------------------------------------------


class TestCloseCleansAutoPrompt:
    """close() should unsubscribe auto-prompt handler and unsubscribe
    from the event."""

    @pytest.mark.asyncio
    async def test_close_disables_auto_prompt(self) -> None:
        conn = MagicMock()
        conn._dispatcher = EventDispatcher()
        conn.on_reconnect = MagicMock()
        conn.on_disconnect = MagicMock()
        conn.close = AsyncMock()
        conn.send_command = AsyncMock(return_value={})

        client = BiDiClient(conn)
        await client.set_auto_prompt(accept=True)

        assert client._auto_prompt_subscribed
        assert client._auto_prompt_sub is not None

        await client.close()

        assert client._auto_prompt_sub is None
        assert not client._auto_prompt_subscribed

    @pytest.mark.asyncio
    async def test_close_without_auto_prompt_is_safe(self) -> None:
        conn = MagicMock()
        conn._dispatcher = EventDispatcher()
        conn.on_reconnect = MagicMock()
        conn.on_disconnect = MagicMock()
        conn.close = AsyncMock()
        conn.send_command = AsyncMock(return_value={})

        client = BiDiClient(conn)
        await client.close()
        assert client._auto_prompt_sub is None


# ---------------------------------------------------------------------------
# Bug: BrowsingModule and LogEntryAddedEvent missing from __init__ exports
# ---------------------------------------------------------------------------


class TestMissingExports:
    """BrowsingModule and LogEntryAddedEvent should be exported from
    the bidiwave package."""

    def test_browsing_module_exported(self) -> None:
        import bidiwave

        assert hasattr(bidiwave, "BrowsingModule")
        assert "BrowsingModule" in bidiwave.__all__

    def test_log_entry_added_event_exported(self) -> None:
        import bidiwave

        assert hasattr(bidiwave, "LogEntryAddedEvent")
        assert "LogEntryAddedEvent" in bidiwave.__all__
