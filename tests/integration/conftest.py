"""Fixtures para integration tests con EdgeDriver real."""

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

EDGEDRIVER_PATH = r"D:\Codigo\bidiwave\bin\edgedriver\msedgedriver.exe"
DRIVER_PORT = 9516


def _wait_for_port(port: int, timeout: float = 30.0) -> bool:
    """Wait for EdgeDriver to become available."""
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
    """Creates a WebDriver session and returns the BiDi WebSocket URL."""
    payload = json.dumps(
        {
            "capabilities": {
                "alwaysMatch": {
                    "webSocketUrl": True,
                    "acceptInsecureCerts": True,
                    "ms:edgeOptions": {
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
def _edgedriver_proc() -> Iterator[subprocess.Popen[bytes]]:
    """Launches EdgeDriver once per session."""
    with contextlib.suppress(Exception):
        subprocess.run(
            ["taskkill", "/F", "/IM", "msedgedriver.exe"],
            capture_output=True,
            timeout=5,
        )
        time.sleep(1)

    proc = subprocess.Popen(
        [EDGEDRIVER_PATH, f"--port={DRIVER_PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_port(DRIVER_PORT):
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        pytest.fail(f"EdgeDriver did not start on port {DRIVER_PORT}")

    yield proc

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    # Only kill msedgedriver, never kill user's Edge browser
    with contextlib.suppress(Exception):
        subprocess.run(
            ["taskkill", "/F", "/IM", "msedgedriver.exe"],
            capture_output=True,
            timeout=5,
        )


@pytest.fixture
def chrome_bidi(_edgedriver_proc: subprocess.Popen[bytes]) -> str:
    """Creates a new WebDriver session per test and returns the BiDi URL."""
    return _create_webdriver_session()


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
