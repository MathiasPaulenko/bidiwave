# bidiwave

WebDriver BiDi for Python — talk to any browser via W3C standard.

[![CI](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/test.yml/badge.svg)](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/bidiwave)](https://pypi.org/project/bidiwave/)
[![Python](https://img.shields.io/pypi/pyversions/bidiwave)](https://pypi.org/project/bidiwave/)
[![License](https://img.shields.io/github/license/MathiasPaulenko/bidiwave)](LICENSE)

## Features

- **W3C WebDriver BiDi** — standard, not proprietary CDP
- **Cross-browser** — Chrome, Firefox, Edge (Safari when BiDi support lands)
- **Async-first** — native `async/await` with `asyncio`
- **Event streaming** — console logs, navigation, network, contexts in real time
- **Input simulation** — clicks, keyboard, scroll, drag & drop via `input.performActions`
- **Network interception** — block, modify and mock HTTP requests
- **Type-safe** — Pydantic v2 models, type narrowing with `match`
- **Lightweight** — no Selenium, no Playwright required

## Install

```bash
pip install bidiwave
```

## Quick start

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://example.com") as page:
            # Evaluate JS
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

            # Screenshot
            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)

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

## Input simulation

```python
async with await BiDiClient.connect(url) as client:
    async with await client.browsing.open("https://example.com") as page:
        ctx = page.context

        # Click at coordinates
        await client.input.click(ctx, x=100, y=200)

        # Type text
        await client.input.type_text(ctx, "Hello, world!")

        # Press Enter
        await client.input.press_key(ctx, "Enter")

        # Scroll down 500px
        await client.input.scroll(ctx, delta_y=500)

        # Drag and drop
        await client.input.drag_and_drop(ctx, 100, 100, 300, 300)
```

## Network interception

```python
async with await BiDiClient.connect(url) as client:
    # Block all requests to ads
    intercept = await client.network.add_intercept(
        phases=["beforeRequestSent"],
        url_patterns=["*ads.example.com*"],
    )

    async with await client.browsing.open("https://example.com") as page:
        await asyncio.sleep(2)

    await client.network.remove_intercept(intercept.intercept_id)
```

## Launch a browser with BiDi

### Chrome

```bash
google-chrome --headless=new --remote-debugging-port=9222 --enable-bidi
```

### Firefox

```bash
firefox --headless --remote-debugging-port=9223 --no-remote
```

## Documentation

- [Quick Start](https://bidiwave.readthedocs.io/quick-start/)
- [API Reference](https://bidiwave.readthedocs.io/api/)
- [Network](https://bidiwave.readthedocs.io/api/network/)
- [Input](https://bidiwave.readthedocs.io/api/input/)
- [Cookbook](https://bidiwave.readthedocs.io/cookbook/)
- [Error Handling](https://bidiwave.readthedocs.io/error-handling/)

## License

MIT
