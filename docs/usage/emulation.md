# Emulation

The emulation module lets you override browser settings to simulate
different devices, locations, network conditions, and time zones. This is
essential for testing how pages behave under various conditions without
needing physical devices.

## Geolocation override

Simulate a specific geographic location:

```python
await client.emulation.set_geolocation(
    coordinates={
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 1.0,
    },
    contexts=["context-id-1"],  # optional: scope to specific contexts
)
```

To simulate a geolocation error instead of coordinates:

```python
await client.emulation.set_geolocation(
    error={"type": "positionUnavailable"},
)
```

Clear the override (sends `coordinates: null` per spec):

```python
await client.emulation.set_geolocation()
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `coordinates` | `dict \| None` | `None` | `{"latitude": float, "longitude": float, "accuracy": float}`. `None` clears the override. |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. `None` = all contexts. |
| `user_contexts` | `list[str] \| None` | `None` | User context IDs to scope. |
| `error` | `dict \| None` | `None` | Error to simulate, e.g. `{"type": "positionUnavailable"}`. Mutually exclusive with `coordinates`. |

### Use cases

- Test location-based features (store finders, local content)
- Verify geo-restricted content behavior
- Test GPS-dependent JavaScript APIs

## Network conditions

Per the W3C spec, the only supported network condition is **offline
emulation** — throughput and latency throttling are not part of
`emulation.setNetworkConditions`.

```python
# Simulate offline mode
await client.emulation.set_network_conditions(offline=True, contexts=["context-id-1"])

# Restore normal connectivity (sends networkConditions: null)
await client.emulation.set_network_conditions(offline=False)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `offline` | `bool` | `True` | `True` simulates offline, `False` clears the override |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. |
| `user_contexts` | `list[str] \| None` | `None` | User context IDs to scope. |

## Time zone override

Simulate a different time zone:

```python
await client.emulation.set_timezone(
    "America/New_York",
    contexts=["context-id-1"],
)
```

Clear the override (sends `timezone: null`):

```python
await client.emulation.set_timezone(None)
```

### Common timezones

| Timezone | UTC offset |
| -------- | ---------- |
| `"UTC"` | UTC+0 |
| `"America/New_York"` | UTC-5/-4 |
| `"America/Los_Angeles"` | UTC-8/-7 |
| `"Europe/London"` | UTC+0/+1 |
| `"Europe/Berlin"` | UTC+1/+2 |
| `"Asia/Tokyo"` | UTC+9 |
| `"Australia/Sydney"` | UTC+10/+11 |

```python
# Test date/time display
await client.emulation.set_timezone("Asia/Tokyo")
result = await page.evaluate("new Date().toLocaleString()")
# Result will show Tokyo time
```

## User agent override

Override the browser's User-Agent string. Per spec, only the UA string
itself can be overridden:

```python
await client.emulation.set_user_agent(
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    contexts=["context-id-1"],
)
```

Clear the override (sends `userAgent: null`):

```python
await client.emulation.set_user_agent(None)
```

### Use cases

- Test responsive designs that check User-Agent
- Verify server-side content negotiation
- Simulate mobile or tablet browsers

## Locale and screen orientation

```python
# Override locale (None clears)
await client.emulation.set_locale("fr-FR", contexts=["context-id-1"])

# Override screen orientation (None clears)
await client.emulation.set_screen_orientation(
    {"type": "portrait-primary", "natural": "portrait"},
    contexts=["context-id-1"],
)
```

## Combining overrides

You can combine multiple emulation overrides to simulate a complete device:

```python
async with await client.browsing.open("https://example.com") as page:
    ctx = page.id

    # Simulate an iPhone in Tokyo, offline
    await client.emulation.set_geolocation(
        coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
        contexts=[ctx],
    )
    await client.emulation.set_network_conditions(offline=True, contexts=[ctx])
    await client.emulation.set_timezone("Asia/Tokyo", contexts=[ctx])
    await client.emulation.set_user_agent(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        contexts=[ctx],
    )

    # Now test the page under these conditions
    result = await page.evaluate("navigator.userAgent")
    # ... run tests ...
```

## API reference

See [Emulation API](../api/emulation.md) for the complete `EmulationModule`
reference.
