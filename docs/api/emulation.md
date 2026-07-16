# Emulation

The emulation module overrides browser settings for device simulation.
For full usage examples, see [Emulation](../usage/emulation.md).

## Methods

- `set_geolocation_override` — simulate a geographic location (supports `userContexts` and `error` parameters)
- `set_locale_override` — override the browser locale (e.g. `"fr-FR"`)
- `set_screen_orientation_override` — set screen orientation (`"portrait"`, `"landscape"`)
- `set_timezone_override` — change the browser's time zone (supports `userContexts`)
- `set_network_conditions` — simulate network speed/latency
- `set_user_agent_override` — override the User-Agent string

## Locale override

```python
await client.emulation.set_locale_override(
    locale="fr-FR",
    contexts=["context-id-1"],
)
```

## Screen orientation

```python
await client.emulation.set_screen_orientation_override(
    orientation="portrait",
    contexts=["context-id-1"],
)
```

## Geolocation with error simulation

```python
# Simulate a position error (e.g. GPS unavailable)
await client.emulation.set_geolocation_override(
    error={"type": "positionUnavailable"},
    contexts=["context-id-1"],
)

# Or simulate a real position
await client.emulation.set_geolocation_override(
    coordinates={"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
    user_contexts=["user-context-id-1"],
)
```

## Reference

::: bidiwave.modules.emulation.EmulationModule
