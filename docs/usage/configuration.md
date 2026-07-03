# Configuration

## ClientConfig

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

## Options

| Option | Type | Default | Description |
|---|---|---|---|
| `timeout` | `float` | `30.0` | Timeout for command responses (seconds) |
| `max_retries` | `int` | `3` | Max reconnection attempts |
| `retry_delay` | `float` | `1.0` | Initial retry delay (seconds) |
| `retry_backoff` | `float` | `2.0` | Backoff multiplier for retries |
| `max_queue` | `int` | `512` | Max event queue size |
| `drop_policy` | `str` | `"oldest"` | Queue overflow policy: `"oldest"`, `"newest"`, or `"block"` |
| `log_level` | `str` | `"WARNING"` | Logging level |

## TransportConfig

Low-level transport configuration is derived from `ClientConfig`:

```python
from bidiwave import TransportConfig

transport = TransportConfig(
    timeout=60.0,
    max_retries=5,
    retry_delay=1.0,
    retry_backoff=2.0,
    max_queue=1000,
    drop_policy="oldest",
)
```

## Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("bidiwave").setLevel(logging.DEBUG)
```

Levels:

- `DEBUG` — all messages sent/received, ID correlation
- `INFO` — connections, reconnections, subscriptions
- `WARNING` — events dropped (backpressure), failed handlers
- `ERROR` — protocol errors, rejected commands
