# Quick Start

This guide walks you through your first BiDi script, from launching the
driver to evaluating JavaScript in a page. By the end you'll understand the
connection lifecycle, the `Page` object, and how to subscribe to browser
events.

## Prerequisites

You need a driver process running. See
[Browser Setup](../guides/browser-setup.md) for detailed instructions, but
the short version:

=== "Chrome"

    ```bash
    chromedriver --port=9515
    ```

=== "Edge"

    ```bash
    msedgedriver --port=9516
    ```

=== "Firefox"

    ```bash
    firefox --headless --remote-debugging-port=9223 --no-remote
    ```

## Step 1: Connect to the browser

The entry point is `BiDiClient.connect()`. It opens a WebSocket connection to
the driver and returns a `BiDiClient` instance. Use `async with` to ensure
the connection is closed when your script exits:

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        print("Connected!")
        # ... your code here ...

asyncio.run(main())
```

### What happens during `connect()`?

1. bidiwave opens a WebSocket to the driver's `/session` endpoint.
2. The driver creates a BiDi session and returns capabilities (browser name,
   version, platform).
3. bidiwave starts a background receive loop that listens for responses and
   events.
4. The `BiDiClient` is ready to send commands and receive events.

You don't need to call `session.new()` manually — the driver creates the
session when you connect via the WebSocket URL.

## Step 2: Open a page

The `browsing.open()` method is the most convenient way to start working
with a page. It creates a new browsing context (a tab), navigates to the
URL, waits for the page to load, and returns a `Page` object:

```python
async with await BiDiClient.connect("ws://localhost:9515/session") as client:
    async with await client.browsing.open("https://example.com") as page:
        print(f"Page URL: {page.url}")
        print(f"Context ID: {page.id}")
```

The `Page` object is a convenience wrapper that bundles a browsing context
with a script module. It provides ergonomic methods like `evaluate()`,
`call()`, `screenshot()`, and `wait_for_selector()` so you don't have to
pass the context ID to every call.

When the `async with` block exits, the browsing context (tab) is
automatically closed.

### Manual context management

If you need more control, you can create and close contexts manually:

```python
ctx = await client.browsing.create_context()
await client.browsing.navigate(ctx, "https://example.com", wait="complete")

# ... work with the page ...

await client.browsing.close(ctx)
```

## Step 3: Evaluate JavaScript

Once you have a page, you can run JavaScript in it:

```python
from bidiwave import StringValue

async with await client.browsing.open("https://example.com") as page:
    result = await page.evaluate("document.title")
    match result:
        case StringValue(value=title):
            print(f"Title: {title}")
```

### Understanding RemoteValue

`evaluate()` and `call()` return a `RemoteValue` — a typed wrapper around
whatever JavaScript returned. The protocol serializes JS values into a
JSON structure with a `type` field. bidiwave parses this into specific
Python classes:

| JS type | Python class | Key field |
| ------- | ------------ | --------- |
| `"string"` | `StringValue` | `.value: str` |
| `"number"` | `NumberValue` | `.value: int \| float` |
| `"boolean"` | `BooleanValue` | `.value: bool` |
| `"null"` | `NullValue` | (none) |
| `"undefined"` | `UndefinedValue` | (none) |
| `"bigint"` | `BigIntValue` | `.value: str` |
| `"object"` | `ObjectValue` | `.value: dict` |
| `"array"` | `ArrayValue` | `.value: list` |
| `"function"` | `HandleValue` | `.handle: str` |

Use Python's `match` statement for type-safe pattern matching:

```python
result = await page.evaluate("1 + 1")
match result:
    case NumberValue(value=n):
        print(f"Result: {n}")  # Result: 2
    case _:
        print(f"Unexpected: {result}")
```

See [Script](../usage/script.md) for a deep dive on `evaluate`,
`call_function`, and `RemoteValue`.

## Step 4: Subscribe to events

BiDi's killer feature is real-time event streaming. You can listen to
console logs, network requests, navigation events, and more — without
polling.

```python
async with await BiDiClient.connect("ws://localhost:9515/session") as client:
    async def on_log(entry):
        print(f"[{entry.level}] {entry.text}")

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    async with await client.browsing.open("https://example.com") as page:
        await page.evaluate("console.log('hello from BiDi!')")
        await asyncio.sleep(2)
```

### How events work

1. **Register a handler** with `client.on(event_type, handler)`. The handler
   must be an `async` function that receives a typed event model.
2. **Subscribe** to the event type with
   `await client.session.subscribe([...])`. This tells the browser to start
   sending events of that type.
3. **The browser pushes events** over the WebSocket. bidiwave's receive loop
   dispatches them to your handlers via the `EventDispatcher`.
4. **Error isolation**: if one handler raises an exception, it's logged but
   doesn't affect other handlers or the connection.

See [Events](../usage/events.md) for all event types and patterns.

## Step 5: Take a screenshot

```python
async with await client.browsing.open("https://example.com") as page:
    screenshot = await page.screenshot()
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)
```

`page.screenshot()` returns raw `bytes` (PNG by default). The underlying
protocol command `browsingContext.captureScreenshot` returns base64-encoded
data, but the `Page` object decodes it for you.

## Complete example

Putting it all together — connect, open a page, evaluate JS, listen to
console logs, and take a screenshot:

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

        # Open a page
        async with await client.browsing.open("https://example.com") as page:
            # Get the title
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

            # Trigger a console log
            await page.evaluate("console.log('hello from BiDi!')")

            # Take a screenshot
            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)
            print("Screenshot saved!")

            await asyncio.sleep(1)

asyncio.run(main())
```

## Next steps

- [Browsing](../usage/browsing.md) — navigation, contexts, screenshots, waits
- [Script](../usage/script.md) — evaluate JS, call functions, RemoteValue
- [Input Simulation](../usage/input.md) — clicks, keyboard, scroll, drag
- [Network Interception](../usage/network.md) — block, modify, mock requests
- [Cookies & Storage](../usage/storage.md) — get, set, delete cookies
- [Events](../usage/events.md) — real-time event subscriptions
- [Cookbook](../guides/cookbook.md) — more recipes
