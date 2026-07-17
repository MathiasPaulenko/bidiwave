"""Tests de detect_capabilities."""

from bidiwave.protocol.capabilities import Capabilities, detect_capabilities


def test_detect_chrome_capabilities():
    caps = detect_capabilities({
        "result": {
            "capabilities": {
                "browserName": "chrome",
                "browserVersion": "149.0.7827.155",
                "platformName": "windows",
                "vendor": "Google Inc.",
            }
        }
    })
    assert caps.browser_name == "chrome"
    assert caps.browser_version == "149.0.7827.155"
    assert caps.platform_name == "windows"
    assert caps.vendor == "Google Inc."
    assert caps.supports_browsing is True
    assert caps.supports_script is True
    assert caps.supports_network is True
    assert caps.supports_input is True


def test_detect_firefox_capabilities():
    caps = detect_capabilities({
        "result": {
            "capabilities": {
                "browserName": "firefox",
                "browserVersion": "134.0",
                "platformName": "linux",
                "vendor": "Mozilla",
            }
        }
    })
    assert caps.browser_name == "firefox"
    assert caps.supports_network is True
    assert caps.supports_input is True


def test_detect_capabilities_without_result_wrapper():
    caps = detect_capabilities({
        "capabilities": {
            "browserName": "chrome",
            "browserVersion": "100",
            "platformName": "mac",
            "vendor": "Google",
        }
    })
    assert caps.browser_name == "chrome"
    assert caps.browser_version == "100"


def test_capabilities_defaults():
    caps = Capabilities()
    assert caps.browser_name == ""
    assert caps.supports_browsing is True
    assert caps.supports_network is True


def test_detect_capabilities_without_browser_name_does_not_claim_support():
    """session.status does not report browser info; detection must not
    fabricate support flags when no browser data is available."""
    caps = detect_capabilities({"result": {"ready": True, "message": ""}})
    assert caps.browser_name == ""
    assert caps.supports_browsing is False
    assert caps.supports_script is False
    assert caps.supports_network is False
    assert caps.supports_input is False


def test_detect_capabilities_empty_dict():
    caps = detect_capabilities({})
    assert caps.browser_name == ""
    assert caps.supports_browsing is False
