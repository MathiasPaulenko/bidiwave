# Emulation

The emulation module overrides browser settings for device simulation.
For full usage examples, see [Emulation](../usage/emulation.md).

## Methods

- `set_geolocation` — simulate a geographic location or a position error
- `set_locale` — override the browser locale (e.g. `"fr-FR"`)
- `set_screen_orientation` — set screen orientation (`{"type": "portrait-primary", "natural": "portrait"}`)
- `set_timezone` — change the browser's time zone
- `set_network_conditions` — offline emulation (the spec's only network condition)
- `set_user_agent` — override the User-Agent string

## Locale override

```python
await client.emulation.set_locale("fr-FR", contexts=["context-id-1"])
```

## Screen orientation

```python
await client.emulation.set_screen_orientation(
    {"type": "portrait-primary", "natural": "portrait"},
    contexts=["context-id-1"],
)
```

## Geolocation with error simulation

```python
# Simulate a position error (e.g. GPS unavailable)
await client.emulation.set_geolocation(
    error={"type": "positionUnavailable"},
    contexts=["context-id-1"],
)

# Or simulate a real position
await client.emulation.set_geolocation(
    coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
    user_contexts=["user-context-id-1"],
)
```

## Reference

::: bidiwave.modules.emulation.EmulationModule
