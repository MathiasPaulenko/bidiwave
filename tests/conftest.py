"""Global pytest configuration — markers and options."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: unit tests without browser")
    config.addinivalue_line("markers", "integration: tests with a real browser")
    config.addinivalue_line("markers", "contract: tests against W3C spec")
    config.addinivalue_line("markers", "slow: slow tests (>1s)")
    config.addinivalue_line("markers", "chrome: Chrome-specific tests")
    config.addinivalue_line("markers", "firefox: Firefox-specific tests")
