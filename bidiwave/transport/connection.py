"""WebSocket connection to the browser's BiDi endpoint."""

import asyncio
import logging
from typing import Any, Literal

import websockets
from pydantic import BaseModel
from websockets.asyncio.client import ClientConnection

from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler
from bidiwave.exceptions import ConnectionError as BiDiConnectionError
from bidiwave.exceptions import map_error
from bidiwave.transport.correlation import Correlator
from bidiwave.transport.serializer import deserialize_message, serialize_command

logger = logging.getLogger("bidiwave.transport")


class TransportConfig(BaseModel):
    """Transport configuration."""

    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    max_queue: int = 1000
    drop_policy: Literal["oldest", "newest", "block"] = "oldest"


class Connection:
    """WebSocket connection to the browser's BiDi endpoint."""

    def __init__(
        self,
        url: str,
        config: TransportConfig | None = None,
        correlator: Correlator | None = None,
        dispatcher: EventDispatcher | None = None,
    ) -> None:
        self._url = url
        self._config = config or TransportConfig()
        self._correlator = correlator or Correlator()
        self._dispatcher = dispatcher or EventDispatcher()
        self._ws: ClientConnection | None = None
        self._receive_task: asyncio.Task[None] | None = None
        self._closed = False
        self._reconnecting = False
        self._on_reconnect: list[AsyncHandler] = []
        self._on_disconnect: list[AsyncHandler] = []

    async def connect(self) -> None:
        self._ws = await websockets.connect(self._url)
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info("Connected to %s", self._url)

    async def send_command(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._ws is None or self._closed:
            raise BiDiConnectionError("Connection is closed")

        command_id = self._correlator.next_id()
        future = self._correlator.register(command_id)

        message = serialize_command(command_id, method, params)
        await self._ws.send(message)
        logger.debug("→ [%d] %s", command_id, method)

        return await asyncio.wait_for(future, timeout=self._config.timeout)

    async def _reconnect(self) -> bool:
        """Attempts to reconnect with exponential backoff. Returns True on success."""
        self._reconnecting = True
        delay = self._config.retry_delay

        for attempt in range(self._config.max_retries):
            logger.info(
                "Reconnect attempt %d/%d (delay=%.1fs)",
                attempt + 1,
                self._config.max_retries,
                delay,
            )
            await asyncio.sleep(delay)

            try:
                self._ws = await websockets.connect(self._url)
                self._receive_task = asyncio.create_task(self._receive_loop())
                logger.info("Reconnected successfully")

                for handler in self._on_reconnect:
                    try:
                        await handler(None)
                    except Exception as e:
                        logger.error("Reconnect handler error: %s", e)

                self._reconnecting = False
                return True
            except Exception as e:
                logger.warning("Reconnect failed: %s", e)
                delay *= self._config.retry_backoff

        self._reconnecting = False
        return False

    async def _receive_loop(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                data = deserialize_message(str(raw))
                msg_type = data.get("type")

                if msg_type in ("success", "error"):
                    command_id = data.get("id")
                    if command_id is None:
                        logger.warning("Response without id: %s", data)
                        continue

                    if msg_type == "success":
                        self._correlator.resolve(command_id, data.get("result", {}))
                        logger.debug("← [%d] success", command_id)
                    else:
                        error_data = data.get("error", {})
                        if isinstance(error_data, str):
                            error_data = {"code": "unknown", "message": error_data}
                        error = map_error(
                            error_data.get("code", "unknown"),
                            error_data.get("message", "Unknown error"),
                        )
                        self._correlator.reject(command_id, error)
                        logger.debug("← [%d] error: %s", command_id, error_data.get("message"))
                else:
                    method = data.get("method", "unknown")
                    params = data.get("params", {})
                    logger.debug("← event: %s", method)
                    await self._dispatcher.dispatch(method, params)
        except websockets.ConnectionClosed:
            logger.info("WebSocket closed")
            if not self._closed:
                for handler in self._on_disconnect:
                    try:
                        await handler(None)
                    except Exception as e:
                        logger.error("Disconnect handler error: %s", e)

                await self._reconnect()
        finally:
            if not self._reconnecting:
                self._correlator.reject_all(BiDiConnectionError("Connection closed"))

    def on_reconnect(self, handler: AsyncHandler) -> None:
        self._on_reconnect.append(handler)

    def on_disconnect(self, handler: AsyncHandler) -> None:
        self._on_disconnect.append(handler)

    async def close(self) -> None:
        self._closed = True
        if self._receive_task:
            self._receive_task.cancel()
        if self._ws:
            await self._ws.close()
        logger.info("Connection closed")