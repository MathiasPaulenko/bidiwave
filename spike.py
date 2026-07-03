"""Spike: validar que WebDriver BiDi funciona con Chrome y Firefox.

Uso:
    python spike.py --browser chrome
    python spike.py --browser firefox
"""

import argparse
import asyncio
import json
import subprocess
import sys

import websockets


async def spike_bidi(url: str, browser: str) -> None:
    """Conectar a BiDi, crear sesión, imprimir resultado."""
    print(f"Conectando a {url} ...")

    async with websockets.connect(url) as ws:
        command = {
            "id": 1,
            "method": "session.new",
            "params": {
                "capabilities": {
                    "alwaysMatch": {
                        "webSocketUrl": True,
                    }
                }
            },
        }
        await ws.send(json.dumps(command))
        print(f"→ {command['method']}")

        raw = await asyncio.wait_for(ws.recv(), timeout=10)
        response = json.loads(raw)
        print(f"← type={response.get('type')}")

        if response.get("type") == "success":
            result = response.get("result", {})
            session_id = result.get("sessionId", "N/A")
            caps = result.get("capabilities", {})
            print(f"  sessionId: {session_id}")
            print(f"  browserName: {caps.get('browserName', 'N/A')}")
            print(f"  browserVersion: {caps.get('browserVersion', 'N/A')}")
            print(f"  platformName: {caps.get('platformName', 'N/A')}")
            print(f"  webSocketUrl: {caps.get('webSocketUrl', 'N/A')}")
            print(f"\n✅ {browser} BiDi funciona correctamente")
        elif response.get("type") == "error":
            error = response.get("error", {})
            print(f"  error code: {error.get('code')}")
            print(f"  error message: {error.get('message')}")
            print(f"\n❌ {browser} BiDi falló")
            sys.exit(1)


def launch_chrome(port: int = 9222) -> subprocess.Popen:
    """Lanzar Chrome headless con BiDi."""
    return subprocess.Popen(
        [
            "google-chrome-stable",
            "--headless=new",
            f"--remote-debugging-port={port}",
            "--enable-bidi",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
        ]
    )


def launch_firefox(port: int = 9223) -> subprocess.Popen:
    """Lanzar Firefox headless con BiDi."""
    return subprocess.Popen(
        [
            "firefox",
            "--headless",
            f"--remote-debugging-port={port}",
            "--no-remote",
        ]
    )


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["chrome", "firefox"], required=True)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    port = args.port or (9222 if args.browser == "chrome" else 9223)

    proc = launch_chrome(port) if args.browser == "chrome" else launch_firefox(port)

    print(f"Esperando {args.browser} en puerto {port} ...")
    await asyncio.sleep(3)

    try:
        bidi_url = f"ws://localhost:{port}/session"
        await spike_bidi(bidi_url, args.browser)
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    asyncio.run(main())
