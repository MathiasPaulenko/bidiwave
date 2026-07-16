# Log

The log module manages browser console logs and log entry events.

## Methods

### clear

Clear all log entries for specific contexts:

```python
await client.log.clear(contexts=["context-id-1"])
```

## Events

Subscribe to `log.entryAdded` to receive console logs in real time:

```python
async def on_log(entry):
    print(f"[{entry.level.upper()}] {entry.text}")

client.on("log.entryAdded", on_log)
await client.session.subscribe(["log.entryAdded"])
```

### Log entry fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `level` | `str` | `"info"`, `"warning"`, `"error"`, `"debug"` |
| `text` | `str` | Log message text |
| `timestamp` | `int` | Unix timestamp (ms) |
| `args` | `list[RemoteValue]` | Structured arguments (auto-parsed) |
| `type` | `str` | Log type: `"console"`, `"javascript"` |
| `method` | `str \| None` | Console method (e.g. `"log"`, `"warn"`, `"error"`) |
| `stack_trace` | `StackTrace \| None` | Call stack (if available) |
| `source` | `ScriptSource \| None` | Source realm and context info |

## Reference

::: bidiwave.modules.log.LogModule
