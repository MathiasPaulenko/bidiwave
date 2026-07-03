# Events

WebDriver BiDi's key advantage over classic WebDriver is **bidirectional
communication** — the browser pushes events to your script in real time over
the WebSocket. No polling, no refresh loops. You subscribe to event types,
register async handlers, and the browser calls them when things happen.

## How the event system works

```
Browser ──WebSocket──▶ bidiwave receive loop
                              │
                      EventDispatcher
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              handler 1   handler 2   handler 3
```

1. **You register a handler** with `client.on(event_type, handler)`.
2. **You subscribe** to the event type with
   `await client.session.subscribe([...])`. This tells the browser to start
   sending events of that type over the WebSocket.
3. **The browser pushes events** — bidiwave's receive loop reads them,
   parses them into typed Pydantic models, and dispatches them to all
   registered handlers.
4. **Error isolation**: if one handler raises an exception, it's logged
   but doesn't affect other handlers or the WebSocket connection.

### Handler requirements

Handlers must be **async functions** that accept a single argument — the
typed event model:

```python
async def on_log(entry):
    # entry is a LogEntryAddedEvent with .level, .text, .timestamp, .source
    print(f"[{entry.level}] {entry.text}")
```

## Subscribing and unsubscribing

### subscribe

Tell the browser to start sending events of specific types:

```python
# Subscribe to multiple event types at once
await client.session.subscribe([
    "log.entryAdded",
    "browsingContext.contextCreated",
    "network.beforeRequestSent",
])
```

You can also scope subscriptions to specific browsing contexts:

```python
await client.session.subscribe(
    ["log.entryAdded"],
    contexts=[ctx_id],  # only receive events from this context
)
```

### unsubscribe

Stop receiving events of a type:

```python
await client.session.unsubscribe(["log.entryAdded"])
```

!!! note "Subscribe before navigating"
    Always subscribe to events **before** navigating to a page. Otherwise
    you may miss events that fire during page load.

## Event types

### Console logs — `log.entryAdded`

Fired when the page calls `console.log()`, `console.warn()`, etc.

```python
async def on_log(entry):
    print(f"[{entry.level.upper()}] {entry.text}")

client.on("log.entryAdded", on_log)
await client.session.subscribe(["log.entryAdded"])
```

The handler receives a `LogEntryAddedEvent` with:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `level` | `"debug" \| "info" \| "warn" \| "error"` | Console level |
| `text` | `str` | The log message text |
| `timestamp` | `int` | Unix timestamp in ms |
| `source` | `dict` | Source info (realm, context) |
| `args` | `list[dict]` | Raw argument values |
| `type` | `str` | Usually `"console"` |

### Browsing context events

| Event | Fired when | Handler receives |
| ----- | ---------- | ---------------- |
| `browsingContext.contextCreated` | A new tab, window, or iframe is created | `BrowsingContextCreatedEvent` (`.context`, `.url`) |
| `browsingContext.contextDestroyed` | A context is closed | `BrowsingContextDestroyedEvent` (`.context`) |
| `browsingContext.navigationStarted` | Navigation begins | `BrowsingContextNavigatedEvent` (`.context`, `.url`, `.navigation`) |

```python
async def on_context_created(event):
    print(f"New context: {event.context} (URL: {event.url})")

async def on_context_destroyed(event):
    print(f"Context closed: {event.context}")

client.on("browsingContext.contextCreated", on_context_created)
client.on("browsingContext.contextDestroyed", on_context_destroyed)
await client.session.subscribe([
    "browsingContext.contextCreated",
    "browsingContext.contextDestroyed",
])
```

### Network events

| Event | Fired when | Handler receives |
| ----- | ---------- | ---------------- |
| `network.beforeRequestSent` | A request is about to be sent | `NetworkBeforeRequestSentEvent` (`.request`, `.is_blocked`, `.intercepts`) |
| `network.responseCompleted` | A response finishes loading | `NetworkResponseCompletedEvent` (`.request`, `.response`) |
| `network.fetchError` | A request fails | `NetworkFetchErrorEvent` (`.request`, `.error_text`) |

```python
async def on_request(event):
    print(f"→ {event.request.method} {event.request.url}")

async def on_response(event):
    print(f"← {event.response.status} {event.request.url}")

client.on("network.beforeRequestSent", on_request)
client.on("network.responseCompleted", on_response)
await client.session.subscribe([
    "network.beforeRequestSent",
    "network.responseCompleted",
])
```

The `NetworkRequestData` model has: `.request` (ID), `.url`, `.method`,
`.headers`, `.cookies`. The `NetworkResponseData` model has: `.url`,
`.status`, `.status_text`, `.headers`, `.mime_type`.

### Script events

| Event | Fired when |
| ----- | ---------- |
| `script.message` | A script sends a message via a BiDi channel |

## Convenience handlers

`BiDiClient` provides shortcuts for the most common event types so you
don't have to type the full event name:

| Method | Event type |
| ------ | ---------- |
| `client.on("log.entryAdded", h)` | Console logs |
| `client.on_log_entry(h)` | Console logs (async convenience) |
| `client.on_context_created(h)` | `browsingContext.contextCreated` |
| `client.on_context_destroyed(h)` | `browsingContext.contextDestroyed` |
| `client.on_request(h)` | `network.beforeRequestSent` |
| `client.on_response(h)` | `network.responseCompleted` |
| `client.on_fetch_error(h)` | `network.fetchError` |

## Unregistering handlers

Use `client.off(subscription)` to remove a handler:

```python
sub = client.on("log.entryAdded", on_log)
# ... later ...
client.off(sub)
```

The `Subscription` object returned by `on()` is a handle that identifies
the registration. Pass it to `off()` to stop receiving events in that
handler.

## Connection lifecycle events

bidiwave automatically reconnects when the WebSocket drops. You can
register handlers for connection-level events:

### on_reconnect

Fired after a successful reconnection. Use it to re-subscribe to events
(subscriptions don't survive a reconnect):

```python
async def on_reconnect(_):
    print("Reconnected! Re-subscribing...")
    await client.session.subscribe(["log.entryAdded"])

client.on_reconnect(on_reconnect)
```

### on_disconnect

Fired when the WebSocket closes (before reconnection attempts):

```python
async def on_disconnect(_):
    print("Connection lost. Attempting to reconnect...")

client.on_disconnect(on_disconnect)
```

### Reconnection behavior

When the WebSocket drops, bidiwave tries to reconnect with **exponential
backoff**:

1. Wait `retry_delay` seconds (default: 1.0s)
2. Try to connect
3. If it fails, wait `retry_delay * retry_backoff` seconds
4. Repeat up to `max_retries` times (default: 3)

After a successful reconnect, all `on_reconnect` handlers are called.
Commands that were in-flight when the connection dropped are rejected with
`ConnectionError`.

See [Configuration](configuration.md) for tuning these parameters.

## API reference

See [Events API](../api/events.md) for the `EventDispatcher` and event model
reference.
