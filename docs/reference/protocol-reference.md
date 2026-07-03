# WebDriver BiDi protocol reference

## Commands v1

### session.new

Creates a new BiDi session.

```json
{
  "id": 1,
  "method": "session.new",
  "params": {
    "capabilities": {
      "alwaysMatch": {
        "webSocketUrl": true
      }
    }
  }
}
```

Response:

```json
{
  "type": "success",
  "id": 1,
  "result": {
    "sessionId": "...",
    "capabilities": {
      "browserName": "chrome",
      "browserVersion": "120.0",
      "platformName": "linux",
      "webSocketUrl": "ws://localhost:9222/session/...",
      "acceptInsecureCerts": false
    }
  }
}
```

### session.status

Returns the status of the current session.

```json
{
  "id": 2,
  "method": "session.status",
  "params": {}
}
```

### session.subscribe

Subscribes to events.

```json
{
  "id": 3,
  "method": "session.subscribe",
  "params": {
    "events": ["log.entryAdded", "browsing.contextCreated"],
    "contexts": ["context-id-1"]
  }
}
```

### browsing.createContext

Creates a new context (tab).

```json
{
  "id": 4,
  "method": "browsing.createContext",
  "params": {
    "type": "tab"
  }
}
```

### browsing.navigate

Navigates to a URL.

```json
{
  "id": 5,
  "method": "browsing.navigate",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "wait": "complete"
  }
}
```

### browsing.close

Closes a context.

```json
{
  "id": 6,
  "method": "browsing.close",
  "params": {
    "context": "context-id-1"
  }
}
```

### browsing.getTree

Returns the context tree.

```json
{
  "id": 7,
  "method": "browsing.getTree",
  "params": {
    "root": null
  }
}
```

### browsing.captureScreenshot

Captures a screenshot of the context.

```json
{
  "id": 8,
  "method": "browsing.captureScreenshot",
  "params": {
    "context": "context-id-1",
    "format": "png"
  }
}
```

Response:

```json
{
  "type": "success",
  "id": 8,
  "result": {
    "data": "iVBORw0KGgo..."
  }
}
```

### script.evaluate

Evaluates a JS expression.

```json
{
  "id": 9,
  "method": "script.evaluate",
  "params": {
    "expression": "document.title",
    "target": {
      "context": "context-id-1"
    },
    "awaitPromise": false
  }
}
```

### script.callFunction

Calls a JS function.

```json
{
  "id": 10,
  "method": "script.callFunction",
  "params": {
    "functionDeclaration": "(selector) => document.querySelector(selector)?.textContent",
    "args": [
      { "type": "string", "value": "h1" }
    ],
    "target": {
      "context": "context-id-1"
    },
    "awaitPromise": false
  }
}
```

### script.disown

Releases a reference (handle) to a remote object.

```json
{
  "id": 11,
  "method": "script.disown",
  "params": {
    "handles": ["handle-id-1"],
    "target": {
      "context": "context-id-1"
    }
  }
}
```

## Events v1

### log.entryAdded

Emitted when there is a console.log or JS error.

```json
{
  "type": "event",
  "method": "log.entryAdded",
  "params": {
    "level": "info",
    "text": "Hello from console",
    "timestamp": 1700000000000,
    "source": {
      "realm": "realm-id-1",
      "context": "context-id-1"
    },
    "type": "console"
  }
}
```

Levels: `debug`, `info`, `warn`, `error`

Types: `console`, `javascript`

### browsing.contextCreated

Emitted when a new context is created.

```json
{
  "type": "event",
  "method": "browsing.contextCreated",
  "params": {
    "context": "context-id-2",
    "url": "about:blank",
    "userContext": "default",
    "originalOpener": null
  }
}
```

### browsing.contextDestroyed

Emitted when a context is closed.

```json
{
  "type": "event",
  "method": "browsing.contextDestroyed",
  "params": {
    "context": "context-id-2"
  }
}
```

### browsing.contextNavigated

Emitted during navigation.

```json
{
  "type": "event",
  "method": "browsing.contextNavigated",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1",
    "status": "complete"
  }
}
```

Status: `pending`, `complete`, `canceled`

### script.message

Emitted when a script sends a message via `script.channel`.

```json
{
  "type": "event",
  "method": "script.message",
  "params": {
    "realm": "realm-id-1",
    "source": {
      "context": "context-id-1"
    },
    "channel": "my-channel",
    "data": {
      "type": "string",
      "value": "hello"
    }
  }
}
```

## Error codes

| Code | Description |
|---|---|
| `invalid argument` | Invalid parameter |
| `invalid session` | Invalid or expired session |
| `session not created` | Could not create the session |
| `session not found` | Session not found |
| `unknown command` | Command not supported by the browser |
| `unsupported operation` | Operation not supported |
| `javascript error` | Error evaluating JS |
| `no such frame` | Context not found |
| `no such window` | Window not found |
| `timeout` | Browser timeout |
| `unable to capture screen` | Could not capture screenshot |

## Mapping to Pydantic models

Each command and event has a corresponding Pydantic model in `protocol/`. Model names follow the pattern:

- Command: `session.new` → `NewSessionParams`
- Event: `log.entryAdded` → `LogEntryAddedEvent`
- Response: always `SuccessResponse` or `ErrorResponse`
