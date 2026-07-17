"""BiDiClient — public API for bidiwave."""

from __future__ import annotations

import logging
from typing import Any

from bidiwave._internal.logging import setup_logging
from bidiwave.config import ClientConfig
from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.cdp import CDPModule
from bidiwave.modules.emulation import EmulationModule
from bidiwave.modules.input import InputModule
from bidiwave.modules.log import LogModule
from bidiwave.modules.network import NetworkModule
from bidiwave.modules.permissions import PermissionsModule
from bidiwave.modules.preload import PreloadModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.session import SessionModule
from bidiwave.modules.storage import StorageModule
from bidiwave.modules.webextension import WebExtensionModule
from bidiwave.protocol.capabilities import Capabilities, detect_capabilities
from bidiwave.transport.connection import Connection, TransportConfig

logger = logging.getLogger("bidiwave.client")


class BiDiClient:
    """WebDriver BiDi client.

    Example:
        async with await BiDiClient.connect("ws://localhost:9222/session") as client:
            await client.session.new()
            async with await client.browsing.create_context() as ctx:
                await client.browsing.navigate(ctx, "https://example.com")
                result = await client.script.evaluate(ctx, "document.title")
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self._dispatcher: EventDispatcher = connection._dispatcher
        self.session = SessionModule(connection)
        self.script = ScriptModule(connection)
        self.browsing = BrowsingModule(connection, script_module=self.script)
        self.network = NetworkModule(connection)
        self.input = InputModule(connection)
        self.storage = StorageModule(connection)
        self.cdp = CDPModule(connection)
        self.preload = PreloadModule(connection)
        self.emulation = EmulationModule(connection)
        self.permissions = PermissionsModule(connection)
        self.log = LogModule(connection)
        self.web_extension = WebExtensionModule(connection)
        self._capabilities: Capabilities | None = None
        self._auto_prompt_accept: bool | None = None
        self._auto_prompt_text: str | None = None
        self._auto_prompt_sub: Subscription | None = None
        self._auto_prompt_subscribed: bool = False

    @classmethod
    async def connect(
        cls,
        url: str,
        config: ClientConfig | None = None,
    ) -> BiDiClient:
        cfg = config or ClientConfig()
        setup_logging(level=cfg.log_level)
        transport_config = TransportConfig(
            timeout=cfg.timeout,
            max_retries=cfg.max_retries,
            retry_delay=cfg.retry_delay,
            retry_backoff=cfg.retry_backoff,
        )
        connection = Connection(url, config=transport_config)
        await connection.connect()
        client = cls(connection)
        try:
            status = await client.session.status()
            client._capabilities = detect_capabilities(
                status.model_dump()
            )
        except Exception as e:
            logger.warning("Failed to detect capabilities: %s", e)
        return client

    @property
    def capabilities(self) -> Capabilities | None:
        return self._capabilities

    def on(self, event_type: str, handler: AsyncHandler) -> Subscription:
        """Registers a handler for an event type."""
        return self._dispatcher.on(event_type, handler)

    def off(self, subscription: Subscription) -> None:
        """Unsubscribes a handler."""
        self._dispatcher.off(subscription)

    def on_log_entry(self, handler: AsyncHandler) -> Subscription:
        """Convenience for subscribing to console logs."""
        return self._dispatcher.on("log.entryAdded", handler)

    def on_context_created(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.contextCreated."""
        return self._dispatcher.on("browsingContext.contextCreated", handler)

    def on_context_destroyed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.contextDestroyed."""
        return self._dispatcher.on("browsingContext.contextDestroyed", handler)

    def on_request(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.beforeRequestSent."""
        return self._dispatcher.on("network.beforeRequestSent", handler)

    def on_response(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.responseCompleted."""
        return self._dispatcher.on("network.responseCompleted", handler)

    def on_fetch_error(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.fetchError."""
        return self._dispatcher.on("network.fetchError", handler)

    def on_auth_required(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.authRequired."""
        return self._dispatcher.on("network.authRequired", handler)

    def on_response_started(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.responseStarted."""
        return self._dispatcher.on("network.responseStarted", handler)

    def on_data_received(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.dataReceived."""
        return self._dispatcher.on("network.dataReceived", handler)

    def on_navigation_completed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.navigationCompleted."""
        return self._dispatcher.on("browsingContext.navigationCompleted", handler)

    def on_fragment_navigated(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.fragmentNavigated."""
        return self._dispatcher.on("browsingContext.fragmentNavigated", handler)

    def on_load(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.load."""
        return self._dispatcher.on("browsingContext.load", handler)

    def on_dom_content_loaded(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.domContentLoaded."""
        return self._dispatcher.on("browsingContext.domContentLoaded", handler)

    def on_history_updated(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.historyUpdated."""
        return self._dispatcher.on("browsingContext.historyUpdated", handler)

    def on_sampling_state_changed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for network.samplingStateChanged."""
        return self._dispatcher.on("network.samplingStateChanged", handler)

    def on_realm_created(self, handler: AsyncHandler) -> Subscription:
        """Convenience for script.realmCreated."""
        return self._dispatcher.on("script.realmCreated", handler)

    def on_realm_destroyed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for script.realmDestroyed."""
        return self._dispatcher.on("script.realmDestroyed", handler)

    def on_user_prompt_opened(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.userPromptOpened."""
        return self._dispatcher.on("browsingContext.userPromptOpened", handler)

    def on_user_prompt_closed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.userPromptClosed."""
        return self._dispatcher.on("browsingContext.userPromptClosed", handler)

    def on_navigation_started(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.navigationStarted."""
        return self._dispatcher.on("browsingContext.navigationStarted", handler)

    def on_navigation_aborted(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.navigationAborted."""
        return self._dispatcher.on("browsingContext.navigationAborted", handler)

    def on_navigation_committed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.navigationCommitted."""
        return self._dispatcher.on("browsingContext.navigationCommitted", handler)

    def on_navigation_failed(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.navigationFailed."""
        return self._dispatcher.on("browsingContext.navigationFailed", handler)

    def on_script_message(self, handler: AsyncHandler) -> Subscription:
        """Convenience for script.message."""
        return self._dispatcher.on("script.message", handler)

    def on_download_will_begin(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.downloadWillBegin."""
        return self._dispatcher.on("browsingContext.downloadWillBegin", handler)

    def on_download_end(self, handler: AsyncHandler) -> Subscription:
        """Convenience for browsingContext.downloadEnd."""
        return self._dispatcher.on("browsingContext.downloadEnd", handler)

    def on_file_dialog_opened(self, handler: AsyncHandler) -> Subscription:
        """Convenience for input.fileDialogOpened."""
        return self._dispatcher.on("input.fileDialogOpened", handler)

    async def set_auto_prompt(
        self,
        accept: bool = True,
        user_text: str | None = None,
    ) -> None:
        """Enables automatic dialog handling (alert/confirm/prompt).

        Subscribes to browsingContext.userPromptOpened and handles each dialog
        automatically with the given parameters.

        Args:
            accept: True to accept, False to dismiss.
            user_text: Text for prompts (optional).
        """
        self._auto_prompt_accept = accept
        self._auto_prompt_text = user_text

        if self._auto_prompt_sub is not None:
            self.off(self._auto_prompt_sub)

        async def _handle_prompt(event: Any) -> None:
            if isinstance(event, dict):
                ctx_id = event.get("context")
            else:
                ctx_id = getattr(event, "context", None)
            if ctx_id is not None:
                await self.browsing.handle_user_prompt(
                    ctx_id,
                    accept=self._auto_prompt_accept,
                    user_text=self._auto_prompt_text,
                )

        if not self._auto_prompt_subscribed:
            await self.session.subscribe(["browsingContext.userPromptOpened"])
            self._auto_prompt_subscribed = True
        self._auto_prompt_sub = self.on("browsingContext.userPromptOpened", _handle_prompt)

    async def disable_auto_prompt(self) -> None:
        """Disables automatic dialog handling."""
        sub = getattr(self, "_auto_prompt_sub", None)
        if sub is not None:
            self.off(sub)
            self._auto_prompt_sub = None
        self._auto_prompt_accept = None
        self._auto_prompt_text = None
        if getattr(self, "_auto_prompt_subscribed", False):
            try:
                await self.session.unsubscribe(["browsingContext.userPromptOpened"])
            except Exception as e:
                logger.warning("Error unsubscribing from auto prompt: %s", e)
            self._auto_prompt_subscribed = False

    def on_reconnect(self, handler: AsyncHandler) -> None:
        """Registers a handler that runs after reconnection."""
        self._connection.on_reconnect(handler)

    def on_disconnect(self, handler: AsyncHandler) -> None:
        """Registers a handler that runs on disconnection."""
        self._connection.on_disconnect(handler)

    async def close(self) -> None:
        if getattr(self, "_auto_prompt_sub", None) is not None:
            await self.disable_auto_prompt()
        try:
            await self.session.end()
        except Exception as e:
            logger.warning("Error ending session during close: %s", e)
        await self._connection.close()

    async def __aenter__(self) -> BiDiClient:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        await self.close()
