"""BiDiClient — API pública de bidiwave."""

from __future__ import annotations

from bidiwave.config import ClientConfig
from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.modules.browsing import BrowsingModule
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
        self._capabilities: Capabilities | None = None

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