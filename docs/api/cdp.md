# CDP

The CDP module provides access to Chrome DevTools Protocol commands.
For full usage examples, see [CDP](../usage/cdp.md).

!!! warning "Chrome/Edge only"
    CDP commands are only supported by Chromium-based browsers.

## Methods

### send_command

Send a raw CDP command:

```python
result = await client.cdp.send_command(
    method="Performance.getMetrics",
    params={},
)
# result.result contains the CDP response
```

### get_session

Get the CDP session ID for a specific browsing context:

```python
session = await client.cdp.get_session(context="context-id-1")
# session.session = "cdp-session-id"
```

## Reference

::: bidiwave.modules.cdp.CDPModule
