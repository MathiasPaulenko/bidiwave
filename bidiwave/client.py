"""BiDiClient — API pública de bidiwave."""

from __future__ import annotations

from typing import Any

from bidiwave.config import ClientConfig
from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.cdp import CDPModule
from bidiwave.modules.input import InputModule
from bidiwave.modules.network import NetworkModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.session import SessionModule
from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.capabilities import Capabilities
from bidiwave.transport.connection import Connection, TransportConfig


class BiDiClient:
    """Cliente WebDriver BiDi.

    Ejemplo:
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
        self._capabilities: Capabilities | None = None
        self._auto_prompt_accept: bool | None = None
        self._auto_prompt_text: str | None = None
        self._auto_prompt_sub: Subscription | None = None

    @classmethod
    async def connect(
        cls,
        url: str,
        config: ClientConfig | None = None,
    ) -> BiDiClient:
        cfg = config or ClientConfig()
        transport_config = TransportConfig(
            timeout=cfg.timeout,
            max_retries=cfg.max_retries,
            retry_delay=cfg.retry_delay,
            retry_backoff=cfg.retry_backoff,
            max_queue=cfg.max_queue,
            drop_policy=cfg.drop_policy,
        )
        connection = Connection(url, config=transport_config)
        await connection.connect()
        return cls(connection)

    @property
    def capabilities(self) -> Capabilities | None:
        return self._capabilities

    def on(self, event_type: str, handler: AsyncHandler) -> Subscription:
        """Registra un handler para un event type."""
        return self._dispatcher.on(event_type, handler)  # type: ignore[return-value]

    def off(self, subscription: Subscription) -> None:
        """Desuscribe un handler."""
        self._dispatcher.off(subscription)

    async def on_log_entry(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para suscribirse a console logs."""
        return self._dispatcher.on("log.entryAdded", handler)  # type: ignore[return-value]

    def on_context_created(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para browsingContext.contextCreated."""
        return self._dispatcher.on("browsingContext.contextCreated", handler)  # type: ignore[return-value]

    def on_context_destroyed(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para browsingContext.contextDestroyed."""
        return self._dispatcher.on("browsingContext.contextDestroyed", handler)  # type: ignore[return-value]

    def on_request(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para network.beforeRequestSent."""
        return self._dispatcher.on("network.beforeRequestSent", handler)  # type: ignore[return-value]

    def on_response(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para network.responseCompleted."""
        return self._dispatcher.on("network.responseCompleted", handler)  # type: ignore[return-value]

    def on_fetch_error(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para network.fetchError."""
        return self._dispatcher.on("network.fetchError", handler)  # type: ignore[return-value]

    def on_cookie_changed(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para storage.cookieChanged."""
        return self._dispatcher.on("storage.cookieChanged", handler)  # type: ignore[return-value]

    def on_auth_required(self, handler: AsyncHandler) -> Subscription:
        """Conveniencia para network.authRequired."""
        return self._dispatcher.on("network.authRequired", handler)  # type: ignore[return-value]

    async def set_auto_prompt(
        self,
        accept: bool = True,
        user_text: str | None = None,
    ) -> None:
        """Habilita el manejo automático de dialogs (alert/confirm/prompt).

        Suscribe a browsingContext.userPromptOpened y maneja cada dialog
        automáticamente con los parámetros indicados.

        Args:
            accept: True para aceptar, False para dismiss.
            user_text: Texto para prompts (opcional).
        """
        self._auto_prompt_accept = accept
        self._auto_prompt_text = user_text

        if self._auto_prompt_sub is not None:
            self.off(self._auto_prompt_sub)

        async def _handle_prompt(event: dict[str, Any]) -> None:
            ctx_id = event.get("context")
            if ctx_id is not None:
                await self.browsing.handle_user_prompt(
                    ctx_id,
                    accept=self._auto_prompt_accept,
                    user_text=self._auto_prompt_text,
                )

        self._auto_prompt_sub = self.on(
            "browsingContext.userPromptOpened", _handle_prompt
        )
        await self.session.subscribe(["browsingContext.userPromptOpened"])

    async def disable_auto_prompt(self) -> None:
        """Desactiva el manejo automático de dialogs."""
        if self._auto_prompt_sub is not None:
            self.off(self._auto_prompt_sub)
            self._auto_prompt_sub = None
        self._auto_prompt_accept = None
        self._auto_prompt_text = None

    def on_reconnect(self, handler: AsyncHandler) -> None:
        """Registra un handler que se ejecuta tras reconectar."""
        self._connection.on_reconnect(handler)

    def on_disconnect(self, handler: AsyncHandler) -> None:
        """Registra un handler que se ejecuta al desconectar."""
        self._connection.on_disconnect(handler)

    async def close(self) -> None:
        await self._connection.close()

    async def __aenter__(self) -> BiDiClient:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        await self.close()