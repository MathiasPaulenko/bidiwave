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

## Cache overrides

Cache overrides let you serve cached responses without hitting the network.

### add / remove pattern

```python
# Add a cache override — returns a cache ID
cache = await client.network.add_cache_override(
    url="https://example.com/api",
    method="GET",
    status_code=200,
    body="eyJkYXRhIjogInRlc3QifQ==",
)
# cache.cache = "cache-id-1"

# Remove it later
await client.network.remove_cache_override(cache.cache)
```

### set pattern (replace all)

```python
# Replaces ALL existing cache overrides in a single call
await client.network.set_cache_override(
    url="https://example.com/api",
    method="GET",
    status_code=204,
)
```

## Response body

Retrieve the body of a completed response by request ID:

```python
result = await client.network.response_body("request-id-1")
print(result.body)        # base64-encoded content
print(result.total_size)  # size in bytes
```

## Authentication

Handle `network.authRequired` events:

```python
# Continue with credentials
await client.network.continue_with_auth(
    request=request_id,
    credentials={"type": "password", "username": "user", "password": "pass"},
)

# Cancel the auth challenge
await client.network.cancel_auth(request=request_id)
```
