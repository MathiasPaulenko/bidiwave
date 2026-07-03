# Script

The script module lets you execute JavaScript in a browsing context. There
are two ways to run code: `evaluate` (run an expression) and `call_function`
(run a function with arguments). Both return a `RemoteValue` — a typed
wrapper around the JavaScript value.

## evaluate

`evaluate` runs a JavaScript expression in the page's main realm and
returns the result as a `RemoteValue`:

```python
result = await client.script.evaluate(ctx, "document.title")
```

### Pattern matching with RemoteValue

The protocol serializes JavaScript values into JSON with a `type` field.
bidiwave parses this into specific Python classes. Use `match` for
type-safe narrowing:

```python
from bidiwave import StringValue, NumberValue, NullValue

result = await client.script.evaluate(ctx, "document.title")
match result:
    case StringValue(value=title):
        print(f"Title: {title}")
    case NullValue():
        print("No title")
    case _:
        print(f"Unexpected type: {result.type}")
```

### Awaiting Promises

By default, `evaluate` returns immediately even if the expression returns a
`Promise`. Set `await_promise=True` to wait for the Promise to resolve:

```python
result = await client.script.evaluate(
    ctx,
    "new Promise(r => setTimeout(() => r('done'), 1000))",
    await_promise=True,
)
match result:
    case StringValue(value=text):
        print(f"Promise resolved: {text}")  # "done"
```

This is essential for waiting on `fetch()` calls, animations, or any
async JavaScript:

```python
result = await client.script.evaluate(
    ctx,
    "fetch('/api/data').then(r => r.json()).then(d => d.result)",
    await_promise=True,
)
```

### All RemoteValue types

| JS type | Python class | Key field | Example |
| ------- | ------------ | --------- | ------- |
| `"string"` | `StringValue` | `.value: str` | `"hello"` |
| `"number"` | `NumberValue` | `.value: int \| float` | `42`, `3.14` |
| `"boolean"` | `BooleanValue` | `.value: bool` | `true` |
| `"null"` | `NullValue` | (none) | `null` |
| `"undefined"` | `UndefinedValue` | (none) | `undefined` |
| `"bigint"` | `BigIntValue` | `.value: str` | `9007199254740993n` |
| `"object"` | `ObjectValue` | `.value: dict` | `{a: 1}` |
| `"array"` | `ArrayValue` | `.value: list` | `[1, 2, 3]` |
| `"function"` | `HandleValue` | `.handle: str` | `() => {}` |
| `"symbol"` | `HandleValue` | `.handle: str` | `Symbol()` |

### Working with objects and arrays

When JavaScript returns an object or array, bidiwave parses it into
`ObjectValue` or `ArrayValue`. Nested values are preserved as dicts and
lists:

```python
result = await client.script.evaluate(ctx, "({name: 'Alice', age: 30})")
match result:
    case ObjectValue(value=data):
        print(data["name"])  # "Alice"
        print(data["age"])   # 30
```

```python
result = await client.script.evaluate(ctx, "[1, 2, 3, 4, 5]")
match result:
    case ArrayValue(value=items):
        print(items)        # [1, 2, 3, 4, 5]
        print(sum(items))   # 15
```

### Handles and disown

When JavaScript returns a function, symbol, or an object with circular
references, the protocol returns a **handle** instead of the value. Handles
are string references to objects living in the browser. Use `disown` to
release them and free memory:

```python
result = await client.script.evaluate(ctx, "document.querySelector('button')")
match result:
    case ObjectValue(handle=h) if h:
        # h is a handle string like "element-1234"
        # Use it as an argument in call_function
        await client.script.call_function(
            ctx,
            "(el) => el.click()",
            args=[{"handle": h}],
        )
        # Release the handle when done
        await client.script.disown(ctx, handles=[h])
```

!!! warning "Memory leaks"
    Handles keep objects alive in the browser's memory. Always call
    `disown` when you're done with a handle to avoid memory leaks,
    especially in long-running scripts.

## call_function

`call_function` executes a JavaScript function with arguments. The
function declaration is a string (not an expression), and arguments are
passed as a list of BiDi value descriptors:

```python
result = await client.script.call_function(
    ctx,
    "(a, b) => a + b",
    args=[
        {"type": "number", "value": 2},
        {"type": "number", "value": 3},
    ],
)
match result:
    case NumberValue(value=n):
        print(f"2 + 3 = {n}")  # 5
```

### Argument format

Arguments are dictionaries with `type` and `value` keys:

| JS type | Argument format |
| ------- | --------------- |
| string | `{"type": "string", "value": "hello"}` |
| number | `{"type": "number", "value": 42}` |
| boolean | `{"type": "boolean", "value": true}` |
| null | `{"type": "null"}` |
| undefined | `{"type": "undefined"}` |
| handle | `{"handle": "handle-id"}` |

### Passing handles

Handles from `evaluate` can be passed to `call_function`:

```python
# Get a reference to an element
element = await client.script.evaluate(ctx, "document.querySelector('#btn')")
match element:
    case ObjectValue(handle=h) if h:
        # Pass the handle as an argument
        result = await client.script.call_function(
            ctx,
            "(el) => el.textContent",
            args=[{"handle": h}],
        )
        await client.script.disown(ctx, handles=[h])
```

!!! warning "ChromeDriver/EdgeDriver bug"
    Some versions of ChromeDriver and EdgeDriver have a bug where
    `callFunction` returns `NaN` when passed primitive number arguments.
    If you encounter this, use `evaluate` with an inline expression
    instead:

    ```python
    # Instead of call_function with args:
    result = await client.script.call_function(
        ctx, "(a, b) => a + b",
        args=[{"type": "number", "value": 2}, {"type": "number", "value": 3}],
    )

    # Use evaluate with inline values:
    result = await client.script.evaluate(ctx, "2 + 3")
    ```

## Preload scripts

Preload scripts run **before** the page's own scripts. They're useful for
injecting polyfills, overriding globals, or monitoring page behavior from
the very start.

### script.addPreloadScript (with channels)

Unlike `preload.addPreloadScript`, `script.addPreloadScript` supports
**channels** for bidirectional communication between the preload script
and the client via `script.message` events:

```python
result = await client.script.add_preload_script(
    function_declaration="(channel) => { channel('hello from page'); }",
    arguments=[{"type": "channel", "value": {"channel": "my-channel"}}],
    contexts=["context-id-1"],
)
print(result.script)  # preload script ID
print(result.channel) # channel name for communication
```

### Receiving messages from preload scripts

```python
async def on_message(event):
    print(f"Message from preload: {event.data}")

client.on("script.message", on_message)
await client.session.subscribe(["script.message"])
```

### preload.addPreloadScript (without channels)

For simpler use cases where you don't need bidirectional communication:

```python
result = await client.preload.add_preload_script(
    function_declaration="() => { window.myPolyfill = true; }",
    contexts=["context-id-1"],
)
# result.script = "preload-script-id"

# Remove when done
await client.preload.remove_preload_script(result.script)
```

### add_preload_script parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `function_declaration` | `str` | (required) | JS function to execute |
| `arguments` | `list[dict] \| None` | `None` | Arguments (supports channel type) |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope the script |
| `user_contexts` | `list[str] \| None` | `None` | User context IDs to scope |

## Realms

Realms are JavaScript execution environments. Each browsing context has
at least one realm (the main world). Iframes and service workers have
their own realms.

### Get all realms

```python
realms = await client.script.get_realms()
for realm in realms:
    print(f"Realm: {realm.realm} (type={realm.type}, context={realm.context})")
```

### Filter by context

```python
realms = await client.script.get_realms(context="context-id-1")
```

### Filter by realm type

```python
# Only main realms
realms = await client.script.get_realms(realm_type="window")

# Service worker realms
realms = await client.script.get_realms(realm_type="service-worker")
```

| Realm type | Description |
| ---------- | ----------- |
| `"window"` | Main page realm (one per browsing context) |
| `"dedicated-worker"` | Web Worker realm |
| `"shared-worker"` | SharedWorker realm |
| `"service-worker"` | Service Worker realm |
| `"worker"` | Generic worker realm |

## Script events

| Event | Fired when | Handler receives |
| ----- | ---------- | ---------------- |
| `script.realmCreated` | A new JavaScript realm is created | `ScriptRealmCreatedEvent` |
| `script.realmDestroyed` | A realm is destroyed (context closed, worker terminated) | `ScriptRealmDestroyedEvent` |
| `script.message` | A preload script sends a message via channel | `ScriptMessageEvent` |

```python
async def on_realm_created(event):
    print(f"Realm created: {event.realm} (type={event.type})")

async def on_realm_destroyed(event):
    print(f"Realm destroyed: {event.realm}")

client.on_realm_created(on_realm_created)
client.on_realm_destroyed(on_realm_destroyed)
await client.session.subscribe(["script.realmCreated", "script.realmDestroyed"])
```

## Page convenience methods

The `Page` object provides shortcuts for `evaluate` and `call_function`:

```python
async with await client.browsing.open("https://example.com") as page:
    # Same as client.script.evaluate(page._context, expr)
    result = await page.evaluate("document.title")

    # Same as client.script.call_function(page._context, fn, args)
    result = await page.call("(a, b) => a + b", args=[...])
```

## API reference

See [Script API](../api/script.md) for the complete `ScriptModule` reference,
[Preload API](../api/preload.md) for the `PreloadModule` reference,
and [RemoteValue API](../api/remote-value.md) for all `RemoteValue` subtypes.
