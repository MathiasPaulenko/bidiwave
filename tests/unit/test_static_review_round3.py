"""Regression tests for Phase 2 static review round 3 fixes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.exceptions import BiDiConnectionError
from bidiwave.transport.connection import Connection, TransportConfig
from bidiwave.transport.correlation import Correlator

# ---------------------------------------------------------------------------
# Bug: Connection.connect() didn't guard against double-connect
# ---------------------------------------------------------------------------


class TestConnectDoubleGuard:
    """connect() must raise if already connected and not closed."""

    @pytest.mark.asyncio
    async def test_double_connect_raises(self) -> None:
        correlator = Correlator()
        conn = Connection("ws://fake", correlator=correlator)
        conn._ws = MagicMock()
        conn._closed = False

        with pytest.raises(BiDiConnectionError, match="already established"):
            await conn.connect()

    @pytest.mark.asyncio
    async def test_connect_after_close_resets_closed_flag(self) -> None:
        """After close(), _closed is True; connect() should reset it."""
        correlator = Correlator()
        conn = Connection("ws://fake", correlator=correlator)
        conn._ws = MagicMock()
        conn._closed = True

        # Should not raise — closed connections can be reconnected
        # We mock websockets.connect to avoid real network calls
        import bidiwave.transport.connection as conn_mod

        original_connect = conn_mod.websockets.connect
        conn_mod.websockets.connect = AsyncMock(return_value=MagicMock())
        try:
            await conn.connect()
            assert conn._closed is False
        finally:
            conn_mod.websockets.connect = original_connect


# ---------------------------------------------------------------------------
# Bug: Connection.close() didn't explicitly reject_all pending futures
# ---------------------------------------------------------------------------


class TestCloseRejectsAllPending:
    """close() must reject all pending correlator futures even if the
    receive loop's finally block didn't run."""

    @pytest.mark.asyncio
    async def test_close_rejects_pending(self) -> None:
        correlator = Correlator()
        config = TransportConfig(timeout=10.0)
        conn = Connection("ws://fake", config=config, correlator=correlator)

        # Register a pending future manually
        fut = correlator.register(42)
        assert len(correlator._pending) == 1

        # Close without a receive task — finally block won't run
        conn._ws = MagicMock()
        conn._ws.close = AsyncMock()

        await conn.close()

        assert len(correlator._pending) == 0
        assert fut.done()
        with pytest.raises(BiDiConnectionError, match="Connection closed"):
            fut.result()


# ---------------------------------------------------------------------------
# Bug: InstallResult was dead code duplicating WebExtensionInfo
# ---------------------------------------------------------------------------


class TestInstallResultRemoved:
    """InstallResult should no longer exist in webextension module."""

    def test_install_result_not_importable(self) -> None:
        from bidiwave.modules import webextension

        assert not hasattr(webextension, "InstallResult")


# ---------------------------------------------------------------------------
# Bug: Missing public type exports in __init__.py
# ---------------------------------------------------------------------------


class TestMissingExportsRound3:
    """Public types returned by module methods should be exported."""

    @pytest.mark.parametrize(
        "name",
        [
            "BrowsingContextInfo",
            "ClientWindowInfo",
            "GetCookiesResult",
            "GetRealmsResult",
            "GetTreeResult",
            "GetUserContextsResult",
            "InterceptResult",
            "Navigation",
            "PrintResult",
            "Screenshot",
            "Session",
            "SessionStatus",
            "WebExtensionInfo",
        ],
    )
    def test_type_exported(self, name: str) -> None:
        import bidiwave

        assert hasattr(bidiwave, name), f"{name} should be exported from bidiwave"
        assert name in bidiwave.__all__, f"{name} should be in __all__"
