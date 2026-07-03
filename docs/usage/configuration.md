# Configuration

bidiwave provides two levels of configuration: `ClientConfig` (high-level,
user-facing) and `TransportConfig` (low-level, WebSocket transport). In
most cases you only need `ClientConfig` — bidiwave derives the transport
config from it automatically.

## ClientConfig

`ClientConfig` controls the behavior of the `BiDiClient` — timeouts,
reconnection strategy, event queue, and logging:

```python
from bidiwave import BiDiClient, ClientConfig

config = ClientConfig(
    timeout=60.0,
    max_retries=5,
    retry_delay=1.0,
    retry_backoff=2.0,
    max_queue=1000,
    drop_policy="oldest",
    log_level="INFO",
)

client = await BiDiClient.connect("ws://localhost:9515/session", config=config)
```

### Options

| Option | Type | Default | Description |
| ------ | ---- | ------- | ----------- |
| `timeout` | `float` | `30.0` | Timeout for command responses, in seconds. If a command doesn't get a response within this time, a `TimeoutError` is raised. |
| `max_retries` | `int` | `3` | Maximum number of reconnection attempts when the WebSocket drops. Set to `0` to disable reconnection. |
| `retry_delay` | `float` | `1.0` | Initial delay before the first reconnection attempt, in seconds. |
| `retry_backoff` | `float` | `2.0` | Multiplier applied to the delay after each failed reconnection attempt. E.g., with `retry_delay=1.0` and `retry_backoff=2.0`, delays are: 1s, 2s, 4s. |
| `max_queue` | `int` | `1000` | Maximum number of events to buffer in the event queue. When the queue is full, the `drop_policy` determines what happens. |
| `drop_policy` | `Literal["oldest", "newest", "block"]` | `"oldest"` | What to do when the event queue is full (see below). |
| `log_level` | `str` | `"INFO"` | Python logging level for the `bidiwave` logger. |

### Drop policies

When the event queue reaches `max_queue` events, the `drop_policy`
controls what happens to new events:

| Policy | Behavior | Use case |
| ------ | -------- | -------- |
| `"oldest"` | Drop the oldest event from the queue to make room for the new one | When recent events matter more than old ones (e.g., log monitoring) |
| `"newest"` | Drop the new event (don't add it to the queue) | When you don't want to lose historical events |
| `"block"` | Wait until there's space in the queue (backpressure) | When you can't afford to lose any events (e.g., audit logging) |

### Reconnection strategy

When the WebSocket connection drops, bidiwave tries to reconnect with
exponential backoff:

```
Attempt 1: wait retry_delay seconds          (1.0s by default)
Attempt 2: wait retry_delay * retry_backoff  (2.0s)
Attempt 3: wait retry_delay * retry_backoff² (4.0s)
...up to max_retries attempts
```

During reconnection:

- All `on_disconnect` handlers are called when the connection drops.
- Commands that were in-flight are rejected with `ConnectionError`.
- After a successful reconnect, all `on_reconnect` handlers are called.
- You must re-subscribe to events after a reconnect (subscriptions don't
  survive).

### Tuning for different scenarios

**Fast feedback (development)**:

```python
config = ClientConfig(
    timeout=10.0,
    max_retries=1,
    retry_delay=0.5,
    log_level="DEBUG",
)
```

**Resilient (production)**:

```python
config = ClientConfig(
    timeout=60.0,
    max_retries=10,
    retry_delay=1.0,
    retry_backoff=2.0,
    max_queue=5000,
    drop_policy="block",
    log_level="WARNING",
)
```

**High-throughput events**:

```python
config = ClientConfig(
    max_queue=10000,
    drop_policy="oldest",
    log_level="WARNING",
)
```

## TransportConfig

`TransportConfig` is the low-level configuration for the WebSocket
transport layer. It's derived from `ClientConfig` automatically, but you
can create and pass it directly if you need fine-grained control:

```python
from bidiwave import BiDiClient, TransportConfig

transport = TransportConfig(
    timeout=60.0,
    max_retries=5,
    retry_delay=1.0,
    retry_backoff=2.0,
    max_queue=1000,
    drop_policy="oldest",
)

client = await BiDiClient.connect(
    "ws://localhost:9515/session",
    transport_config=transport,
)
```

The `TransportConfig` has the same fields as `ClientConfig` except
`log_level`. It's used internally by the `Connection` class.

## Logging

bidiwave uses Python's standard `logging` module. All log messages go
through the `"bidiwave"` logger. You can configure it globally:

```python
import logging

# Enable all bidiwave logs
logging.getLogger("bidiwave").setLevel(logging.DEBUG)

# Or configure via basicConfig
logging.basicConfig(level=logging.INFO)
```

### Log levels

| Level | What gets logged |
| ----- | ---------------- |
| `DEBUG` | Every message sent/received, ID correlation, event dispatching |
| `INFO` | Connection events, reconnections, subscriptions, context creation |
| `WARNING` | Events dropped (backpressure), failed event handlers, deprecated usage |
| `ERROR` | Protocol errors, rejected commands, connection failures |

### Interpreting logs

**DEBUG** output is very verbose — it logs every WebSocket frame. Use it
only for debugging protocol-level issues:

```
DEBUG bidiwave.transport: → {"id":1,"method":"session.new","params":{...}}
DEBUG bidiwave.transport: ← {"id":1,"result":{"sessionId":"..."}}
DEBUG bidiwave.events: Dispatching log.entryAdded to 2 handlers
```

**INFO** is good for production monitoring — it shows the connection
lifecycle without the noise:

```
INFO bidiwave: Connected to ChromeDriver 131.0.6778.87
INFO bidiwave: Subscribed to: log.entryAdded, network.beforeRequestSent
INFO bidiwave: Reconnecting (attempt 1/3)...
INFO bidiwave: Reconnected successfully
```

## API reference

See [Config API](../api/config.md) for the complete `ClientConfig` and
`TransportConfig` reference.
