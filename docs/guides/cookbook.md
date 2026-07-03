# Cookbook — bidiwave

## Example 1: Console logger

Capture all console logs from a page.

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        logs: list[str] = []

        async def on_log(entry):
            ts = entry.datetime.strftime("%H:%M:%S.%f")[:-3]
            logs.append(f"[{ts}] [{entry.level.upper()}] {entry.text}")
            print(logs[-1])

        client.on("log.entryAdded", on_log)
        await client.session.subscribe(["log.entryAdded"])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(5)

asyncio.run(main())
```

## Example 2: Full page screenshot

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)
            print("Screenshot saved to screenshot.png")

asyncio.run(main())
```

## Example 3: Extract data from a page

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        async with await client.browsing.open("https://news.ycombinator.com") as page:
            result = await page.call(
                """() => {
                    const rows = document.querySelectorAll('.athing');
                    return Array.from(rows).slice(0, 10).map(row => {
                        const title = row.querySelector('.titleline > a');
                        return {
                            id: row.id,
                            title: title?.textContent,
                            url: title?.href,
                        };
                    });
                }""",
            )

            for item in result.value:
                print(f"[{item['id']}] {item['title']} — {item['url']}")

asyncio.run(main())
```

## Example 4: Multiple tabs in parallel

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def scrape_page(client, url):
    async with await client.browsing.open(url) as page:
        result = await page.evaluate("document.title")
        match result:
            case StringValue(value=title):
                return title
            case _:
                return "unknown"

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net",
        ]

        titles = await asyncio.gather(*[scrape_page(client, url) for url in urls])

        for url, title in zip(urls, titles):
            print(f"{url} → {title}")

asyncio.run(main())
```

## Example 5: Wait for an element to appear

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            found = await page.wait_for_selector("h1", timeout=5)
            print(f"Element found: {found}")

asyncio.run(main())
```

## Example 6: Reconnect handling

```python
import asyncio
from bidiwave import BiDiClient, ClientConfig

async def main():
    config = ClientConfig(max_retries=5)
    async with await BiDiClient.connect("ws://localhost:9222/session", config=config) as client:
        async def on_reconnect():
            print("Reconnected. Recreating session...")
            await client.session.subscribe(["log.entryAdded"])

        client.on_reconnect(on_reconnect)

        async def on_disconnect():
            print("Connection lost. Retrying...")

        client.on_disconnect(on_disconnect)

        while True:
            await asyncio.sleep(1)

asyncio.run(main())
```

## Example 7: Capability-aware code

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        print(f"Browser: {client.capabilities.browser_name} {client.capabilities.browser_version}")
        print(f"Browsing: {client.capabilities.supports_browsing}")
        print(f"Script: {client.capabilities.supports_script}")
        print(f"Network: {client.capabilities.supports_network}")

        if client.capabilities.supports_network:
            # Use network module
            ...
        else:
            print("Network not supported on this browser")

asyncio.run(main())
```

## Example 8: Simulate user input

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            ctx = page.context

            # Click an element
            await client.input.click(ctx, x=100, y=200)

            # Type text
            await client.input.type_text(ctx, "Hello, world!")

            # Press Enter
            await client.input.press_key(ctx, "Enter")

            # Scroll down 500px
            await client.input.scroll(ctx, delta_y=500)

            # Drag and drop
            await client.input.drag_and_drop(ctx, 100, 100, 300, 300)

asyncio.run(main())
```

## Example 9: Block network requests

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        # Block all requests to ad domains
        intercept = await client.network.add_intercept(
            phases=["beforeRequestSent"],
            url_patterns=["*ads.example.com*", "*doubleclick.net*"],
        )

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        # Remove the intercept
        await client.network.remove_intercept(intercept.intercept_id)

asyncio.run(main())
```

## Example 10: Monitor network requests

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        requests: list[str] = []

        async def on_request(event):
            url = event.request.url
            method = event.request.method
            requests.append(f"{method} {url}")
            print(f"→ {method} {url}")

        async def on_response(event):
            status = event.response.status
            url = event.request.url
            print(f"← {status} {url}")

        client.on_request(on_request)
        client.on_response(on_response)
        await client.session.subscribe([
            "network.beforeRequestSent",
            "network.responseCompleted",
        ])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        print(f"\nTotal requests: {len(requests)}")

asyncio.run(main())
```

## Example 11: Mock an HTTP response

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        # Intercept at beforeRequestSent
        intercept = await client.network.add_intercept(
            phases=["beforeRequestSent"],
            url_patterns=["*api.example.com/data*"],
        )

        # When intercepted, provide a synthetic response
        async def on_request(event):
            await client.network.provide_response(
                request=event.request.request,
                status_code=200,
                reason_phrase="OK",
                body="eyJtZXNzYWdlIjogIm1vY2tlZCJ9",  # {"message": "mocked"}
            )

        client.on_request(on_request)

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        await client.network.remove_intercept(intercept.intercept_id)

asyncio.run(main())
```

## Example 12: Set viewport for mobile testing

```python
import asyncio
from bidiwave import BiDiClient, ViewportSize

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            # Simulate iPhone 14 Pro viewport
            await client.browsing.set_viewport(
                page.id,
                viewport=ViewportSize(width=393, height=852),
                device_pixel_ratio=3.0,
            )

            # Take a mobile screenshot
            screenshot = await page.screenshot()
            with open("mobile.png", "wb") as f:
                f.write(screenshot)

asyncio.run(main())
```

## Example 13: Cache override for offline testing

```python
import asyncio
import base64
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        # Serve a cached response without hitting the network
        body = base64.b64encode(b'{"status": "cached"}').decode()
        cache = await client.network.add_cache_override(
            url="https://api.example.com/status",
            method="GET",
            status_code=200,
            body=body,
        )

        async with await client.browsing.open("https://example.com") as page:
            result = await page.evaluate(
                "fetch('https://api.example.com/status').then(r => r.json())",
                await_promise=True,
            )
            print(f"Response from cache: {result.value}")

        await client.network.remove_cache_override(cache.cache)

asyncio.run(main())
```

## Example 14: Emulate a mobile device

```python
import asyncio
from bidiwave import BiDiClient, ViewportSize

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            ctx = page.id

            # Set mobile viewport
            await client.browsing.set_viewport(
                ctx,
                viewport=ViewportSize(width=375, height=812),
                device_pixel_ratio=3.0,
            )

            # Simulate Tokyo location
            await client.emulation.set_geolocation_override(
                coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
                contexts=[ctx],
            )

            # Simulate 3G network
            await client.emulation.set_network_conditions(
                network_conditions={
                    "offline": False,
                    "download_throughput": 50000,
                    "upload_throughput": 25000,
                    "latency": 400,
                },
                contexts=[ctx],
            )

            # Set Tokyo timezone
            await client.emulation.set_timezone_override(
                timezone="Asia/Tokyo",
                contexts=[ctx],
            )

            # Set mobile user agent
            await client.emulation.set_user_agent_override(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
                accept_language="ja-JP",
                contexts=[ctx],
            )

            # Grant geolocation permission
            await client.permissions.set_permission(
                descriptor={"name": "geolocation"},
                state="granted",
                contexts=[ctx],
            )

            # Now test the page under these conditions
            result = await page.evaluate("navigator.userAgent")
            print(f"UA: {result.value}")

asyncio.run(main())
```

## Example 15: Inject a preload script

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        # Inject a preload script that intercepts console.log
        result = await client.preload.add_preload_script(
            function_declaration="""() => {
                const origLog = console.log;
                window.__logs = [];
                console.log = function(...args) {
                    window.__logs.push(args.join(' '));
                    origLog.apply(console, args);
                };
            }""",
        )

        async with await client.browsing.open("https://example.com") as page:
            await page.evaluate("console.log('test message')")
            logs = await page.evaluate("window.__logs")
            print(f"Captured logs: {logs.value}")

        await client.preload.remove_preload_script(result.script)

asyncio.run(main())
```

## Example 16: Monitor cookie changes

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async def on_cookie_changed(event):
            if event.type == "added":
                print(f"Cookie added: {event.cookie.name}={event.cookie.value}")
            elif event.type == "deleted":
                print(f"Cookie deleted: {event.cookie.name}")
            elif event.type == "changed":
                print(f"Cookie changed: {event.cookie.name}={event.cookie.value}")

        client.on("storage.cookieChanged", on_cookie_changed)
        await client.session.subscribe(["storage.cookieChanged"])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(5)

asyncio.run(main())
```

## Example 17: Retrieve response body

```python
import asyncio
import base64
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async def on_response(event):
            # Get the response body
            body_result = await client.network.response_body(event.request.request)
            content = base64.b64decode(body_result.body)
            print(f"Response from {event.request.url}: {len(content)} bytes")

        client.on_response(on_response)
        await client.session.subscribe(["network.responseCompleted"])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

asyncio.run(main())
```

## Example 18: CDP performance metrics

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        # Enable Performance domain via CDP
        await client.cdp.send_command(method="Performance.enable", params={})

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(2)

            # Get performance metrics
            metrics = await client.cdp.send_command(
                method="Performance.getMetrics",
                params={},
            )
            for metric in metrics.result["metrics"]:
                print(f"{metric['name']}: {metric['value']}")

asyncio.run(main())
```
