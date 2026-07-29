<p align="center">
  <img src="https://raw.githubusercontent.com/MathiasPaulenko/bidiwave/main/docs/assets/images/logo-wide.svg" alt="bidiwave" width="480">
</p>

<h3 align="center">WebDriver BiDi for Python — talk to any browser via W3C standard</h3>

<p align="center">
  <strong>Cross-browser · Chrome + Firefox + Edge · async-first · zero Selenium · zero Playwright</strong>
</p>

---

[![CI](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/ci.yml/badge.svg)](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bidiwave.svg)](https://pypi.org/project/bidiwave/)
[![Python](https://img.shields.io/pypi/pyversions/bidiwave.svg)](https://pypi.org/project/bidiwave/)
[![License](https://img.shields.io/github/license/MathiasPaulenko/bidiwave.svg)](https://github.com/MathiasPaulenko/bidiwave/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://mathiaspaulenko.github.io/bidiwave/)

> WebDriver BiDi for Python — talk to any browser via the W3C standard. bidiwave connects to Chrome, Firefox, and Edge using the WebDriver BiDi protocol. No Selenium, no Playwright, no Node.js. Pure async Python with Pydantic v2 models and full type hints.

## Quick demo

**30 seconds to your first BiDi call.**

```bash
pip install bidiwave
```

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")  # "Example Domain"

asyncio.run(main())
```

## Why bidiwave?

bidiwave is a low-level WebDriver BiDi client for Python. It speaks the W3C WebDriver BiDi protocol directly — no Selenium, no Playwright, no Node.js. Unlike CDP (which is Chromium-specific), BiDi is a W3C standard that works across Chrome, Firefox, and Edge.

It is the BiDi backend that powers [wavexis](https://github.com/MathiasPaulenko/wavexis) and [wavexis-mcp](https://github.com/MathiasPaulenko/wavexis-mcp).

### Key features

- **W3C WebDriver BiDi** — standard protocol, not proprietary CDP
- **Cross-browser** — Chrome, Firefox, Edge (Safari when BiDi support lands)
- **Async-first** — native `async/await` with `asyncio`
- **Browsing** — contexts, navigation, screenshots, viewport control with DPR, element waiting, CSS/XPath locators, PDF printing, dialog handling, download events, history traversal, user prompt management
- **Script** — evaluate JS, call functions, typed `RemoteValue` with `match` pattern narrowing, preload scripts with channel communication, realm inspection, serialization options, user activation
- **Input simulation** — clicks, keyboard, scroll, drag & drop, file upload, file dialog events
- **Network interception** — block, modify, mock requests, cache overrides, response body retrieval, authentication handling, extra headers, data collectors, cache behavior control
- **Storage** — get, set, delete cookies with full attribute support, partition key support, cookie change monitoring
- **Emulation** — geolocation, locale, screen orientation, timezone, user agent override, network conditions
- **Permissions** — grant or deny browser permissions without user dialogs
- **Preload scripts** — inject JS before page load for polyfills or monitoring with user context support
- **Web extensions** — install and uninstall browser extensions
- **CDP bridge** — access Chrome DevTools Protocol for browser-specific features
- **Event streaming** — 27 event types with async handlers and error isolation
- **Type-safe** — Pydantic v2 models, full type hints, `mypy` clean
- **Spec-compliant** — W3C WebDriver BiDi (WD 2025-07-28), full coverage
- **Resilient** — automatic reconnection with exponential backoff
- **Lightweight** — no Selenium, no Playwright required

### How it works

```text
Your Python code
  → BiDiClient.connect() connects to a BiDi endpoint
    → ChromeDriver / Firefox / EdgeDriver speaks BiDi
      → client.browsing.open("https://example.com")
        → Browser navigates and returns a page context
      ← Typed response parsed into Pydantic models
    ← Page stays open for chained calls
  ← Connection closes on context exit
```

### Core concepts

- **BiDiClient** — The top-level client. Connects to a BiDi endpoint and provides access to all modules.
- **Page** — A browsing context (tab). Created via `client.browsing.open()`, supports `evaluate()`, `screenshot()`, `navigate()`, etc.
- **Modules** — `client.browsing`, `client.script`, `client.input`, `client.network`, `client.storage`, `client.emulation`, `client.permissions`, `client.preload`, `client.log`, `client.web_extension`, `client.cdp`.
- **RemoteValue** — Typed wrapper for BiDi serialized values. Use `match` pattern narrowing to extract `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `ArrayValue`, `ObjectValue`, etc.

## Requirements

- Python 3.11 or higher
- A BiDi-capable browser endpoint:
  - **Chrome/Edge**: ChromeDriver or EdgeDriver running with BiDi support
  - **Firefox**: Firefox with `--remote-debugging-port` (BiDi is native, no driver needed)
- No Selenium, no Playwright, no Node.js

## Install

```bash
pip install bidiwave
```

## Quick start

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
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
        ctx = page.id

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

## Cookies & storage

```python
from bidiwave import Cookie

async with await BiDiClient.connect(url) as client:
    async with await client.browsing.open("https://example.com") as page:
        # Set a session cookie
        await client.storage.set_cookie(
            page.id,
            cookie=Cookie(
                name="session",
                value="abc123",
                domain="example.com",
                http_only=True,
                secure=True,
            ),
        )

        # Read all cookies
        cookies = await client.storage.get_cookies(page.id)
        for c in cookies:
            print(f"{c.name}={c.value}")

        # Delete one cookie
        await client.storage.delete_cookie(page.id, "session")
```

## Emulation & permissions

```python
from bidiwave import ViewportSize

async with await BiDiClient.connect(url) as client:
    async with await client.browsing.open("https://example.com") as page:
        ctx = page.id

        # Simulate iPhone viewport
        await client.browsing.set_viewport(
            ctx,
            viewport=ViewportSize(width=375, height=812),
            device_pixel_ratio=3.0,
        )

        # Simulate Tokyo location on 3G
        await client.emulation.set_geolocation_override(
            coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
            contexts=[ctx],
        )
        await client.emulation.set_network_conditions(
            network_conditions={
                "offline": False,
                "download_throughput": 50000,
                "upload_throughput": 25000,
                "latency": 400,
            },
            contexts=[ctx],
        )

        # Grant geolocation permission
        await client.permissions.set_permission(
            descriptor={"name": "geolocation"},
            state="granted",
            contexts=[ctx],
        )
```

## Preload scripts

```python
async with await BiDiClient.connect(url) as client:
    # Inject a script that runs before every page load
    result = await client.preload.add_preload_script(
        function_declaration="() => { window.__testMode = true; }",
    )

    async with await client.browsing.open("https://example.com") as page:
        value = await page.evaluate("window.__testMode")
        print(f"Test mode: {value}")

    await client.preload.remove_preload_script(result.script)
```

## Web extensions

```python
async with await BiDiClient.connect(url) as client:
    # Install a browser extension
    result = await client.web_extension.install("/path/to/extension.crx")
    print(f"Installed: {result}")

    # Uninstall when done
    await client.web_extension.uninstall(result.extension)
```

## Launch a browser with BiDi

### Chrome / Edge

```bash
# Chrome — requires ChromeDriver as BiDi proxy
chromedriver --port=9515

# Edge — requires EdgeDriver
msedgedriver --port=9516
```

### Firefox

Firefox implements BiDi natively — no driver needed:

```bash
firefox --headless --remote-debugging-port=9223 --no-remote
```

See [Browser Setup](https://mathiaspaulenko.github.io/bidiwave/guides/browser-setup/)
for detailed instructions.

## Documentation

Full documentation at **[mathiaspaulenko.github.io/bidiwave](https://mathiaspaulenko.github.io/bidiwave/)**

- [Installation](https://mathiaspaulenko.github.io/bidiwave/getting-started/installation/)
- [Quick Start](https://mathiaspaulenko.github.io/bidiwave/getting-started/quick-start/)
- [Browsing](https://mathiaspaulenko.github.io/bidiwave/usage/browsing/)
- [Script](https://mathiaspaulenko.github.io/bidiwave/usage/script/)
- [Network Interception](https://mathiaspaulenko.github.io/bidiwave/usage/network/)
- [Input Simulation](https://mathiaspaulenko.github.io/bidiwave/usage/input/)
- [Cookies & Storage](https://mathiaspaulenko.github.io/bidiwave/usage/storage/)
- [Emulation](https://mathiaspaulenko.github.io/bidiwave/usage/emulation/)
- [Permissions](https://mathiaspaulenko.github.io/bidiwave/usage/permissions/)
- [Preload Scripts](https://mathiaspaulenko.github.io/bidiwave/usage/preload/)
- [Web Extensions](https://mathiaspaulenko.github.io/bidiwave/api/web-extension/)
- [CDP](https://mathiaspaulenko.github.io/bidiwave/usage/cdp/)
- [Events](https://mathiaspaulenko.github.io/bidiwave/usage/events/)
- [Configuration](https://mathiaspaulenko.github.io/bidiwave/usage/configuration/)
- [Cookbook](https://mathiaspaulenko.github.io/bidiwave/guides/cookbook/)
- [Error Handling](https://mathiaspaulenko.github.io/bidiwave/guides/error-handling/)
- [API Reference](https://mathiaspaulenko.github.io/bidiwave/api/client/)
- [Protocol Reference](https://mathiaspaulenko.github.io/bidiwave/reference/protocol-reference/)
- [Changelog](https://mathiaspaulenko.github.io/bidiwave/reference/changelog/)

## Ecosystem

bidiwave is part of the Wave ecosystem — browser automation tools in 100% Python:

| Project | Description |
|---------|-------------|
| **[cdpwave](https://github.com/MathiasPaulenko/cdpwave)** | Chrome DevTools Protocol client |
| **[bidiwave](https://github.com/MathiasPaulenko/bidiwave)** | WebDriver BiDi client — cross-browser, W3C standard (this repo) |
| **[wavexis](https://github.com/MathiasPaulenko/wavexis)** | Browser automation CLI — wraps cdpwave + bidiwave |
| **[wavexis-mcp](https://github.com/MathiasPaulenko/wavexis-mcp)** | MCP server — 220 browser automation tools for LLMs |

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on
development setup, code style, testing, and pull request process.

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) for responsible disclosure.

## License

MIT
