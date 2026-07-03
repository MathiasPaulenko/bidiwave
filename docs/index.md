# bidiwave

WebDriver BiDi for Python — a typed, async client for the W3C WebDriver
Bidirectional Protocol. Talk to Chrome, Edge, and Firefox through a single
standard API with real-time event streaming.

## Why bidiwave?

- **W3C standard** — no proprietary protocols, no browser-specific CDP
  hacks. One API for all browsers.
- **Real-time events** — the WebSocket connection lets the browser push
  events to your script: console logs, network requests, navigation, and
  more. No polling.
- **Fully typed** — every command, result, and event is a Pydantic model
  with type hints. IDE autocomplete and mypy strict mode work out of the
  box.
- **Async-first** — built on `asyncio` and `websockets`. No threads, no
  blocking calls.
- **Resilient** — automatic reconnection with exponential backoff.
  Configurable event queue with backpressure policies.
- **Ergonomic** — the `Page` object wraps browsing contexts with
  convenient methods. Pattern-match on `RemoteValue` for type-safe JS
  results.

## Features

- **Browsing** — create tabs/windows, navigate, take screenshots, wait
  for elements with `MutationObserver`-based selectors or JS expressions
- **Script** — evaluate JavaScript, call functions with arguments, handle
  remote values via typed `RemoteValue` subclasses
- **Input** — simulate mouse clicks, keyboard typing, scrolling,
  drag-and-drop, and file uploads with action sequences
- **Network** — monitor requests/responses, intercept and block, modify
  headers/URLs, provide synthetic responses
- **Storage** — get, set, and delete cookies with full attribute support
  (HttpOnly, Secure, SameSite, expires, etc.)
- **Events** — subscribe to browser events with async handlers, error
  isolation, and decorator support
- **Reconnection** — automatic WebSocket reconnection with configurable
  retries and exponential backoff

## Install

```bash
pip install bidiwave
```

See [Installation](getting-started/installation.md) for requirements and
setup instructions.

## Quick example

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        # Listen to console logs
        async def on_log(entry):
            print(f"[{entry.level.upper()}] {entry.text}")

        client.on("log.entryAdded", on_log)
        await client.session.subscribe(["log.entryAdded"])

        # Open a page and interact with it
        async with await client.browsing.open("https://example.com") as page:
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)

asyncio.run(main())
```

## Documentation

### Getting Started

- [Installation](getting-started/installation.md) — requirements, install, verify
- [Quick Start](getting-started/quick-start.md) — your first BiDi script

### Usage

- [Browsing](usage/browsing.md) — contexts, navigation, screenshots, waits
- [Script](usage/script.md) — evaluate JS, call functions, RemoteValue
- [Events](usage/events.md) — real-time event subscriptions
- [Input Simulation](usage/input.md) — clicks, keyboard, scroll, drag
- [Network Interception](usage/network.md) — block, modify, mock requests
- [Cookies & Storage](usage/storage.md) — get, set, delete cookies
- [Configuration](usage/configuration.md) — timeouts, reconnection, logging

### Guides

- [Browser Setup](guides/browser-setup.md) — Chrome, Edge, Firefox setup
- [Cookbook](guides/cookbook.md) — recipes for common tasks
- [Error Handling](guides/error-handling.md) — exception hierarchy and patterns

### API Reference

- [BiDiClient](api/client.md) — main client class
- [Session](api/session.md) — session management
- [Browsing](api/browsing.md) — browsing contexts and navigation
- [Script](api/script.md) — JavaScript execution
- [Network](api/network.md) — network interception
- [Input](api/input.md) — input simulation
- [Storage](api/storage.md) — cookie management
- [Events](api/events.md) — event dispatcher and models
- [RemoteValue](api/remote-value.md) — typed JS return values
- [Exceptions](api/exceptions.md) — error hierarchy
- [Config](api/config.md) — configuration models

### Reference

- [Changelog](reference/changelog.md) — version history
- [Protocol Reference](reference/protocol-reference.md) — BiDi commands and events
- [Spike Notes](reference/spike-notes.md) — initial BiDi validation findings
