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


class InstallResult(BaseModel):
    """Result of webExtension.install."""

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

    async def install(self, archive_path: str) -> WebExtensionInfo:
        """Installs a web extension from an archive file.

        Args:
            archive_path: File system path to the extension archive
                (e.g. .zip or .crx file).

        Returns:
            WebExtensionInfo with the extension ID.
        """
        result = await self._connection.send_command(
            WEB_EXTENSION_INSTALL, {"archivePath": archive_path}
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
