"""WebExtension module for the WebDriver BiDi protocol."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from bidiwave.protocol.constants import (
    WEB_EXTENSION_INSTALL,
    WEB_EXTENSION_UNINSTALL,
)
from bidiwave.transport.connection import Connection


class WebExtensionInfo(BaseModel):
    """Information about an installed web extension."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    extension: str = Field(alias="extension")


class WebExtensionModule:
    """Module for managing browser extensions.

    Commands:
        - install — install a web extension from an archive path
        - uninstall — uninstall a previously installed extension

    Example:
        result = await client.web_extension.install("/path/to/extension.zip")
        await client.web_extension.uninstall(result.extension)
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def install(
        self, extension_data: dict[str, str] | str
    ) -> WebExtensionInfo:
        """Installs a web extension.

        Args:
            extension_data: Either a path to a packed extension archive
                (sent as ``{"type": "archivePath", "path": ...}``) or a
                full ExtensionData dict per the spec:
                ``{"type": "path", "path": ...}`` for an unpacked
                directory, ``{"type": "archivePath", "path": ...}`` for a
                packed archive, or ``{"type": "base64", "value": ...}``.

        Returns:
            WebExtensionInfo with the extension ID.
        """
        if isinstance(extension_data, str):
            extension_data = {"type": "archivePath", "path": extension_data}
        result = await self._connection.send_command(
            WEB_EXTENSION_INSTALL, {"extensionData": extension_data}
        )
        return WebExtensionInfo.model_validate(result)

    async def uninstall(self, extension: str) -> None:
        """Uninstalls a previously installed web extension.

        Args:
            extension: ID of the extension to uninstall.
        """
        await self._connection.send_command(
            WEB_EXTENSION_UNINSTALL, {"extension": extension}
        )
