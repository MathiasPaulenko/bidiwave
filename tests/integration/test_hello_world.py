"""Integration test: hello world BiDi contra Chrome via ChromeDriver."""

import asyncio
import json
import subprocess
import sys
import urllib.request

from bidiwave import BiDiClient

CHROMEDRIVER_PATH = r"D:\Codigo\bidiwave\bin\chromedriver-win64\chromedriver.exe"
DRIVER_PORT = 9515


def launch_driver() -> subprocess.Popen:
    return subprocess.Popen(
        [CHROMEDRIVER_PATH, f"--port={DRIVER_PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def create_webdriver_session() -> str:
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
        f"http://localhost:{DRIVER_PORT}/session",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return data["value"]["capabilities"]["webSocketUrl"]


async def main() -> None:
    proc = launch_driver()
    print(f"ChromeDriver en puerto {DRIVER_PORT} ...")
    await asyncio.sleep(2)

    try:
        bidi_url = create_webdriver_session()
        print(f"  webSocketUrl: {bidi_url}")

        client = await BiDiClient.connect(bidi_url)

        status = await client.session.status()
        print(f"  session.status: ready={status.get('ready')}, message={status.get('message')}")

        ctx = await client.browsing.create_context()
        context_id = ctx["context"]
        print(f"  create_context: {context_id}")

        await client.browsing.navigate(context_id, "https://example.com")
        print("  navigate OK")

        result = await client.script.evaluate(context_id, "document.title")
        title = result.get("result", {}).get("value", "N/A")
        print(f"  document.title: {title}")
        assert title == "Example Domain", f"Expected 'Example Domain', got '{title}'"

        await client.browsing.close(context_id)
        print("  close context OK")

        await client.close()
        print("\n✅ Integration test passed")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        sys.exit(1)
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    asyncio.run(main())
