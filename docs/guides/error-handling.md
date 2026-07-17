# Error handling guide — bidiwave

## Exception hierarchy

```text
BiDiError (base)
├── BiDiConnectionError      # WebSocket disconnected or unreachable
├── BiDiTimeoutError         # Timeout waiting for response or navigation
├── CapabilityError          # Browser does not support the capability
├── ProtocolError            # Invalid or unexpected protocol message
├── SessionError             # Invalid or expired session
└── CommandError             # Browser rejected the command
    ├── InvalidArgumentError # Invalid argument
    ├── NoSuchFrameError     # Context not found
    └── JavaScriptError      # Error evaluating JS
```

## Errors by scenario

### Connection

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| Browser not responding | `BiDiConnectionError` | Browser not launched, wrong port | Verify the browser is running with `--remote-debugging-port` |
| WebSocket closed | `BiDiConnectionError` | Browser crashed or was closed | Automatic reconnect, or reconnect manually |
| Timeout on connect | `BiDiTimeoutError` | Firewall, slow network | Increase `timeout` in `BiDiClient.connect()` |

### Session

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| `session.new` fails | `SessionError` | Unsupported capabilities | Verify `alwaysMatch` in capabilities |
| Session expired | `SessionError` | Session closed by the browser | Create a new session |
| `session.subscribe` fails | `CommandError` | Unsupported event type | Verify `client.capabilities` |

### Navigation

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| Invalid URL | `CommandError` | Malformed URL | Validate URL before navigating |
| Load timeout | `BiDiTimeoutError` | Slow or hanging page | Use `wait="none"` or `wait="interactive"`, or increase timeout |
| Context closed | `CommandError` | Context was closed by another process | Verify the context exists before navigating |
| Screenshot fails | `CommandError` | Context not visible (headless without GPU) | Use `--headless=new` in Chrome |

### Script

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| JS error | `CommandError` | Invalid expression | Catch errors in JS: `try { ... } catch(e) { return e.message }` |
| Promise not resolved | `BiDiTimeoutError` | `await_promise=True` and Promise hung | Use timeout in JS: `Promise.race([promise, timeout(5000)])` |
| Invalid handle | `CommandError` | Handle already released or context closed | Don't reuse handles after `disown()` or `close()` |

### Events

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| Handler fails | (silent) | Exception in async handler | The handler runs in error isolation. Log errors inside the handler |
| No events received | (silent) | Not subscribed or context closed | Verify `session.subscribe()` and that the context is active |

### Reconnection

| Scenario | Exception | Common cause | Solution |
|---|---|---|---|
| Reconnect fails | `BiDiConnectionError` | Browser closed | Handle `on_reconnect` failure, relaunch browser |
| Session lost after reconnect | `SessionError` | BiDi session does not survive reconnection | Create new session in `on_reconnect` handler |
| Duplicate handlers after reconnect | (silent) | Re-registering handlers on each reconnect | Handlers are kept in memory, no need to re-register |

## Error handling patterns

### Retry with backoff

```python
async def navigate_with_retry(client, ctx, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.browsing.navigate(ctx, url, wait="complete")
        except BiDiTimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Context-safe operations

```python
async def safe_navigate(client, ctx, url):
    try:
        return await client.browsing.navigate(ctx, url, wait="complete")
    except CommandError as e:
        if "no such frame" in e.message.lower():
            ctx = await client.browsing.create_context()
            return await client.browsing.navigate(ctx, url, wait="complete")
        raise
```

### Capability guard

```python
async def safe_screenshot(client, ctx):
    if not client.capabilities.supports_browsing:
        raise CapabilityError("Browser does not support browsing.captureScreenshot")
    return await client.browsing.screenshot(ctx)
```

### Promise with timeout in JS

```python
result = await client.script.evaluate(
    ctx,
    """new Promise((resolve, reject) => {
        setTimeout(() => resolve('done'), 1000);
        setTimeout(() => reject(new Error('timeout')), 5000);
    })""",
    await_promise=True,
)
```

## Logging

bidiwave uses Python's standard `logging` module. Configure to see messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("bidiwave").setLevel(logging.DEBUG)
```

Levels:

- `DEBUG` — all messages sent/received, ID correlation
- `INFO` — connections, reconnections, subscriptions
- `WARNING` — events dropped (backpressure), failed handlers
- `ERROR` — protocol errors, rejected commands
