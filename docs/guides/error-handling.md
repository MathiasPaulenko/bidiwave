# Guía de errores — bidiwave

## Jerarquía de excepciones

```text
BiDiError (base)
├── ConnectionError          # WebSocket desconectado o inalcanzable
├── TimeoutError             # Timeout esperando respuesta o navegación
├── CapabilityError          # Browser no soporta la capability
├── ProtocolError            # Mensaje del protocolo inválido o inesperado
├── SessionError             # Sesión inválida o expirada
└── CommandError             # Browser rechazó el comando
    ├── InvalidArgumentError # Argumento inválido
    ├── NoSuchFrameError     # Context no encontrado
    └── JavaScriptError      # Error al evaluar JS
```

## Errores por escenario

### Conexión

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| Browser no responde | `ConnectionError` | Browser no lanzado, puerto incorrecto | Verificar que el browser está corriendo con `--remote-debugging-port` |
| WebSocket cerrado | `ConnectionError` | Browser crasheó o fue cerrado | Reconnect automático, o reconectar manual |
| Timeout al conectar | `TimeoutError` | Firewall, red lenta | Aumentar `timeout` en `BiDiClient.connect()` |

### Sesión

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| `session.new` falla | `SessionError` | Capabilities no soportadas | Verificar `alwaysMatch` en capabilities |
| Sesión expirada | `SessionError` | Sesión cerrada por el browser | Crear nueva sesión |
| `session.subscribe` falla | `CommandError` | Event type no soportado | Verificar `client.capabilities` |

### Navegación

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| URL inválida | `CommandError` | URL malformada | Validar URL antes de navegar |
| Timeout de carga | `TimeoutError` | Página lenta o colgada | Usar `wait="none"` o `wait="interactive"`, o aumentar timeout |
| Context cerrado | `CommandError` | Context fue cerrado por otro proceso | Verificar que el context existe antes de navegar |
| Screenshot falla | `CommandError` | Context no visible (headless sin GPU) | Usar `--headless=new` en Chrome |

### Script

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| Error de JS | `CommandError` | Expresión inválida | Capturar errores en JS: `try { ... } catch(e) { return e.message }` |
| Promise no resuelta | `TimeoutError` | `await_promise=True` y Promise colgada | Usar timeout en JS: `Promise.race([promise, timeout(5000)])` |
| Handle inválido | `CommandError` | Handle ya liberado o context cerrado | No reusar handles tras `disown()` o `close()` |

### Eventos

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| Handler falla | (silencioso) | Excepción en handler async | El handler se ejecuta en error isolation. Loguear errores dentro del handler |
| Eventos perdidos | (silencioso) | Queue llena, drop policy activo | Aumentar `max_queue` o usar `drop_policy="block"` |
| No llegan eventos | (silencioso) | No se suscribió o context cerrado | Verificar `session.subscribe()` y que el context esté activo |

### Reconexión

| Escenario | Excepción | Causa común | Solución |
|---|---|---|---|
| Reconnect falla | `ConnectionError` | Browser cerrado | Manejar `on_reconnect` failure, relanzar browser |
| Sesión perdida tras reconnect | `SessionError` | La sesión BiDi no sobrevive reconexión | Crear nueva sesión en `on_reconnect` handler |
| Handlers duplicados tras reconnect | (silencioso) | Re-registrar handlers en cada reconnect | Los handlers se mantienen en memoria, no re-registrar |

## Patrones de manejo de errores

### Retry con backoff

```python
async def navigate_with_retry(client, ctx, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.browsing.navigate(ctx, url, wait="complete")
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Context-safe operations

```python
async def safe_navigate(client, ctx, url):
    try:
        return await client.browsing.navigate(ctx, url, wait="complete")
    except CommandError as e:
        if "no such frame" in e.message.lower():
            ctx = await client.browsing.create_context()
            return await client.browsing.navigate(ctx, url, wait="complete")
        raise
```

### Capability guard

```python
async def safe_screenshot(client, ctx):
    if not client.capabilities.supports_browsing:
        raise CapabilityError("Browser no soporta browsing.captureScreenshot")
    return await client.browsing.screenshot(ctx)
```

### Promise con timeout en JS

```python
result = await client.script.evaluate(
    ctx,
    """new Promise((resolve, reject) => {
        setTimeout(() => resolve('done'), 1000);
        setTimeout(() => reject(new Error('timeout')), 5000);
    })""",
    await_promise=True,
)
```

## Logging

bidiwave usa el módulo `logging` estándar de Python. Configurar para ver mensajes:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("bidiwave").setLevel(logging.DEBUG)
```

Niveles:

- `DEBUG` — todos los mensajes enviados/recibidos, correlación de IDs
- `INFO` — conexiones, reconexiones, suscripciones
- `WARNING` — eventos descartados (backpressure), handlers fallidos
- `ERROR` — errores de protocolo, comandos rechazados
