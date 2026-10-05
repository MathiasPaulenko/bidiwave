"""Log module for the WebDriver BiDi protocol.

The W3C BiDi log module defines no commands — only the
``log.entryAdded`` event. Subscribe to it via ``client.session`` and
register a handler with ``client.on("log.entryAdded", handler)`` or
``client.on_log_entry(handler)``.
"""

from __future__ import annotations

from bidiwave.transport.connection import Connection


class LogModule:
    """Namespace for log-related functionality.

    The spec defines no log commands; this module exists so
    ``client.log`` remains a stable namespace for log events.
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
