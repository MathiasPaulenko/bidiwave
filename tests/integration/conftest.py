"""Fixtures para integration tests con un WebDriver real.

Se busca un driver ejecutable en este orden:

1. Variables de entorno ``EDGEDRIVER_PATH`` / ``CHROMEDRIVER_PATH``.
2. ``msedgedriver`` o ``chromedriver`` en el PATH.
3. ``bin/edgedriver/msedgedriver.exe`` o ``bin/chromedriver/chromedriver.exe``
   relativos a la raíz del repo.

Si no se encuentra ninguno, los tests de integración se saltan.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

REPO_ROOT = Path(__file__).resolve().parents[2]
DRIVER_PORT = 9516


def _find_driver() -> tuple[str, str] | None:
    """Returns (driver_path, browser_kind) or None. kind is "edge"|"chrome"."""
    candidates = [
        ("EDGEDRIVER_PATH", "msedgedriver", "edge"),
        ("CHROMEDRIVER_PATH", "chromedriver", "chrome"),
    ]
    for env_var, exe, kind in candidates:
        env_path = os.environ.get(env_var)
        if env_path and Path(env_path).is_file():
            return env_path, kind
        on_path = shutil.which(exe)
        if on_path:
            return on_path, kind
        bundled = REPO_ROOT / "bin" / f"{kind}driver" / f"{exe}.exe"
        if bundled.is_file():
            return str(bundled), kind
    return None


def _wait_for_port(port: int, timeout: float = 30.0) -> bool:
    """Wait for the driver to become available."""
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


def _create_webdriver_session(
    browser: str = "edge", port: int = DRIVER_PORT
) -> str:
    """Creates a WebDriver session and returns the BiDi WebSocket URL."""
    options_key = "ms:edgeOptions" if browser == "edge" else "goog:chromeOptions"
    payload = json.dumps(
        {
            "capabilities": {
                "alwaysMatch": {
                    "webSocketUrl": True,
                    "acceptInsecureCerts": True,
                    options_key: {
                        "args": ["--headless", "--no-sandbox", "--disable-gpu"],
                    },
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


@pytest.fixture(scope="session")
def _driver_proc() -> Iterator[tuple[subprocess.Popen[bytes], str]]:
    """Launches the driver once per session."""
    found = _find_driver()
    if found is None:
        pytest.skip(
            "no WebDriver found — set EDGEDRIVER_PATH/CHROMEDRIVER_PATH "
            "or put msedgedriver/chromedriver on PATH"
        )
    driver, browser = found

    proc = subprocess.Popen(
        [driver, f"--port={DRIVER_PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_port(DRIVER_PORT):
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        pytest.fail(f"Driver did not start on port {DRIVER_PORT}")

    yield proc, browser

    # Only terminate the driver process we launched.
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def chrome_bidi(_driver_proc: tuple[subprocess.Popen[bytes], str]) -> str:
    """Creates a new WebDriver session per test and returns the BiDi URL."""
    _, browser = _driver_proc
    return _create_webdriver_session(browser)


@pytest_asyncio.fixture
async def client(request: pytest.FixtureRequest) -> Any:
    """Connected BiDiClient. Uses indirect parametrization to select browser."""
    from bidiwave import BiDiClient, ClientConfig

    fixture_name = request.param
    bidi_url = request.getfixturevalue(fixture_name)

    config = ClientConfig(timeout=60.0, max_retries=1)
    c = await BiDiClient.connect(bidi_url, config=config)
    yield c
    await c.close()


@pytest_asyncio.fixture
async def context(client: Any) -> Any:
    """BrowsingContext created and cleaned up automatically."""
    ctx = await client.browsing.create_context()
    yield ctx
    with contextlib.suppress(Exception):
        await client.browsing.close(ctx)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark all tests in integration/ with @pytest.mark.integration."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
