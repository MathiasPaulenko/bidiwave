# CDP

The CDP module provides access to Chrome DevTools Protocol commands.
For full usage examples, see [CDP](../usage/cdp.md).

!!! warning "Chrome/Edge only, not part of BiDi"
    `cdp.*` commands are Chromium driver extensions — not in the W3C spec.

## Methods

### send_command

Send a raw CDP command:

```python
result = await client.cdp.send_command(
    "Performance.getMetrics",
    params={},
    session=None,  # optional CDP session to target
)
# result is the raw response dict
```

### get_session

Get the CDP session ID for a browsing context (context required):

```python
session_id = await client.cdp.get_session("context-id-1")
# session_id = "cdp-session-id" or None
```

## Reference

::: bidiwave.modules.cdp.CDPModule
