# Browsing

The browsing module manages **browsing contexts** — the BiDi term for tabs
and windows. Each context has its own URL, DOM, and JavaScript realm. You
can create multiple contexts, navigate between URLs, take screenshots, and
wait for elements to appear.

## Browsing contexts

A browsing context is the fundamental unit of browsing in BiDi. When you
create one, the browser opens a new tab (or window). Each context has:

- A unique **context ID** (a string like `"A1B2C3D4E5F6"`)
- A **URL** (the current page URL)
- A **type** (`"tab"` or `"window"`)

### Creating contexts

```python
# Create a new tab
ctx = await client.browsing.create_context(type="tab")

# Create a new window
ctx = await client.browsing.create_context(type="window")
```

The `BrowsingContext` object is an async context manager — when used with
`async with`, it automatically closes the tab when the block exits:

```python
async with await client.browsing.create_context() as ctx:
    await client.browsing.navigate(ctx, "https://example.com")
    # tab is closed when the block exits
```

### The Page convenience object

For most use cases, use `browsing.open()` instead of managing contexts
manually. It creates a context, navigates to the URL, waits for the page
to load, and returns a `Page` object:

```python
async with await client.browsing.open("https://example.com") as page:
    title = await page.evaluate("document.title")
    screenshot = await page.screenshot()
```

The `Page` object wraps a `BrowsingContext` and provides ergonomic methods:

| Method | Description |
| ------ | ----------- |
| `page.evaluate(expr)` | Run JavaScript and return a `RemoteValue` |
| `page.call(fn, args)` | Call a JS function with arguments |
| `page.navigate(url)` | Navigate to a new URL |
| `page.screenshot()` | Take a screenshot, returns `bytes` |
| `page.wait_for_selector(sel)` | Wait for an element to appear in the DOM |
| `page.wait_for_function(expr)` | Wait for a JS expression to return truthy |
| `page.disown(handles)` | Release references to remote objects |
| `page.close()` | Close the tab |
| `page.id` | The context ID (read-only property) |
| `page.url` | The current URL (read-only property) |

## Navigation

Navigation in BiDi is explicit — you call `navigate()` with a URL and a
**wait strategy** that controls when the call returns:

```python
navigation = await client.browsing.navigate(
    ctx,
    "https://example.com",
    wait="complete",  # wait for full page load
)
```

### Wait strategies

The `wait` parameter controls how long the driver waits before returning:

| Value | Description |
| ----- | ----------- |
| `"none"` | Return immediately after the navigation command is sent. The page may not have started loading. |
| `"interactive"` | Wait until the page's `document.readyState` is `"interactive"` — the DOM is parsed but resources (images, scripts) may still be loading. |
| `"complete"` (default) | Wait until `document.readyState` is `"complete"` — the page and all resources are fully loaded. |

Choose `"interactive"` when you want to interact with the DOM as soon as
possible (e.g., clicking a button that doesn't depend on images). Use
`"complete"` when you need the full page rendered (e.g., for screenshots).

### Navigation result

`navigate()` returns a `Navigation` object with:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `context` | `str \| None` | The context ID that navigated |
| `url` | `str` | The URL navigated to |
| `navigation` | `str \| None` | A navigation ID (can be used to track the navigation in events) |
| `status` | `str` | `"complete"` or `"pending"` |

## Screenshots

Take a screenshot of a browsing context:

```python
# Via the Page object (returns bytes)
screenshot = await page.screenshot()
with open("page.png", "wb") as f:
    f.write(screenshot)

# Via the browsing module (returns Screenshot model with base64 data)
result = await client.browsing.screenshot(ctx, format="png")
# result.data is base64-encoded string
```

### Formats

```python
# PNG (default, lossless)
screenshot = await page.screenshot(format="png")

# JPEG (smaller file, supports quality)
screenshot = await page.screenshot(format="jpeg", quality=80)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `format` | `"png" \| "jpeg"` | `"png"` | Image format |
| `quality` | `int \| None` | `None` | JPEG quality (0-100). Only used with `"jpeg"`. |

## Waiting for elements

### wait_for_selector

Waits until a CSS selector matches an element in the DOM. Uses a
`MutationObserver` under the hood — no polling:

```python
found = await page.wait_for_selector("div.product-list", timeout=10.0)
if found:
    print("Element appeared!")
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `selector` | `str` | (required) | CSS selector to wait for |
| `timeout` | `float` | `10.0` | Maximum seconds to wait |

Returns `True` if the element appeared, raises `asyncio.TimeoutError` if
the timeout is reached.

### wait_for_function

Waits until a JavaScript expression returns a truthy value. Polls every
100ms:

```python
result = await page.wait_for_function(
    "document.querySelectorAll('.item').length >= 5",
    timeout=15.0,
)
```

This is useful when you need to wait for a dynamic condition that can't
be expressed as a simple selector — e.g., "wait until at least 5 items
are loaded" or "wait until a global variable is set".

## Context tree

BiDi maintains a tree of browsing contexts. A top-level context (a tab)
can have child contexts (iframes). You can inspect the tree:

```python
tree = await client.browsing.get_tree(
    root=None,       # None = full tree, or pass a context ID
    max_depth=None,  # None = unlimited, or pass an int
)
```

This returns a nested dict representing the context hierarchy. Each node
has a `context` (ID), `url`, `children` (list of child contexts), and
`userContext` (the user context bucket).

## Events

Browsing contexts emit events that you can subscribe to:

| Event | Description |
| ----- | ----------- |
| `browsingContext.contextCreated` | A new context (tab/window/iframe) was created |
| `browsingContext.contextDestroyed` | A context was closed |
| `browsingContext.navigationStarted` | Navigation began in a context |

```python
client.on("browsingContext.contextCreated", lambda e: print(f"New tab: {e.context}"))
client.on("browsingContext.contextDestroyed", lambda e: print(f"Tab closed: {e.context}"))
await client.session.subscribe([
    "browsingContext.contextCreated",
    "browsingContext.contextDestroyed",
])
```

See [Events](events.md) for the full event system documentation.

## API reference

See [Browsing API](../api/browsing.md) for the complete `BrowsingModule`
and `BrowsingContext` reference.
