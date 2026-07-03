# Storage

::: bidiwave.modules.storage.StorageModule

## Cookie model

::: bidiwave.protocol.results.Cookie

## Get cookies

```python
cookies = await client.storage.get_cookies(context)
for cookie in cookies:
    print(f"{cookie.name}={cookie.value} (domain={cookie.domain})")
```

## Set cookie

```python
from bidiwave import Cookie

await client.storage.set_cookie(
    context,
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
await client.storage.delete_cookies(context)

# Delete a specific cookie by name
await client.storage.delete_cookies(context, name="session")

# Delete cookies by domain
await client.storage.delete_cookies(context, domain="example.com")

# Delete cookies by name, domain, and path
await client.storage.delete_cookies(
    context,
    name="session",
    domain="example.com",
    path="/app",
)
```

## Delete a single cookie

```python
# Delete one cookie by name (targeted, no filter)
await client.storage.delete_cookie(context, "session")
```
