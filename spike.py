"""Spike: validate that WebDriver BiDi works with Chrome and Edge.

Uses ChromeDriver/EdgeDriver as a BiDi proxy.

Usage:
    python spike.py --browser chrome
    python spike.py --browser edge
"""

import argparse
import asyncio
import json
import subprocess
import sys
import urllib.error
import urllib.request

import websockets

CHROMEDRIVER_PATH = r"D:\Codigo\bidiwave\bin\chromedriver-win64\chromedriver.exe"
EDGEDRIVER_PATH = r"D:\Codigo\bidiwave\bin\edgedriver\msedgedriver.exe"

DRIVERS = {
    "chrome": (CHROMEDRIVER_PATH, 9515),
    "edge": (EDGEDRIVER_PATH, 9516),
}


def launch_driver(driver_path: str, port: int) -> subprocess.Popen:
    """Launch ChromeDriver/EdgeDriver on the given port."""
    return subprocess.Popen(
        [driver_path, f"--port={port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_webdriver_session(port: int) -> dict:
    """Create a classic WebDriver session requesting webSocketUrl (BiDi).

    Returns the full JSON response.
    """
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
    return json.loads(resp.read())


async def spike_bidi(bidi_url: str, browser: str) -> None:
    """Connect to BiDi and send session.status to validate."""
    print(f"Connecting to BiDi WebSocket: {bidi_url} ...")

    async with websockets.connect(bidi_url) as ws:
        command = {"id": 1, "method": "session.status", "params": {}}
        await ws.send(json.dumps(command))
        print(f"→ {command['method']}")

        raw = await asyncio.wait_for(ws.recv(), timeout=10)
        response = json.loads(raw)
        print(f"← raw: {json.dumps(response, indent=2)[:800]}")
        print(f"← type={response.get('type')}")

        if response.get("type") == "success":
            result = response.get("result", {})
            print(f"  ready: {result.get('ready')}")
            print(f"  message: {result.get('message')}")
            print(f"\n✅ {browser} BiDi works correctly")
        else:
            error = response.get("error", {})
            print(f"  error: {error}")
            print(f"\n❌ {browser} BiDi failed")
            sys.exit(1)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["chrome", "edge"], required=True)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    driver_path, default_port = DRIVERS[args.browser]
    port = args.port or default_port

    proc = launch_driver(driver_path, port)
    print(f"Launching {args.browser}Driver on port {port} ...")
    await asyncio.sleep(2)

    try:
        print("Creating WebDriver session with webSocketUrl=True ...")
        session_resp = create_webdriver_session(port)
        print(f"  status: {session_resp.get('value', {}).get('sessionId', 'N/A')}")

        bidi_url = session_resp.get("value", {}).get("capabilities", {}).get("webSocketUrl", "")
        if not bidi_url:
            print("❌ No webSocketUrl obtained from driver response")
            print(f"  raw: {json.dumps(session_resp, indent=2)[:500]}")
            sys.exit(1)

        print(f"  webSocketUrl: {bidi_url}")
        await spike_bidi(bidi_url, args.browser)

    except urllib.error.URLError as e:
        print(f"❌ HTTP error creating session: {e}")
        sys.exit(1)
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    asyncio.run(main())
