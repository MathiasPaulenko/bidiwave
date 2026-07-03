# Browsing

## Open a page

```python
async with await client.browsing.open("https://example.com") as page:
    result = await page.evaluate("document.title")
```

The `open()` method creates a browsing context, navigates to the URL, and returns a `Page` object. The context is automatically closed when the `async with` block exits.

## Manual context management

```python
ctx = await client.browsing.create_context()
await client.browsing.navigate(ctx, "https://example.com", wait="complete")

# ... work with the page ...

await client.browsing.close(ctx)
```

## Navigation

```python
nav = await client.browsing.navigate(ctx, "https://example.com", wait="complete")
print(f"URL: {nav.url}, Status: {nav.status}")
```

`wait` options:

- `"none"` — return immediately
- `"interactive"` — wait for DOMContentLoaded
- `"complete"` — wait for full page load (default)

## Screenshot

```python
screenshot = await client.browsing.screenshot(ctx)
with open("screenshot.png", "wb") as f:
    f.write(screenshot.data)
```

## Context tree

```python
tree = await client.browsing.get_tree()
for ctx in tree:
    print(f"Context: {ctx.id}, URL: {ctx.url}")
```

## Wait for selector

```python
found = await client.browsing.wait_for_selector(ctx, "h1", timeout=10)
if found:
    print("Element found!")
```

## Wait for function

```python
result = await client.browsing.wait_for_function(
    ctx,
    "document.readyState === 'complete'",
    timeout=10,
)
```

## Page convenience object

The `Page` object wraps a browsing context with ergonomic methods:

```python
async with await client.browsing.open("https://example.com") as page:
    # Evaluate JS
    result = await page.evaluate("document.title")

    # Call a JS function
    result = await page.call("() => document.querySelector('h1')?.textContent")

    # Screenshot
    screenshot = await page.screenshot()

    # Wait for selector
    await page.wait_for_selector("#loaded", timeout=5)
```
