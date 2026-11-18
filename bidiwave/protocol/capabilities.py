"""Browser capabilities reported via BiDi."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class Capabilities(BaseModel):
    """Browser capabilities detected via session.new."""

    model_config = ConfigDict(extra="allow")

    browser_name: str = ""
    browser_version: str = ""
    platform_name: str = ""
    vendor: str = ""
    supports_browsing: bool = True
    supports_script: bool = True
    supports_network: bool = True
    supports_input: bool = True


def detect_capabilities(status_response: dict[str, Any]) -> Capabilities:
    """Parses the session.new/status response and detects capabilities.

    Browser identification (browserName, browserVersion, platformName,
    vendor) is only present in the ``session.new`` result per spec —
    ``session.status`` does not report it. When that data is missing,
    ``supports_*`` flags are left at their unknown state (False) instead
    of being assumed True, since we have no evidence the browser
    actually implements those modules.
    """
    if not isinstance(status_response, dict):
        status_response = {}
    result = status_response.get("result", status_response)
    if not isinstance(result, dict):
        result = {}
    caps_data = result.get("capabilities", result)
    if not isinstance(caps_data, dict):
        caps_data = {}

    def _text(key: str) -> str:
        value = caps_data.get(key)
        return value if isinstance(value, str) else ""

    browser_name = _text("browserName")
    browser_version = _text("browserVersion")
    platform_name = _text("platformName")
    vendor = _text("vendor")

    # All WebDriver BiDi implementations are required to support these
    # core modules, but we can only claim detection succeeded if we
    # actually received browser identification data.
    detected = bool(browser_name)

    return Capabilities(
        browser_name=browser_name,
        browser_version=browser_version,
        platform_name=platform_name,
        vendor=vendor,
        supports_browsing=detected,
        supports_script=detected,
        supports_network=detected,
        supports_input=detected,
    )