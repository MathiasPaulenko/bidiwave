# Quick Start

## Launch a browser with BiDi

=== "Chrome"

    ```bash
    chromedriver --port=9515
    ```

    Then connect to the WebSocket URL returned by the driver.

=== "Edge"

    ```bash
    msedgedriver --port=9516
    ```

=== "Firefox"

    ```bash
    firefox --headless --remote-debugging-port=9223 --no-remote
    ```

See [Browser Setup](../guides/browser-setup.md) for detailed instructions.

## Hello world

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

asyncio.run(main())
```

## Console log monitoring

```python
async with await BiDiClient.connect(url) as client:
    async def on_log(entry):
        print(f"[{entry.level}] {entry.text}")

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    async with await client.browsing.open("https://example.com") as page:
        await page.evaluate("console.log('hello!')")
        await asyncio.sleep(2)
```

## Screenshot

```python
async with await BiDiClient.connect(url) as client:
    async with await client.browsing.open("https://example.com") as page:
        screenshot = await page.screenshot()
        with open("screenshot.png", "wb") as f:
            f.write(screenshot)
```

## Input simulation

```python
async with await BiDiClient.connect(url) as client:
    async with await client.browsing.open("https://example.com") as page:
        ctx = page.context

        await client.input.click(ctx, x=100, y=200)
        await client.input.type_text(ctx, "Hello, world!")
        await client.input.press_key(ctx, "Enter")
        await client.input.scroll(ctx, delta_y=500)
```

## Network interception

```python
async with await BiDiClient.connect(url) as client:
    intercept = await client.network.add_intercept(
        phases=["beforeRequestSent"],
        url_patterns=["*ads.example.com*"],
    )

    async with await client.browsing.open("https://example.com") as page:
        await asyncio.sleep(2)

    await client.network.remove_intercept(intercept.intercept_id)
```

## Next steps

- [Browsing](../usage/browsing.md) — navigation, screenshots, contexts
- [Script](../usage/script.md) — evaluate JS, call functions
- [Input Simulation](../usage/input.md) — clicks, keyboard, scroll
- [Network Interception](../usage/network.md) — block, modify, mock requests
- [Cookbook](../guides/cookbook.md) — more recipes
