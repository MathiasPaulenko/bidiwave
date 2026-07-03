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
| `page.reload()` | Reload the current page |
| `page.back()` | Go back in history |
| `page.forward()` | Go forward in history |
| `page.handle_user_prompt()` | Accept or dismiss a dialog (alert/confirm/prompt) |
| `page.print()` | Export the page to PDF, returns `bytes` |
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

## Reload

Reload the current page. Supports the same `wait` strategies as
`navigate()`:

```python
# Full reload
await page.reload(wait="complete")

# Reload ignoring cache
await page.reload(ignore_cache=True)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `wait` | `"none" \| "interactive" \| "complete"` | `"complete"` | Wait strategy |
| `ignore_cache` | `bool \| None` | `None` | If `True`, bypass the browser cache |

## History navigation

Navigate backward or forward in the browsing history:

```python
# Go back
await page.back()

# Go forward
await page.forward()
```

These correspond to the browser's back/forward buttons. If there's no
page to navigate to (e.g., calling `back()` on the first page in
history), the browser stays on the current page.

## Handling dialogs

When a page shows a dialog (`alert`, `confirm`, or `prompt`), BiDi
pauses script execution until you handle it. Use `handle_user_prompt()`
to accept or dismiss it:

```python
# Accept an alert
await page.handle_user_prompt(accept=True)

# Dismiss a confirm dialog
await page.handle_user_prompt(accept=False)

# Accept a prompt and provide text
await page.handle_user_prompt(accept=True, user_text="Hello!")
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `accept` | `bool \| None` | `None` | `True` to accept, `False` to dismiss. `None` = browser default. |
| `user_text` | `str \| None` | `None` | Text to enter in a `prompt()` dialog. Only used if `accept=True`. |

!!! warning "Dialogs block execution"
    While a dialog is open, all BiDi commands for that context are
    blocked. Always handle the prompt before doing anything else.

## Print to PDF

Export the current page as a PDF:

```python
pdf = await page.print(
    orientation="portrait",
    scale=1.0,
    background=False,
)
with open("page.pdf", "wb") as f:
    f.write(pdf)
```

The `Page.print()` method returns raw PDF `bytes`. The `BrowsingModule.print()`
method returns a `PrintResult` with base64-encoded data.

### Print parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `background` | `bool` | `False` | Include background graphics |
| `orientation` | `"portrait" \| "landscape"` | `"portrait"` | Page orientation |
| `scale` | `float` | `1.0` | Scale factor (0.1 to 2.0) |
| `shrink_to_fit` | `bool` | `True` | Shrink content to fit page width |
| `margin` | `dict \| None` | `None` | Margins in inches: `{"top": 0.4, "bottom": 0.4, "left": 0.4, "right": 0.4}` |
| `page` | `dict \| None` | `None` | Page size in inches: `{"width": 8.5, "height": 11}` |
| `page_ranges` | `list[str] \| None` | `None` | Pages to print, e.g. `["1-3", "5"]` |

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

## Viewport

Control the viewport size and device pixel ratio (DPR) for a browsing context.
This is useful for testing responsive layouts and simulating mobile devices.

### Set viewport

```python
from bidiwave import ViewportSize

# Using the typed ViewportSize model
await client.browsing.set_viewport(
    ctx,
    viewport=ViewportSize(width=375, height=812),
    device_pixel_ratio=3.0,  # simulate iPhone DPR
)

# Or pass a dict (automatically converted)
await client.browsing.set_viewport(
    ctx,
    viewport={"width": 1920, "height": 1080},
    device_pixel_ratio=1.0,
)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `context` | `BrowsingContext \| str` | (required) | Context to modify |
| `viewport` | `ViewportSize \| dict \| None` | `None` | Viewport dimensions. `None` resets to default. |
| `device_pixel_ratio` | `float \| None` | `None` | Device pixel ratio (e.g., `2.0` for retina). `None` resets to default. |

The `ViewportSize` model has two fields:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `width` | `int` | Viewport width in CSS pixels |
| `height` | `int` | Viewport height in CSS pixels |

### Get viewport

Retrieve the current viewport and DPR:

```python
result = await client.browsing.get_viewport(ctx)
print(f"Viewport: {result.viewport.width}x{result.viewport.height}")
print(f"DPR: {result.device_pixel_ratio}")
```

## Activate

Bring a browsing context to the foreground (equivalent to switching tabs):

```python
await client.browsing.activate(ctx)
```

This is useful when working with multiple tabs and you need to ensure a
specific tab is active for screenshots or input simulation.

## Locate nodes

Find elements in the DOM using locator strategies:

```python
# CSS selector
nodes = await client.browsing.locate_nodes(
    ctx,
    locator={"type": "css", "value": "div.product-list .item"},
)

# XPath
nodes = await client.browsing.locate_nodes(
    ctx,
    locator={"type": "xpath", "value": "//button[@class='submit']"},
)
```

### Locator types

| Type | Description | Example |
| ---- | ----------- | ------- |
| `"css"` | CSS selector | `{"type": "css", "value": "div.content"}` |
| `"xpath"` | XPath expression | `{"type": "xpath", "value": "//div[@id='main']"}` |

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
| `browsingContext.navigationCompleted` | Navigation completed successfully |
| `browsingContext.fragmentNavigated` | Fragment navigation (#anchor) occurred |
| `browsingContext.domContentLoaded` | DOM parsed, resources still loading |
| `browsingContext.load` | Page fully loaded (all resources) |
| `browsingContext.historyUpdated` | History changed (pushState, replaceState) — Chrome-specific |
| `browsingContext.userPromptOpened` | A dialog (alert/confirm/prompt) opened |

```python
client.on("browsingContext.contextCreated", lambda e: print(f"New tab: {e.context}"))
client.on("browsingContext.contextDestroyed", lambda e: print(f"Tab closed: {e.context}"))
client.on("browsingContext.navigationCompleted", lambda e: print(f"Loaded: {e.url}"))
client.on("browsingContext.historyUpdated", lambda e: print(f"History changed: {e.url}"))
client.on("browsingContext.userPromptOpened", lambda e: print(f"Dialog: {e.type} — {e.message}"))
await client.session.subscribe([
    "browsingContext.contextCreated",
    "browsingContext.contextDestroyed",
    "browsingContext.navigationCompleted",
    "browsingContext.historyUpdated",
    "browsingContext.userPromptOpened",
])
```

### Convenience handlers

```python
client.on_navigation_completed(lambda e: print(f"Nav complete: {e.url}"))
client.on_fragment_navigated(lambda e: print(f"Fragment: {e.url}"))
client.on_load(lambda e: print(f"Page loaded: {e.url}"))
client.on_dom_content_loaded(lambda e: print(f"DOM ready: {e.url}"))
client.on_history_updated(lambda e: print(f"History: {e.url}"))
```

See [Events](events.md) for the full event system documentation.

## API reference

See [Browsing API](../api/browsing.md) for the complete `BrowsingModule`
and `BrowsingContext` reference.
