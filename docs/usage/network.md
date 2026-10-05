# Network Interception

The network module lets you **monitor** and **intercept** HTTP requests
and responses. Monitoring is passive — you see what's happening. Interception
is active — you can block, modify, or mock requests before they reach the
server.

## Monitoring requests

To watch network traffic without modifying it, subscribe to network events:

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

### Event data

Each network event contains rich data about the request or response:

**`NetworkBeforeRequestSentEvent`**:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `context` | `str \| None` | Browsing context ID |
| `request` | `NetworkRequestData` | Request details (URL, method, headers, cookies) |
| `is_blocked` | `bool` | Whether the request is blocked by an intercept |
| `intercepts` | `list[str]` | Intercept IDs that matched this request |
| `navigation` | `str \| None` | Navigation ID if triggered by navigation |

**`NetworkResponseCompletedEvent`**:

| Field | Type | Description |
| ----- | ---- | ----------- |
| `context` | `str \| None` | Browsing context ID |
| `request` | `NetworkRequestData` | Original request details |
| `response` | `NetworkResponseData` | Response details (status, headers, MIME) |

## Interception

Interception lets you pause requests at specific phases and decide what
happens to them — block, modify, or let them through.

### How interception works

1. **Register an intercept** with `add_intercept()`, specifying which
   phases and URL patterns to match.
2. **Subscribe to `network.beforeRequestSent`** (or `responseStarted`) to
   receive events about intercepted requests.
3. **In your event handler**, call one of:
   - `continue_request()` — let the request proceed (optionally modified)
   - `fail_request()` — block the request with an error
   - `provide_response()` — return a synthetic response without hitting the server
4. **Remove the intercept** with `remove_intercept()` when done.

### Intercept phases

The BiDi protocol defines three interception phases:

| Phase | When it fires | What you can do |
| ----- | ------------- | --------------- |
| `beforeRequestSent` | Before the request leaves the browser | Block, modify URL/method/headers, provide synthetic response |
| `responseStarted` | When response headers arrive (body not yet received) | Modify response status/headers/body |
| `authRequired` | When the server requires authentication | Provide credentials or cancel |

### URL patterns

URL patterns use glob-style matching:

- `"*"` — match all URLs
- `"*example.com*"` — match any URL containing `example.com`
- `"https://api.example.com/*"` — match a specific path prefix

## Blocking requests

Block all requests matching a URL pattern:

```python
# Register an intercept
intercept = await client.network.add_intercept(
    phases=["beforeRequestSent"],
    url_patterns=["*ads.example.com*", "*doubleclick.net*"],
)

# In the event handler, fail the request
async def on_request(event):
    if event.is_blocked and event.intercepts:
        await client.network.fail_request(
            request=event.request.request,
        )

client.on_request(on_request)
await client.session.subscribe(["network.beforeRequestSent"])

# ... browse the page ...

# Clean up when done
await client.network.remove_intercept(intercept.intercept)
```

### add_intercept parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `phases` | `list[str]` | (required) | Phases to intercept: `"beforeRequestSent"`, `"responseStarted"`, `"authRequired"` |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope the intercept. `None` = all contexts |
| `url_patterns` | `list[str] \| None` | `None` | URL patterns to match. `None` = all URLs |

Returns an `InterceptResult` with `.intercept` (the intercept ID).

## Modifying requests

Continue an intercepted request with modified parameters:

```python
async def on_request(event):
    if event.is_blocked and event.intercepts:
        await client.network.continue_request(
            request=event.request.request,
            url="https://modified.example.com",  # change the URL
            method="POST",                       # change the method
            headers=[                            # add/replace headers
                {"name": "X-Custom", "value": "bidiwave"},
                {"name": "Authorization", "value": "Bearer token123"},
            ],
        )

client.on_request(on_request)
await client.session.subscribe(["network.beforeRequestSent"])
```

### continue_request parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `request` | `str` | (required) | Request ID from the event |
| `url` | `str \| None` | `None` | Modified URL |
| `method` | `str \| None` | `None` | Modified HTTP method |
| `headers` | `list[dict] \| None` | `None` | Modified headers (`[{"name": "...", "value": "..."}]`) |
| `cookies` | `list[dict] \| None` | `None` | Modified cookies |
| `post_data` | `str \| None` | `None` | Modified request body, base64-encoded |

If a parameter is `None`, the original value is preserved.

## Providing synthetic responses

Return a fake response without making the actual request:

```python
import base64

async def on_request(event):
    if event.is_blocked and "api.example.com" in event.request.url:
        body = base64.b64encode(b'{"message": "mocked response"}').decode()
        await client.network.provide_response(
            request=event.request.request,
            status_code=200,
            reason_phrase="OK",
            headers=[{"name": "Content-Type", "value": "application/json"}],
            body=body,
        )

client.on_request(on_request)
await client.session.subscribe(["network.beforeRequestSent"])
```

### provide_response parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `request` | `str` | (required) | Request ID from the event |
| `status_code` | `int` | `200` | HTTP status code |
| `reason_phrase` | `str` | `"OK"` | HTTP reason phrase |
| `headers` | `list[dict] \| None` | `None` | Response headers |
| `body` | `str \| None` | `None` | Response body as **base64-encoded** string |

!!! warning "Body encoding"
    The `body` parameter must be a **base64-encoded** string, not raw text.
    Use `base64.b64encode(your_bytes).decode()` to encode it.

## Modifying responses

Continue an intercepted response with modified status or headers (use
the `responseStarted` phase):

```python
intercept = await client.network.add_intercept(
    phases=["responseStarted"],
    url_patterns=["*example.com*"],
)

async def on_response_started(event):
    await client.network.continue_response(
        request=event.request.request,
        status_code=204,
        headers=[{"name": "Content-Type", "value": "application/json"}],
    )

await client.session.subscribe(["network.beforeRequestSent"])
```

### continue_response parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `request` | `str` | (required) | Request ID from the event |
| `status_code` | `int \| None` | `None` | Modified status code |
| `reason_phrase` | `str \| None` | `None` | Modified reason phrase |
| `headers` | `list[dict] \| None` | `None` | Modified headers |
| `cookies` | `list[dict] \| None` | `None` | Modified cookies |
| `credentials` | `dict \| None` | `None` | Auth credentials (`type`, `username`, `password`) |

Note: per the W3C BiDi spec, `continueResponse` does not accept a body.
Use `provide_response()` to supply a synthetic body.

## Failing requests

Block a request with an error:

```python
await client.network.fail_request(request=request_id)
```

The browser will receive a network error for this request.

## Removing intercepts

Always remove intercepts when you're done to stop blocking requests:

```python
await client.network.remove_intercept(intercept.intercept)
```

!!! warning "Forgetting to remove intercepts"
    If you forget to remove an intercept, all matching requests will remain
    blocked forever. Always clean up in a `finally` block or use `async with`.

## Cache behavior

Per the W3C spec, cache control is a single command —
`network.setCacheBehavior` — that either bypasses the HTTP cache or
restores normal behavior:

```python
# Bypass the cache for a context (always hit the network)
await client.network.set_cache_behavior("bypass", contexts=["context-id"])

# Restore normal caching
await client.network.set_cache_behavior("default")
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `cache_behavior` | `str` | (required) | `"bypass"` or `"default"` |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. `None` = all contexts |

## Response body via data collectors

The spec has no `responseBody` command — response bodies are collected
with **data collectors**. Register one before the requests happen, then
fetch the collected data for a request:

```python
import base64

# 1. Register a collector (before the requests happen)
collector = await client.network.add_data_collector(
    data_types=["response"],
    max_encoded_data_size=1_000_000,
)

# 2. Capture request IDs from network events
request_ids = []

async def on_response(event):
    request_ids.append(event.request.request)

client.on_response(on_response)
await client.session.subscribe(["network.responseCompleted"])

# ... browse the page ...

# 3. Retrieve the collected body for a request
data = await client.network.get_data(request_ids[0], data_type="response")
body = base64.b64decode(data["bytes"]["value"])
print(f"Content: {body[:200]}")

# Clean up
await client.network.remove_data_collector(collector)
```

| Method | Description |
| ------ | ----------- |
| `add_data_collector(data_types, max_encoded_data_size, collector_type=None, contexts=None, user_contexts=None)` | Registers a collector, returns its ID |
| `get_data(request, data_type="response", collector_id=None, disown=None)` | Fetches collected data — result contains a BytesValue under `bytes` |
| `disown_data(collector_id, request, data_type="response")` | Releases collected data |
| `remove_data_collector(collector_id)` | Removes the collector |

## Authentication

Handle `network.authRequired` events when the server requires authentication:

### Continue with credentials

```python
async def on_auth(event):
    await client.network.continue_with_auth(
        request=event.request.request,
        action="provideCredentials",
        credentials={
            "type": "password",
            "username": "user",
            "password": "pass",
        },
    )

client.on_auth_required(on_auth)
await client.session.subscribe(["network.authRequired"])
```

### Cancel auth challenge

```python
async def on_auth(event):
    # Cancel the auth challenge — request will fail
    await client.network.cancel_auth(request=event.request.request)

client.on_auth_required(on_auth)
await client.session.subscribe(["network.authRequired"])
```

### Auth parameters

| Method | Parameter | Type | Description |
| ------ | --------- | ---- | ----------- |
| `continue_with_auth` | `request` | `str` | Request ID from the event |
| `continue_with_auth` | `action` | `str` | `"default"`, `"cancel"` or `"provideCredentials"` |
| `continue_with_auth` | `credentials` | `dict \| None` | `{"type": "password", "username": "...", "password": "..."}` — required with `"provideCredentials"` |
| `cancel_auth` | `request` | `str` | Request ID from the event |

## Additional network events

Beyond `beforeRequestSent` and `responseCompleted`, the network module
supports these events:

| Event | Fired when | Handler receives |
| ----- | ---------- | ---------------- |
| `network.responseStarted` | Response headers arrive (body not yet received) | `NetworkResponseStartedEvent` |
| `network.fetchError` | Request failed with a network error | `NetworkFetchErrorEvent` |
| `network.authRequired` | Server requires authentication | `NetworkAuthRequiredEvent` |

```python
# Track fetch errors
async def on_error(event):
    print(f"Fetch error: {event.error_text} for {event.request.url}")

client.on("network.fetchError", on_error)
await client.session.subscribe(["network.fetchError"])
```

## API reference

See [Network API](../api/network.md) for the complete `NetworkModule`
reference.
