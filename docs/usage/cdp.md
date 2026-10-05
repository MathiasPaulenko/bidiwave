# CDP (Chrome DevTools Protocol)

The CDP module provides access to Chrome DevTools Protocol commands for
browser-specific features not covered by the W3C BiDi standard. This
is useful for accessing Chrome-only capabilities like performance tracing,
coverage profiling, or service worker management.

!!! warning "Chrome/Edge only, not part of BiDi"
    `cdp.sendCommand`/`cdp.getSession` are Chromium driver extensions —
    they are **not** in the W3C BiDi spec and are not available on Firefox.

## When to use CDP

- **Performance tracing** — `Performance.startTracing`, `stopTracing`
- **Coverage profiling** — `CSS.startRuleUsageTracking`, `stopRuleUsageTracking`
- **Service worker control** — `ServiceWorker.enable`, `unregister`
- **Heap snapshots** — `HeapProfiler.takeHeapSnapshot`
- **Chrome-specific APIs** — any CDP domain not in the BiDi spec

## Send a CDP command

Send a raw CDP command and receive the response as a dict:

```python
result = await client.cdp.send_command("Performance.getMetrics")
print(result)  # raw CDP response dict
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `method` | `str` | (required) | CDP method name (e.g., `"Page.reload"`) |
| `params` | `dict \| None` | `None` | CDP command parameters |
| `session` | `str \| None` | `None` | CDP session ID to target (from `get_session`) |

Returns the raw command result as a `dict`.

## Get CDP session

Get the CDP session ID for a browsing context. The context is required:

```python
session_id = await client.cdp.get_session("context-id-1")
print(session_id)  # "cdp-session-id" or None
```

Pass the returned ID as the `session` argument of `send_command` to
target that context's CDP session.

## Examples

### Get performance metrics

```python
# Enable Performance domain
await client.cdp.send_command("Performance.enable")

# Get metrics
metrics = await client.cdp.send_command("Performance.getMetrics")
for metric in metrics["metrics"]:
    print(f"{metric['name']}: {metric['value']}")
```

### Take a heap snapshot

```python
await client.cdp.send_command("HeapProfiler.enable")
await client.cdp.send_command(
    "HeapProfiler.takeHeapSnapshot",
    {"reportProgress": False},
)
```

### Control service workers

```python
# Enable ServiceWorker domain
await client.cdp.send_command("ServiceWorker.enable")

# Unregister all service workers
registrations = await client.cdp.send_command("ServiceWorker.getRegistrations")
for reg in registrations["registrations"]:
    await client.cdp.send_command(
        "ServiceWorker.unregister",
        {"scope": reg["scopeURL"]},
    )
```

## Combining BiDi and CDP

You can mix BiDi commands and CDP commands freely:

```python
async with await client.browsing.open("https://example.com") as page:
    # BiDi: evaluate JavaScript
    title = await page.evaluate("document.title")

    # CDP: get performance metrics
    await client.cdp.send_command("Performance.enable")
    metrics = await client.cdp.send_command("Performance.getMetrics")

    # BiDi: take a screenshot
    screenshot = await page.screenshot()
```

## API reference

See [CDP API](../api/cdp.md) for the complete `CDPModule` reference.
