"""WebSocket connection to the browser's BiDi endpoint."""

import asyncio
import contextlib
import logging
from typing import Any

import websockets
from pydantic import BaseModel, Field
from websockets.asyncio.client import ClientConnection

from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler
from bidiwave.exceptions import (
    BiDiConnectionError,
    BiDiTimeoutError,
    ProtocolError,
    map_error,
)
from bidiwave.transport.correlation import Correlator
from bidiwave.transport.serializer import deserialize_message, serialize_command

logger = logging.getLogger("bidiwave.transport")


class TransportConfig(BaseModel):
    """Transport configuration."""

    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=1.0, ge=0)
    retry_backoff: float = Field(default=2.0, ge=0)


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
        self._background_tasks: set[asyncio.Task[Any]] = set()

    async def connect(self) -> None:
        if self._ws is not None and not self._closed:
            raise BiDiConnectionError("Connection is already established")
        self._closed = False
        try:
            self._ws = await asyncio.wait_for(
                websockets.connect(self._url),
                timeout=self._config.timeout,
            )
        except TimeoutError as e:
            raise BiDiTimeoutError(
                f"Connection to {self._url} timed out after {self._config.timeout}s"
            ) from e
        except BiDiConnectionError:
            raise
        except Exception as e:
            raise BiDiConnectionError(
                f"Failed to connect to {self._url}: {e}"
            ) from e
        self._receive_task = asyncio.create_task(self._receive_loop())
        logger.info("Connected to %s", self._url)

    async def send_command(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._ws is None or self._closed:
            raise BiDiConnectionError("Connection is closed")
        if self._reconnecting:
            raise BiDiConnectionError("Connection is reconnecting")
        if not isinstance(params, dict):
            raise TypeError(
                f"params must be a dict, got {type(params).__name__}"
            )

        command_id = self._correlator.next_id()
        # Serialize before registering the future: if params aren't
        # JSON-encodable the caller gets TypeError immediately without
        # leaking a pending entry that would hang until close().
        message = serialize_command(command_id, method, params)
        future = self._correlator.register(command_id)

        try:
            await self._ws.send(message)
        except Exception as e:
            self._correlator.reject(command_id, BiDiConnectionError("Failed to send command"))
            raise BiDiConnectionError(f"Failed to send {method}: {e}") from e
        logger.debug("→ [%d] %s", command_id, method)

        try:
            return await asyncio.wait_for(future, timeout=self._config.timeout)
        except TimeoutError:
            self._correlator.reject(command_id, BiDiConnectionError("Command timed out"))
            raise BiDiTimeoutError(
                f"Command {method} timed out after {self._config.timeout}s"
            ) from None
        except asyncio.CancelledError:
            self._correlator.reject(command_id, BiDiConnectionError("Command cancelled"))
            raise

    async def _reconnect(self) -> bool:
        """Attempts to reconnect with exponential backoff. Returns True on success."""
        self._reconnecting = True
        delay = self._config.retry_delay

        try:
            for attempt in range(self._config.max_retries):
                if self._closed:
                    return False
                logger.info(
                    "Reconnect attempt %d/%d (delay=%.1fs)",
                    attempt + 1,
                    self._config.max_retries,
                    delay,
                )
                await asyncio.sleep(delay)

                try:
                    ws = await asyncio.wait_for(
                        websockets.connect(self._url),
                        timeout=self._config.timeout,
                    )
                except Exception as e:
                    logger.warning("Reconnect failed: %s", e)
                    delay *= self._config.retry_backoff
                    continue
                if self._closed:
                    await ws.close()
                    return False
                self._ws = ws
                self._receive_task = asyncio.create_task(self._receive_loop())
                logger.info("Reconnected successfully")

                for handler in self._on_reconnect:
                    try:
                        await handler({})
                    except Exception as e:
                        logger.error("Reconnect handler error: %s", e)

                return True
            return False
        finally:
            self._reconnecting = False

    async def _receive_loop(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                try:
                    raw_str = raw.decode() if isinstance(raw, bytes) else raw
                    data = deserialize_message(raw_str)
                except (ValueError, TypeError, RecursionError) as e:
                    logger.warning("Malformed message from browser: %s", e)
                    continue
                if not isinstance(data, dict):
                    logger.warning("Non-object message from browser: %r", data)
                    continue
                msg_type = data.get("type")

                if msg_type in ("success", "error"):
                    command_id = data.get("id")
                    if command_id is None:
                        # Per spec, protocol-level errors can carry id: null
                        # when the remote end can't correlate the command.
                        logger.warning("Response without id: %s", data)
                        continue

                    if msg_type == "success":
                        result = data.get("result", {})
                        if not isinstance(result, dict):
                            self._correlator.reject(
                                command_id,
                                ProtocolError(
                                    f"Malformed result for command {command_id}: "
                                    f"expected object, got {type(result).__name__}"
                                ),
                            )
                            continue
                        if not self._correlator.resolve(command_id, result):
                            logger.warning(
                                "Response for unknown command id: %r", command_id
                            )
                        else:
                            logger.debug("← [%d] success", command_id)
                    else:
                        # Per W3C BiDi, `error` is the ErrorCode string and
                        # `message` is a sibling text field.
                        code = data.get("error", "unknown")
                        message = data.get("message", "Unknown error")
                        if not isinstance(code, str):
                            code = "unknown"
                        if not isinstance(message, str):
                            message = "Unknown error"
                        error = map_error(code, message)
                        if not self._correlator.reject(command_id, error):
                            logger.warning(
                                "Error response for unknown command id: %r",
                                command_id,
                            )
                        else:
                            logger.debug("← [%d] error: %s", command_id, message)
                else:
                    method = data.get("method", "unknown")
                    if not isinstance(method, str):
                        method = "unknown"
                    params = data.get("params", {})
                    if not isinstance(params, dict):
                        params = {}
                    logger.debug("← event: %s", method)
                    task = asyncio.create_task(self._dispatcher.dispatch(method, params))
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
        except websockets.ConnectionClosed:
            logger.info("WebSocket closed")
            if not self._closed:
                for handler in self._on_disconnect:
                    try:
                        await handler({})
                    except Exception as e:
                        logger.error("Disconnect handler error: %s", e)

                await self._reconnect()
        except Exception as e:
            logger.error("Receive loop crashed: %s: %s", type(e).__name__, e, exc_info=True)
            if not self._closed:
                await self._reconnect()
        finally:
            # Responses to in-flight commands are lost with the old socket
            # even when a reconnect succeeds — fail them fast instead of
            # leaving callers hanging until their timeout expires.
            self._correlator.reject_all(BiDiConnectionError("Connection closed"))

    def on_reconnect(self, handler: AsyncHandler) -> None:
        self._on_reconnect.append(handler)

    def on_disconnect(self, handler: AsyncHandler) -> None:
        self._on_disconnect.append(handler)

    async def close(self) -> None:
        self._closed = True
        if self._receive_task:
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task
        self._correlator.reject_all(BiDiConnectionError("Connection closed"))
        for task in self._background_tasks:
            task.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()
        if self._ws:
            with contextlib.suppress(Exception):
                await self._ws.close()
        logger.info("Connection closed")