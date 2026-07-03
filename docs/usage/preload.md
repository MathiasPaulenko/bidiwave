# Preload Scripts

Preload scripts run **before** the page's own JavaScript. They're useful
for injecting polyfills, overriding globals, monitoring page behavior,
or setting up test fixtures — all before the page's `DOMContentLoaded`
event.

bidiwave provides two ways to add preload scripts:

1. **`preload.addPreloadScript`** — simple, no channels
2. **`script.addPreloadScript`** — supports channels for bidirectional
   communication (see [Script](script.md#preload-scripts) for details)

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
result = await client.preload.add_preload_script(
    function_declaration="() => { window.__testMode = true; }",
    contexts=["context-id-1"],
)
print(result.script)  # preload script ID, e.g., "preload-1234"
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
await client.preload.remove_preload_script(result.script)
```

Always remove preload scripts when done to avoid affecting subsequent
page loads.

## Examples

### Inject a console logger

```python
result = await client.preload.add_preload_script(
    function_declaration="""() => {
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

await client.preload.remove_preload_script(result.script)
```

### Mock `Date.now()`

```python
result = await client.preload.add_preload_script(
    function_declaration="""() => {
        const fixedTime = 1700000000000;
        Date.now = () => fixedTime;
        Date.prototype.getTime = () => fixedTime;
    }""",
    contexts=[ctx],
)
```

### Intercept `fetch` calls

```python
result = await client.preload.add_preload_script(
    function_declaration="""() => {
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

| Feature | `preload.addPreloadScript` | `script.addPreloadScript` |
| ------- | -------------------------- | ------------------------- |
| Channels | No | Yes — bidirectional communication |
| Scope | Contexts or user contexts | Contexts or user contexts |
| Message events | No | `script.message` events |
| Use case | Simple injection | Interactive communication |

For channel-based communication, see
[Script > Preload scripts](script.md#preload-scripts).

## API reference

See [Preload API](../api/preload.md) for the complete `PreloadModule`
reference.
