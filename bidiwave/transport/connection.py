"""Conexión WebSocket al endpoint BiDi del browser."""

import asyncio
import logging
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from bidiwave.exceptions import CommandError
from bidiwave.exceptions import ConnectionError as BiDiConnectionError
from bidiwave.transport.correlation import Correlator
from bidiwave.transport.serializer import deserialize_message, serialize_command

logger = logging.getLogger("bidiwave.transport")


class Connection:
    """Conexión WebSocket al endpoint BiDi del browser."""

    def __init__(
        self,
        url: str,
        correlator: Correlator | None = None,
    ) -> None:
        self._url = url
        self._correlator = correlator or Correlator()
        self._ws: ClientConnection | None = None
        self._receive_task: asyncio.Task[None] | None = None
        self._closed = False

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

        return await asyncio.wait_for(future, timeout=30.0)

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
                        self._correlator.reject(
                            command_id,
                            CommandError(
                                code=error_data.get("code", "unknown"),
                                message=error_data.get("message", "Unknown error"),
                            ),
                        )
                        logger.debug("← [%d] error: %s", command_id, error_data.get("message"))
                else:
                    logger.debug("← event: %s", data.get("method", "unknown"))
        except websockets.ConnectionClosed:
            logger.info("WebSocket closed")
        finally:
            self._correlator.reject_all(BiDiConnectionError("Connection closed"))

    async def close(self) -> None:
        self._closed = True
        if self._receive_task:
            self._receive_task.cancel()
        if self._ws:
            await self._ws.close()
        logger.info("Connection closed")