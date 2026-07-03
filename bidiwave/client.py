"""BiDiClient — API pública de bidiwave."""

from __future__ import annotations

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.session import SessionModule
from bidiwave.transport.connection import Connection


class BiDiClient:
    """Cliente WebDriver BiDi.

    Ejemplo:
        client = await BiDiClient.connect("ws://localhost:9222/session")
        await client.session.new()
        ctx = await client.browsing.create_context()
        await client.browsing.navigate(ctx.id, "https://example.com")
        await client.close()
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self.session = SessionModule(connection)
        self.browsing = BrowsingModule(connection)
        self.script = ScriptModule(connection)

    @classmethod
    async def connect(cls, url: str) -> BiDiClient:
        connection = Connection(url)
        await connection.connect()
        return cls(connection)

    async def close(self) -> None:
        await self._connection.close()