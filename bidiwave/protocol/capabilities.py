"""Browser capabilities reported via BiDi."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Capabilities(BaseModel):
    """Browser capabilities detected via session.status."""

    model_config = ConfigDict(extra="allow")

    browser_name: str = ""
    browser_version: str = ""
    platform_name: str = ""
    vendor: str = ""
    supports_browsing: bool = True
    supports_script: bool = True
    supports_network: bool = False
    supports_input: bool = False


def detect_capabilities(status_response: dict[str, Any]) -> Capabilities:
    """Parses the session.new/status response and detects capabilities."""
    result = status_response.get("result", status_response)
    caps_data = result.get("capabilities", result)

    browser_name = caps_data.get("browserName", "")
    browser_version = caps_data.get("browserVersion", "")
    platform_name = caps_data.get("platformName", "")
    vendor = caps_data.get("vendor", "")

    supports_network = "firefox" in browser_name.lower()
    supports_input = "firefox" in browser_name.lower()

    return Capabilities(
        browser_name=browser_name,
        browser_version=browser_version,
        platform_name=platform_name,
        vendor=vendor,
        supports_browsing=True,
        supports_script=True,
        supports_network=supports_network,
        supports_input=supports_input,
    )