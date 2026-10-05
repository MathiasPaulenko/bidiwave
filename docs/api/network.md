# Network

::: bidiwave.modules.network.NetworkModule

## Events

Subscribe to network events via `client.session.subscribe()` — handlers
must be `async`:

```python
await client.session.subscribe(["network.beforeRequestSent", "network.responseCompleted"])

async def on_req(req): print(f"→ {req.request.url}")
async def on_res(res): print(f"← {res.response.status} {res.request.url}")
async def on_err(err): print(f"✗ {err.request.url}: {err.error_text}")

client.on_request(on_req)
client.on_response(on_res)
client.on_fetch_error(on_err)
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
await client.network.remove_intercept(intercept.intercept)
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

## Authentication

Handle `network.authRequired` events:

```python
# Continue with credentials
await client.network.continue_with_auth(
    request=request_id,
    action="provideCredentials",
    credentials={"type": "password", "username": "user", "password": "pass"},
)

# Cancel the auth challenge (continueWithAuth action="cancel")
await client.network.cancel_auth(request=request_id)
```

## Cache behavior

Control browser cache behavior for specific contexts:

```python
# Bypass the cache
await client.network.set_cache_behavior(
    cache_behavior="bypass",
    contexts=["context-id-1"],
)

# Restore normal caching
await client.network.set_cache_behavior(cache_behavior="default")
```

## Extra headers

Add, modify, or remove HTTP headers for outgoing requests:

```python
await client.network.set_extra_headers(
    headers=[{"name": "X-Custom-Header", "value": "my-value"}],
    contexts=["context-id-1"],
)
```

## Data collectors

Collect response bodies for later retrieval:

```python
# Start collecting responses (before the requests happen)
collector_id = await client.network.add_data_collector(
    data_types=["response"],
    max_encoded_data_size=1_000_000,
    contexts=["context-id-1"],
)

# Retrieve collected data for a request
data = await client.network.get_data("request-id-1", data_type="response")
body = data["bytes"]["value"]  # base64-encoded content

# Disown the collected data
await client.network.disown_data(collector_id, "request-id-1", data_type="response")

# Remove the data collector
await client.network.remove_data_collector(collector_id)
```
