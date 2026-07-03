# bidiwave

WebDriver BiDi for Python — talk to any browser via the W3C standard.

## Features

- **Browsing** — create contexts, navigate, screenshots, wait for elements
- **Script** — evaluate JS, call functions, handle remote values
- **Input** — simulate clicks, keyboard, scroll, drag & drop, file uploads
- **Network** — monitor, block, modify, and mock HTTP requests
- **Storage** — get, set, and delete cookies
- **Events** — real-time event subscriptions with async handlers
- **Reconnection** — automatic reconnect with configurable retries
- **Typed** — full type hints, Pydantic models, mypy strict

## Install

```bash
pip install bidiwave
```

## Quick example

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

## Documentation

- [Installation](getting-started/installation.md)
- [Quick Start](getting-started/quick-start.md)
- [Browsing](usage/browsing.md)
- [Script](usage/script.md)
- [Input Simulation](usage/input.md)
- [Network Interception](usage/network.md)
- [Cookies & Storage](usage/storage.md)
- [Cookbook](guides/cookbook.md)
- [API Reference](api/client.md)
