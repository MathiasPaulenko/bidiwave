# Events

## Subscribe to events

```python
await client.session.subscribe(["log.entryAdded", "browsingContext.contextCreated"])
```

## Console logs

```python
async def on_log(entry):
    print(f"[{entry.level}] {entry.text}")

client.on("log.entryAdded", on_log)
await client.session.subscribe(["log.entryAdded"])
```

## Browsing context events

```python
def on_context_created(event):
    print(f"Context created: {event.context}")

def on_context_destroyed(event):
    print(f"Context destroyed: {event.context}")

client.on_context_created(on_context_created)
client.on_context_destroyed(on_context_destroyed)
```

## Network events

```python
async def on_request(event):
    print(f"→ {event.request.method} {event.request.url}")

async def on_response(event):
    print(f"← {event.response.status} {event.request.url}")

client.on_request(on_request)
client.on_response(on_response)
await client.session.subscribe([
    "network.beforeRequestSent",
    "network.responseCompleted",
])
```

## Unsubscribe

```python
await client.session.unsubscribe(["log.entryAdded"])
```

## Convenience handlers

`BiDiClient` provides shortcuts for common event types:

| Method | Event |
|---|---|
| `client.on("log.entryAdded", handler)` | Console logs |
| `client.on_context_created(handler)` | `browsingContext.contextCreated` |
| `client.on_context_destroyed(handler)` | `browsingContext.contextDestroyed` |
| `client.on_request(handler)` | `network.beforeRequestSent` |
| `client.on_response(handler)` | `network.responseCompleted` |
| `client.on_fetch_error(handler)` | `network.fetchError` |

## Connection lifecycle events

```python
async def on_reconnect():
    print("Reconnected!")
    await client.session.subscribe(["log.entryAdded"])

async def on_disconnect():
    print("Connection lost...")

client.on_reconnect(on_reconnect)
client.on_disconnect(on_disconnect)
```
