# Network

::: bidiwave.modules.network.NetworkModule

## Events

Subscribe to network events via `client.session.subscribe()`:

```python
await client.session.subscribe(["network.beforeRequestSent", "network.responseCompleted"])

client.on_request(lambda req: print(f"→ {req.request.url}"))
client.on_response(lambda res: print(f"← {res.response.status} {res.request.url}"))
client.on_fetch_error(lambda err: print(f"✗ {err.request.url}: {err.errorText}"))
```

## Interception

Block or modify requests in specific phases:

```python
# Block all requests to example.com
intercept = await client.network.add_intercept(
    phases=["beforeRequestSent"],
    url_patterns=["*example.com*"],
)

# Later, remove the intercept
await client.network.remove_intercept(intercept.intercept_id)
```

Provide a synthetic response without making the real request:

```python
await client.network.provide_response(
    request=request_id,
    status_code=200,
    reason_phrase="OK",
    body="eyJtZXNzYWdlIjogImhlbGxvIn0=",  # base64-encoded JSON
)
```
