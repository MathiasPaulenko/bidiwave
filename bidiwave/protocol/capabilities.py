"""Capabilities del browser reportadas via BiDi."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Capabilities(BaseModel):
    """Capabilities reportadas por el browser en session.new."""

    model_config = ConfigDict(extra="allow")

    browser_name: str
    browser_version: str
    platform_name: str
    vendor: str


def detect_capabilities(status_response: dict[str, Any]) -> Capabilities:
    """Extrae Capabilities desde la respuesta de session.status."""
    result = status_response.get("result", status_response)
    caps = result.get("capabilities", result)
    return Capabilities(
        browser_name=caps.get("browserName", "unknown"),
        browser_version=caps.get("browserVersion", "unknown"),
        platform_name=caps.get("platformName", "unknown"),
        vendor=caps.get("vendor", "unknown"),
    )