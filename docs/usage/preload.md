# Preload Scripts

Preload scripts run **before** the page's own JavaScript. They're useful
for injecting polyfills, overriding globals, monitoring page behavior,
or setting up test fixtures — all before the page's `DOMContentLoaded`
event.

Under the hood everything goes through `script.addPreloadScript` —
`client.preload` is just a convenience namespace with a shorter API.
For `arguments` (channels) or `sandbox` support, call
`client.script.add_preload_script` directly (see
[Script](script.md#preload-scripts)).

## When to use preload scripts

- **Polyfills** — inject `Promise.allSettled`, `structuredClone`, etc.
  before the page runs
- **Monitoring** — intercept `console.log`, `fetch`, `XMLHttpRequest` from
  the very start
- **Testing** — mock globals like `Date`, `Math.random`, `crypto`
- **Security** — override `eval`, `Function` constructor, or other
  dangerous APIs

## Add a preload script

```python
script_id = await client.preload.add_script(
    "() => { window.__testMode = true; }",
    contexts=["context-id-1"],
)
print(script_id)  # preload script ID, e.g., "preload-1234"
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `function_declaration` | `str` | (required) | JavaScript function to execute |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope the script |
| `user_contexts` | `list[str] \| None` | `None` | User context IDs to scope |

The `function_declaration` must be a **function** (not an expression).
It will be called automatically when a new document is created in the
matching contexts.

## Remove a preload script

```python
await client.preload.remove_script(script_id)
```

Always remove preload scripts when done to avoid affecting subsequent
page loads.

## Examples

### Inject a console logger

```python
script_id = await client.preload.add_script(
    """() => {
        const origLog = console.log;
        window.__logs = [];
        console.log = function(...args) {
            window.__logs.push(args.join(' '));
            origLog.apply(console, args);
        };
    }""",
    contexts=[ctx],
)

# After page loads, collect logs
async with await client.browsing.open("https://example.com") as page:
    logs = await page.evaluate("window.__logs")
    # ... process logs ...

await client.preload.remove_script(script_id)
```

### Mock `Date.now()`

```python
script_id = await client.preload.add_script(
    """() => {
        const fixedTime = 1700000000000;
        Date.now = () => fixedTime;
        Date.prototype.getTime = () => fixedTime;
    }""",
    contexts=[ctx],
)
```

### Intercept `fetch` calls

```python
script_id = await client.preload.add_script(
    """() => {
        const origFetch = window.fetch;
        window.__fetchCalls = [];
        window.fetch = function(...args) {
            window.__fetchCalls.push({url: args[0], time: Date.now()});
            return origFetch.apply(window, args);
        };
    }""",
    contexts=[ctx],
)
```

## Preload vs script.addPreloadScript

| Feature | `client.preload` | `client.script` |
| ------- | ---------------- | --------------- |
| Channels / arguments | No | Yes — `arguments` with `ChannelValue` |
| Sandbox | No | Yes — `sandbox` parameter |
| Scope | Contexts or user contexts | Contexts or user contexts |
| Message events | No | `script.message` events |
| Use case | Simple injection | Interactive communication |

For channel-based communication, see
[Script > Preload scripts](script.md#preload-scripts).

## API reference

See [Preload API](../api/preload.md) for the complete `PreloadModule`
reference.
