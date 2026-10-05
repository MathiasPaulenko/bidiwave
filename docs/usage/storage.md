# Cookies & Storage

The storage module manages browser cookies — the small key-value pairs
that websites use for session tracking, authentication, and preferences.
With bidiwave you can read, create, and delete cookies in any browsing
context.

## How cookies work in BiDi

Cookie commands take an optional `filter` (CookieFilter) and `partition`
(PartitionDescriptor). Passing a browsing context scopes the operation
via a `{"type": "context", "context": id}` partition — that's what the
`context` argument of these methods does for you. Cookies are shared
across contexts that belong to the same user profile.

## Get cookies

Retrieve all cookies for a browsing context:

```python
cookies = await client.storage.get_cookies(ctx)
for cookie in cookies:
    print(f"{cookie.name}={cookie.value} (domain={cookie.domain})")
```

Returns a `list[Cookie]`. Each `Cookie` has the fields described in the
table below.

### Filtering by context

Since cookies are scoped to a context, you'll typically pass the context
you're working with:

```python
async with await client.browsing.open("https://example.com") as page:
    cookies = await client.storage.get_cookies(page.id)
    session_cookie = next(
        (c for c in cookies if c.name == "session"),
        None,
    )
    if session_cookie:
        print(f"Session token: {session_cookie.value}")
```

### Filter and partition

```python
# Filter by name/domain (sent as the spec's CookieFilter)
cookies = await client.storage.get_cookies(filter={"name": "session"})

# Scope to a partition directly (e.g. a user context partition)
cookies = await client.storage.get_cookies(
    partition={"type": "storageKey", "userContext": "uc-1"}
)
```

## Set a cookie

Create or update a cookie:

```python
from bidiwave import Cookie

await client.storage.set_cookie(
    ctx,
    cookie=Cookie(
        name="session",
        value="abc123",
        domain="example.com",
        path="/",
        http_only=True,
        secure=True,
        same_site="Strict",
        expires=1735689600,  # Unix timestamp (seconds)
    ),
)
```

If a cookie with the same name, domain, and path already exists, it's
overwritten. Otherwise, a new cookie is created.

### Cookie fields

| Field | Type | Default | Description |
| ----- | ---- | ------- | ----------- |
| `name` | `str` | (required) | Cookie name |
| `value` | `str` | (required) | Cookie value |
| `domain` | `str \| None` | `None` | Domain the cookie applies to |
| `path` | `str` | `"/"` | URL path the cookie applies to |
| `http_only` | `bool` | `False` | If `True`, the cookie is not accessible via JavaScript (`document.cookie`) |
| `secure` | `bool` | `False` | If `True`, the cookie is only sent over HTTPS |
| `same_site` | `str \| None` | `None` | Cross-site policy: `"strict"`, `"lax"`, or `"none"` |
| `expires` | `int \| None` | `None` | Expiration as Unix timestamp (seconds, sent as `expiry`). `None` = session cookie |
| `priority` | `str \| None` | `None` | Cookie priority reported by the browser |
| `same_party` | `bool \| None` | `None` | SameParty attribute |
| `source_scheme` | `str \| None` | `None` | Scheme the cookie was set over |
| `source_port` | `int \| None` | `None` | Port the cookie was set over |

### Common patterns

**Session cookie** (deleted when browser closes):

```python
Cookie(name="session", value="token123", domain="example.com")
```

**Persistent secure cookie**:

```python
Cookie(
    name="preferences",
    value="dark_mode",
    domain="example.com",
    secure=True,
    same_site="Lax",
    expires=1893456000,  # far future
)
```

**Authentication cookie** (not accessible via JS):

```python
Cookie(
    name="auth_token",
    value="jwt-eyJhbGci...",
    domain="api.example.com",
    http_only=True,
    secure=True,
    same_site="Strict",
)
```

## Delete cookies

Delete cookies with optional filters:

```python
# Delete ALL cookies in the context
await client.storage.delete_cookies(ctx)

# Delete a specific cookie by name
await client.storage.delete_cookies(ctx, name="session")

# Delete cookies matching domain and path
await client.storage.delete_cookies(ctx, domain="example.com", path="/app")
```

### Delete parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `context` | `BrowsingContext \| str` | (required) | Context to delete from |
| `name` | `str \| None` | `None` | Delete only cookies with this name |
| `domain` | `str \| None` | `None` | Delete only cookies matching this domain |
| `path` | `str \| None` | `None` | Delete only cookies matching this path |

When `name`, `domain`, and `path` are all `None`, **all cookies** in the
context are deleted.

## Delete a single cookie

For targeted deletion of one cookie by name, use `delete_cookie`:

```python
# Delete one specific cookie by name
await client.storage.delete_cookie(ctx, "session")
```

Unlike `delete_cookies` (which accepts filters for name, domain, and path),
`delete_cookie` is a simpler API that deletes exactly one cookie matching
the given name. Use `delete_cookies` when you need to filter by domain or
path, and `delete_cookie` for simple name-based deletion.

### delete_cookie parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `context` | `BrowsingContext \| str` | (required) | Context to delete from |
| `name` | `str` | (required) | Name of the cookie to delete |

## Use cases

### Session injection

Inject an authentication token without logging in through the UI:

```python
async with await client.browsing.open("https://example.com") as page:
    # Set the session cookie
    await client.storage.set_cookie(
        page.id,
        cookie=Cookie(
            name="session",
            value="pre-authenticated-token",
            domain="example.com",
            path="/",
            http_only=True,
            secure=True,
        ),
    )
    # Reload to apply the cookie
    await page.navigate("https://example.com/dashboard")
```

### Cookie extraction

Extract cookies for use in another context or external HTTP client:

```python
cookies = await client.storage.get_cookies(ctx)
cookie_header = "; ".join(f"{c.name}={c.value}" for c in cookies)
# Use cookie_header in requests, httpx, etc.
```

### Cleanup

Clear all cookies between tests:

```python
await client.storage.delete_cookies(ctx)
```

## API reference

See [Storage API](../api/storage.md) for the complete `StorageModule` and
`Cookie` reference.
