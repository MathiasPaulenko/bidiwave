"""Configuración global de pytest — markers y opciones."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: tests unitarios sin browser")
    config.addinivalue_line("markers", "integration: tests con browser real")
    config.addinivalue_line("markers", "contract: tests contra spec W3C")
    config.addinivalue_line("markers", "slow: tests lentos (>1s)")
    config.addinivalue_line("markers", "chrome: tests específicos de Chrome")
    config.addinivalue_line("markers", "firefox: tests específicos de Firefox")
