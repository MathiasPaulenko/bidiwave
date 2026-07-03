# Network Interception

## Monitor requests

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

## Block requests

```python
intercept = await client.network.add_intercept(
    phases=["beforeRequestSent"],
    url_patterns=["*ads.example.com*", "*doubleclick.net*"],
)

# ... browse the page ...

await client.network.remove_intercept(intercept.intercept_id)
```

## Continue with modifications

```python
await client.network.continue_request(
    request=request_id,
    url="https://modified.example.com",
    method="POST",
    headers=[{"name": "X-Custom", "value": "bidiwave"}],
)
```

## Fail a request

```python
await client.network.fail_request(request=request_id, error="Blocked by bidiwave")
```

## Provide a synthetic response

```python
import base64

body = base64.b64encode(b'{"message": "mocked"}').decode()

await client.network.provide_response(
    request=request_id,
    status_code=200,
    reason_phrase="OK",
    body=body,
)
```

## Continue a response

```python
await client.network.continue_response(
    request=request_id,
    status_code=204,
    headers=[{"name": "Content-Type", "value": "application/json"}],
)
```

## Intercept phases

| Phase | Description |
|---|---|
| `beforeRequestSent` | Before the request is sent |
| `responseStarted` | When response headers arrive |
| `authRequired` | When authentication is required |
