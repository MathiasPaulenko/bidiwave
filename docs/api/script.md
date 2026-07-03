# Script

::: bidiwave.modules.script.ScriptModule

## Add preload script with channels

Unlike `preload.addPreloadScript`, `script.addPreloadScript` supports
channels for bidirectional communication between the preload script and
the client via `script.message` events.

```python
result = await client.script.add_preload_script(
    function_declaration="(channel) => { channel('hello from page'); }",
    arguments=[{"type": "channel", "value": {"channel": "my-channel"}}],
    contexts=["context-id-1"],
)
print(result.script)  # preload script ID
print(result.channel) # channel name for communication
```

Receive messages from the preload script:

```python
async def on_message(event):
    print(f"Message from preload: {event.data}")

client.on("script.message", on_message)
await client.session.subscribe(["script.message"])
```
