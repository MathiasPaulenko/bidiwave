# Emulation

The emulation module lets you override browser settings to simulate
different devices, locations, network conditions, and time zones. This is
essential for testing how pages behave under various conditions without
needing physical devices.

## Geolocation override

Simulate a specific geographic location:

```python
await client.emulation.set_geolocation_override(
    coordinates={
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 1.0,
    },
    contexts=["context-id-1"],  # optional: scope to specific contexts
)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `coordinates` | `dict \| None` | `None` | `{"latitude": float, "longitude": float, "accuracy": float}`. `None` clears the override. |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. `None` = all contexts. |

### Use cases

- Test location-based features (store finders, local content)
- Verify geo-restricted content behavior
- Test GPS-dependent JavaScript APIs

## Network conditions

Simulate slow or unreliable network conditions:

```python
await client.emulation.set_network_conditions(
    network_conditions={
        "offline": False,
        "download_throughput": 50000,   # 50 KB/s
        "upload_throughput": 20000,     # 20 KB/s
        "latency": 500,                 # 500ms latency
    },
    contexts=["context-id-1"],
)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `network_conditions` | `dict \| None` | `None` | Network constraints. `None` clears. |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. |

### Network condition fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `offline` | `bool` | Simulate being offline |
| `download_throughput` | `int` | Download speed in bytes/s. `-1` = unlimited. |
| `upload_throughput` | `int` | Upload speed in bytes/s. `-1` = unlimited. |
| `latency` | `int` | Latency in milliseconds |

### Preset conditions

```python
# 3G slow
await client.emulation.set_network_conditions(
    network_conditions={
        "offline": False,
        "download_throughput": 50000,
        "upload_throughput": 25000,
        "latency": 400,
    },
)

# Offline
await client.emulation.set_network_conditions(
    network_conditions={"offline": True, "download_throughput": -1, "upload_throughput": -1, "latency": 0},
)

# Reset to normal
await client.emulation.set_network_conditions(network_conditions=None)
```

## Time zone override

Simulate a different time zone:

```python
await client.emulation.set_timezone_override(
    timezone="America/New_York",
    contexts=["context-id-1"],
)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `timezone` | `str \| None` | `None` | IANA timezone ID (e.g., `"Europe/London"`). `None` clears. |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. |

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
await client.emulation.set_timezone_override(timezone="Asia/Tokyo")
result = await page.evaluate("new Date().toLocaleString()")
# Result will show Tokyo time
```

## User agent override

Override the browser's User-Agent string:

```python
await client.emulation.set_user_agent_override(
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    accept_language="ja-JP",
    contexts=["context-id-1"],
)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `user_agent` | `str \| None` | `None` | Custom User-Agent string. `None` clears. |
| `accept_language` | `str \| None` | `None` | Accept-Language header value. |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. |

### Use cases

- Test responsive designs that check User-Agent
- Verify server-side content negotiation
- Simulate mobile or tablet browsers

## Combining overrides

You can combine multiple emulation overrides to simulate a complete device:

```python
async with await client.browsing.open("https://example.com") as page:
    ctx = page.id

    # Simulate an iPhone in Tokyo on 3G
    await client.emulation.set_geolocation_override(
        coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
        contexts=[ctx],
    )
    await client.emulation.set_network_conditions(
        network_conditions={"offline": False, "download_throughput": 50000, "upload_throughput": 25000, "latency": 400},
        contexts=[ctx],
    )
    await client.emulation.set_timezone_override(timezone="Asia/Tokyo", contexts=[ctx])
    await client.emulation.set_user_agent_override(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        accept_language="ja-JP",
        contexts=[ctx],
    )

    # Now test the page under these conditions
    result = await page.evaluate("navigator.userAgent")
    # ... run tests ...
```

## API reference

See [Emulation API](../api/emulation.md) for the complete `EmulationModule`
reference.
