# Cookies & Storage

## Get cookies

```python
cookies = await client.storage.get_cookies(ctx)
for cookie in cookies:
    print(f"{cookie.name}={cookie.value} (domain={cookie.domain})")
```

## Set a cookie

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
        expires=1735689600,
    ),
)
```

## Delete cookies

```python
# Delete all cookies
await client.storage.delete_cookies(ctx)

# Delete a specific cookie by name
await client.storage.delete_cookies(ctx, name="session")

# Delete cookies by domain and path
await client.storage.delete_cookies(ctx, domain="example.com", path="/app")
```

## Cookie fields

| Field | Type | Default |
|---|---|---|
| `name` | `str` | required |
| `value` | `str` | required |
| `domain` | `str \| None` | `None` |
| `path` | `str` | `"/"` |
| `http_only` | `bool` | `False` |
| `secure` | `bool` | `False` |
| `same_site` | `str \| None` | `None` |
| `expires` | `int \| None` | `None` |
