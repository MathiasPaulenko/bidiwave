# Permissions

The permissions module lets you grant or deny browser permissions
(geolocation, notifications, camera, microphone, etc.) without user
interaction. This is essential for automated testing of features that
normally require user consent dialogs.

## Set permission

Grant or deny a specific permission for a browsing context:

```python
# Grant geolocation permission
await client.permissions.set_permission(
    descriptor={"name": "geolocation"},
    state="granted",
    contexts=["context-id-1"],
)

# Deny camera access
await client.permissions.set_permission(
    descriptor={"name": "camera"},
    state="denied",
    contexts=["context-id-1"],
)

# Prompt the user (default behavior)
await client.permissions.set_permission(
    descriptor={"name": "notifications"},
    state="prompt",
    contexts=["context-id-1"],
)
```

### Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `descriptor` | `dict` | (required) | Permission descriptor with `name` field |
| `state` | `str` | (required) | `"granted"`, `"denied"`, or `"prompt"` |
| `contexts` | `list[str] \| None` | `None` | Context IDs to scope. `None` = all contexts. |

### Permission states

| State | Behavior |
| ----- | -------- |
| `"granted"` | Permission is automatically granted — no user dialog |
| `"denied"` | Permission is automatically denied — no user dialog |
| `"prompt"` | Normal behavior — browser shows the user consent dialog |

### Supported permissions

| Permission name | Description |
| --------------- | ----------- |
| `"geolocation"` | Access to GPS/location |
| `"notifications"` | Web push notifications |
| `"camera"` | Camera access (`getUserMedia`) |
| `"microphone"` | Microphone access (`getUserMedia`) |
| `"midi"` | MIDI device access |
| `"clipboard-read"` | Read from clipboard |
| `"clipboard-write"` | Write to clipboard |
| `"persistent-storage"` | Persistent storage permission |
| `"background-sync"` | Background sync permission |

!!! note "Browser support"
    Not all permissions are supported by all browsers. Chrome and Edge
    support the widest range. Firefox may not support all permission types.

## Use cases

### Test geolocation-dependent features

```python
async with await client.browsing.open("https://maps.example.com") as page:
    # Grant geolocation so the page can access navigator.geolocation
    await client.permissions.set_permission(
        descriptor={"name": "geolocation"},
        state="granted",
        contexts=[page.id],
    )

    # Also set a simulated location
    await client.emulation.set_geolocation_override(
        coordinates={"latitude": 40.7128, "longitude": -74.0060, "accuracy": 1.0},
        contexts=[page.id],
    )

    # Now the page's geolocation API will work
    result = await page.evaluate("""
        new Promise(resolve => {
            navigator.geolocation.getCurrentPosition(pos => {
                resolve({lat: pos.coords.latitude, lng: pos.coords.longitude});
            });
        })
    """, await_promise=True)
```

### Test denied permissions

```python
# Deny camera to test fallback behavior
await client.permissions.set_permission(
    descriptor={"name": "camera"},
    state="denied",
    contexts=[ctx],
)

# The page should show a fallback UI
result = await page.evaluate("document.querySelector('.camera-error')?.textContent")
```

### Reset to default

```python
# Reset to prompt (normal browser behavior)
await client.permissions.set_permission(
    descriptor={"name": "geolocation"},
    state="prompt",
    contexts=[ctx],
)
```

## API reference

See [Permissions API](../api/permissions.md) for the complete
`PermissionsModule` reference.
