"""Fixtures para integration tests con ChromeDriver real."""

from __future__ import annotations

import contextlib
import json
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest
import pytest_asyncio

CHROMEDRIVER_PATH = r"D:\Codigo\bidiwave\bin\chromedriver-win64\chromedriver.exe"
DRIVER_PORT = 9515


def _wait_for_port(port: int, timeout: float = 30.0) -> bool:
    """Espera a que ChromeDriver esté disponible."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(
                f"http://localhost:{port}/status", timeout=2
            )
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def _create_webdriver_session(port: int = DRIVER_PORT) -> str:
    """Crea una sesión WebDriver y retorna la URL del WebSocket BiDi."""
    payload = json.dumps(
        {
            "capabilities": {
                "alwaysMatch": {
                    "webSocketUrl": True,
                    "acceptInsecureCerts": True,
                }
            }
        }
    ).encode()

    req = urllib.request.Request(
        f"http://localhost:{port}/session",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    data: dict[str, Any] = json.loads(resp.read())
    return data["value"]["capabilities"]["webSocketUrl"]


@pytest.fixture
def chrome_bidi() -> Iterator[str]:
    """Lanza ChromeDriver y retorna la URL del endpoint BiDi."""
    proc = subprocess.Popen(
        [CHROMEDRIVER_PATH, f"--port={DRIVER_PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_port(DRIVER_PORT):
        proc.terminate()
        proc.wait(timeout=10)
        pytest.fail("ChromeDriver no arrancó en el puerto {DRIVER_PORT}")

    bidi_url = _create_webdriver_session()

    yield bidi_url

    proc.terminate()
    proc.wait(timeout=10)


@pytest_asyncio.fixture
async def client(request: pytest.FixtureRequest) -> Any:
    """BiDiClient conectado. Usa indirect parametrization para seleccionar browser."""
    from bidiwave import BiDiClient, ClientConfig

    fixture_name = request.param
    bidi_url = request.getfixturevalue(fixture_name)

    config = ClientConfig(timeout=60.0, max_retries=1)
    c = await BiDiClient.connect(bidi_url, config=config)
    await c.session.new()
    yield c
    await c.close()


@pytest_asyncio.fixture
async def context(client: Any) -> Any:
    """BrowsingContext creado y limpiado automáticamente."""
    ctx = await client.browsing.create_context()
    yield ctx
    with contextlib.suppress(Exception):
        await client.browsing.close(ctx)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Marcar todos los tests en integration/ con @pytest.mark.integration."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
