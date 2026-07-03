# CDP (Chrome DevTools Protocol)

The CDP module provides access to Chrome DevTools Protocol commands for
browser-specific features not yet covered by the W3C BiDi standard. This
is useful for accessing Chrome-only capabilities like performance tracing,
coverage profiling, or service worker management.

!!! warning "Chrome/Edge only"
    CDP commands are only supported by Chrome and Edge (Chromium-based
    browsers). Firefox does not support CDP.

## When to use CDP

- **Performance tracing** — `Performance.startTracing`, `stopTracing`
- **Coverage profiling** — `CSS.startRuleUsageTracking`, `stopRuleUsageTracking`
- **Service worker control** — `ServiceWorker.enable`, `unregister`
- **Heap snapshots** — `HeapProfiler.takeHeapSnapshot`
- **Chrome-specific APIs** — any CDP domain not in the BiDi spec

## Send a CDP command

Send a raw CDP command and receive the response:

```python
result = await client.cdp.send_command(
    method="Performance.getMetrics",
    params={},
)
print(result.result)  # CDP response data
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `method` | `str` | (required) | CDP method name (e.g., `"Page.reload"`) |
| `params` | `dict \| None` | `None` | CDP command parameters |

Returns a `CDPResult` with:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `result` | `dict` | CDP response data |
| `session` | `str \| None` | CDP session ID (if applicable) |

## Get CDP session

Get the current CDP session ID for a specific browsing context:

```python
session = await client.cdp.get_session(context="context-id-1")
print(session.session)  # CDP session ID
```

This is useful when you need to target a specific context's CDP session
(e.g., for iframe-specific commands).

## Examples

### Get performance metrics

```python
# Enable Performance domain
await client.cdp.send_command(method="Performance.enable", params={})

# Get metrics
metrics = await client.cdp.send_command(method="Performance.getMetrics", params={})
for metric in metrics.result["metrics"]:
    print(f"{metric['name']}: {metric['value']}")
```

### Take a heap snapshot

```python
await client.cdp.send_command(method="HeapProfiler.enable", params={})
await client.cdp.send_command(
    method="HeapProfiler.takeHeapSnapshot",
    params={"reportProgress": False},
)
```

### Control service workers

```python
# Enable ServiceWorker domain
await client.cdp.send_command(method="ServiceWorker.enable", params={})

# Unregister all service workers
registrations = await client.cdp.send_command(
    method="ServiceWorker.getRegistrations",
    params={},
)
for reg in registrations.result["registrations"]:
    await client.cdp.send_command(
        method="ServiceWorker.unregister",
        params={"scope": reg["scopeURL"]},
    )
```

## Combining BiDi and CDP

You can mix BiDi commands and CDP commands freely:

```python
async with await client.browsing.open("https://example.com") as page:
    # BiDi: evaluate JavaScript
    title = await page.evaluate("document.title")

    # CDP: get performance metrics
    await client.cdp.send_command(method="Performance.enable", params={})
    metrics = await client.cdp.send_command(method="Performance.getMetrics", params={})

    # BiDi: take a screenshot
    screenshot = await page.screenshot()
```

## API reference

See [CDP API](../api/cdp.md) for the complete `CDPModule` reference.
