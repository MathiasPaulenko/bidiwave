# Referencia del protocolo WebDriver BiDi

## Comandos v1

### session.new

Crea una nueva sesión BiDi.

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

Retorna el estado de la sesión actual.

```json
{
  "id": 2,
  "method": "session.status",
  "params": {}
}
```

### session.subscribe

Suscribe a eventos.

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

Crea un nuevo context (tab).

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

Navega a una URL.

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

Cierra un context.

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

Retorna el árbol de contexts.

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

Captura screenshot del context.

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

Evalúa una expresión JS.

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

Llama una función JS.

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

Libera una referencia (handle) de un objeto remoto.

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

## Eventos v1

### log.entryAdded

Emitido cuando hay un console.log o error JS.

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

Emitido cuando se crea un nuevo context.

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

Emitido cuando se cierra un context.

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

Emitido durante la navegación.

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

Emitido cuando un script envía un mensaje via `script.channel`.

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

## Códigos de error

| Code | Descripción |
|---|---|
| `invalid argument` | Parámetro inválido |
| `invalid session` | Sesión no válida o expirada |
| `session not created` | No se pudo crear la sesión |
| `session not found` | Sesión no encontrada |
| `unknown command` | Comando no soportado por el browser |
| `unsupported operation` | Operación no soportada |
| `javascript error` | Error al evaluar JS |
| `no such frame` | Context no encontrado |
| `no such window` | Window no encontrada |
| `timeout` | Timeout del browser |
| `unable to capture screen` | No se pudo capturar screenshot |

## Mapeo a modelos Pydantic

Cada comando y evento tiene un modelo Pydantic correspondiente en `protocol/`. Los nombres de los modelos siguen el patrón:

- Comando: `session.new` → `NewSessionParams`
- Evento: `log.entryAdded` → `LogEntryAddedEvent`
- Response: siempre `SuccessResponse` o `ErrorResponse`
