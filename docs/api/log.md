# Log

The W3C BiDi spec defines no log commands — only the `log.entryAdded`
event. `client.log` exists as a stable namespace.

## Events

Subscribe to `log.entryAdded` to receive console logs in real time:

```python
async def on_log(entry):
    print(f"[{entry.level.upper()}] {entry.text}")

client.on("log.entryAdded", on_log)
# or: client.on_log_entry(on_log)
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
