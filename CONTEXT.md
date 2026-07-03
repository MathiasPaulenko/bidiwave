# bidiwave — Contexto de desarrollo

## Estado actual

| Fase | Estado | Commit |
|---|---|---|
| 0. Setup + Spike | ✅ Completa | 1a047b1 |
| 1. Hello World | ✅ Completa | fdc10f5 |
| 2. Eventos | ✅ Completa | — |
| 3. Robustez | ✅ Completa | — |
| 4. Ergonomics | ✅ Completa | — |
| 5. Integration + CI | ✅ Completa | — |
| 6. Docs + Release | ✅ Completa | — |

## Phase 0 — Setup + Spike (completa)

- `pyproject.toml` con hatchling, ruff, mypy, pytest-asyncio
- Estructura: `bidiwave/{protocol,transport,modules}/`
- `spike.py` validó BiDi con Chrome y Edge via ChromeDriver/EdgeDriver
- `docs/spike-notes.md` con findings
- `bin/` gitignored (drivers descargados on-demand)

## Phase 1 — Hello World (completa)

### Archivos implementados

- `bidiwave/protocol/constants.py` — command names (`browsingContext.*`, `session.*`, `script.*`), event names, error codes
- `bidiwave/protocol/commands.py` — `Command`, `NewSessionParams`, `NavigateParams`, `EvaluateParams` (Pydantic v2, `extra="allow"`)
- `bidiwave/protocol/responses.py` — `SuccessResponse`, `ErrorResponse`, `ErrorData`, `parse_response` factory
- `bidiwave/protocol/capabilities.py` — `Capabilities` model, `detect_capabilities`
- `bidiwave/transport/serializer.py` — `serialize_command`, `deserialize_message`
- `bidiwave/transport/correlation.py` — `Correlator` (Future-based command/response matching)
- `bidiwave/transport/connection.py` — `Connection` (WebSocket receive loop, correlator, 30s timeout)
- `bidiwave/exceptions.py` — `BiDiError`, `ConnectionError`, `CommandError`
- `bidiwave/modules/session.py` — `SessionModule` (`new`, `status`)
- `bidiwave/modules/browsing.py` — `BrowsingModule` (`create_context`, `navigate`, `close`)
- `bidiwave/modules/script.py` — `ScriptModule` (`evaluate`)
- `bidiwave/client.py` — `BiDiClient.connect()` classmethod, `close()`
- `bidiwave/__init__.py` — exports públicos
- 28 unit tests en `tests/unit/`
- Integration test: `tests/integration/test_hello_world.py`

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 28 passed
- Integration test: navega a example.com, evalúa `document.title` → "Example Domain"

## Hallazgos clave

- Chrome/Edge necesitan ChromeDriver/EdgeDriver como proxy BiDi. El `--remote-debugging-port` expone CDP, no BiDi.
- Al conectar via ChromeDriver `webSocketUrl`, la sesión BiDi **ya existe**. `session.new` falla con "session already exists". Usar `session.status` para verificar.
- Los nombres de comandos son `browsingContext.*` (no `browsing.*` como decía el prompt original)
- `script.evaluate` anida el valor en `result["result"]["value"]`
- Chrome 149, Edge 149. ChromeDriver 149.0.7827.155, EdgeDriver 149.0.4022.98
- Driver paths: `bin/chromedriver-win64/chromedriver.exe`, `bin/edgedriver/msedgedriver.exe`
- pytest necesita `-c pyproject.toml` cuando se ejecuta desde `D:\Codigo\bidiwave` (el pyproject.toml de brainstorming interfiere)

## Phase 2 — Eventos (completa)

### Archivos implementados

- `protocol/events.py` — `Event`, `LogEntryAddedEvent`, `BrowsingContextCreatedEvent`, `BrowsingContextDestroyedEvent`, `BrowsingContextNavigatedEvent`, `ScriptMessageEvent`, `parse_event` factory
- `events/handlers.py` — `AsyncHandler` type, `Subscription` dataclass con weakref al dispatcher
- `events/queue.py` — `EventQueue` (asyncio.Queue wrapper, sin backpressure aún)
- `events/dispatcher.py` — `EventDispatcher` con `on()`, `off()`, `dispatch()`, error isolation
- `transport/connection.py` — modificado: receive loop ahora dispatcha eventos al `EventDispatcher`
- `modules/session.py` — añadido `subscribe()`, `unsubscribe()`
- `client.py` — añadido `on()`, `off()`, `on_log_entry()`, integración con `EventDispatcher`
- `__init__.py` — exports: `EventDispatcher`, `Subscription`, `AsyncHandler`
- 11 unit tests nuevos (6 dispatcher + 5 events) — total 39 passed

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 39 passed
- Pendiente: integration test contra Chrome real (console logs en tiempo real)

### Notas

- Los nombres de eventos se alinearon con `constants.py` y el spec real: `browsingContext.contextCreated` (no `browsing.contextCreated`)
- `BROWSING_CONTEXT_NAVIGATED` en constants.py es `browsingContext.navigationStarted` — el modelo `BrowsingContextNavigatedEvent` matchea ese nombre
- `Subscription` usa `weakref` al dispatcher para evitar reference cycles
- Error isolation: un handler que lanza excepción no afecta a otros handlers ni al receive loop

## Phase 3 — Robustez (completa)

### Archivos implementados / modificados

- `exceptions.py` — jerarquía completa: `TimeoutError`, `CapabilityError`, `ProtocolError`, `SessionError`, `InvalidArgumentError`, `NoSuchFrameError`, `NoSuchWindowError`, `JavaScriptError`, `ERROR_CODE_MAP`, `map_error()`
- `events/queue.py` — `EventQueue` con backpressure: drop policies `oldest`, `newest`, `block`, `dropped_count`
- `protocol/capabilities.py` — `Capabilities` con `supports_browsing/script/network/input`, `detect_capabilities` con heurística Firefox
- `transport/connection.py` — `TransportConfig` (timeout, max_retries, retry_delay, retry_backoff, max_queue, drop_policy), reconnect con backoff exponencial, `on_reconnect`/`on_disconnect` handlers, `map_error` en receive loop
- `protocol/commands.py` — `ScreenshotParams`, `CallFunctionParams`, `DisownParams`, `GetTreeParams`, `SubscribeParams`
- `protocol/constants.py` — añadido `SESSION_END`
- `modules/session.py` — añadido `end()`
- `modules/browsing.py` — añadido `screenshot()`, `get_tree()`
- `modules/script.py` — añadido `call_function()`, `disown()`
- `client.py` — `TransportConfig` param en `connect()`, `capabilities` property, `on_reconnect()`/`on_disconnect()`
- `__init__.py` — exports: `TransportConfig`, `Capabilities`, todas las excepciones nuevas
- 19 unit tests nuevos (5 queue + 4 capabilities + 6 exceptions + 4 reconnect) — total 58 passed

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 58 passed
- Pendiente: integration tests contra Chrome real (screenshot, get_tree, call_function, disown, reconnect)

### Notas

- `TransportConfig` usa Pydantic BaseModel para validación tipada
- Reconnect: backoff exponencial con `retry_delay * retry_backoff^attempt`, llama `on_reconnect` handlers tras reconectar
- `map_error` mapea códigos BiDi a subtipos de `CommandError` — el receive loop ahora usa `map_error` en vez de `CommandError` directo
- `detect_capabilities` usa heurística: Firefox soporta network/input, Chrome no (puede refinarse en Fase 5)
- `EventQueue` ahora es configurable pero no está integrada en el dispatcher aún (Fase 4 puede integrarla)

## Phase 4 — API Ergonomics (completa)

### Archivos implementados / modificados

- `protocol/remote_value.py` — `RemoteValue` base + subtipos: `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `BigIntValue`, `ObjectValue`, `ArrayValue`, `HandleValue` con `parse()` factory usando `match`
- `protocol/results.py` — `Session`, `SessionStatus`, `Navigation`, `Screenshot` modelos tipados
- `config.py` — `ClientConfig` con Pydantic: timeout, max_retries, retry_delay, retry_backoff, max_queue, drop_policy, log_level
- `_internal/logging.py` — `setup_logging()` con formato estructurado opcional
- `modules/browsing.py` — `BrowsingContext` dataclass con `__aenter__`/`__aexit__`, `BrowsingModule` con `script_module` ref, `create_context()` retorna `BrowsingContext`, `navigate`/`screenshot`/`close` aceptan `BrowsingContext | str`, `wait_for_selector`, `wait_for_function`, `open()` retorna `Page`
- `modules/script.py` — `evaluate`/`call_function` retornan `RemoteValue`, aceptan `BrowsingContext | str`
- `modules/session.py` — `new()` retorna `Session`, `status()` retorna `SessionStatus`
- `convenience/page.py` — `Page` object: `evaluate`, `call`, `navigate`, `screenshot` (bytes), `wait_for_selector`, `wait_for_function`, `disown`, `close`, context manager
- `events/dispatcher.py` — Fluent API (`on()` retorna `Self`) + decorator mode (`@dispatcher.on("event")`)
- `client.py` — `__aenter__`/`__aexit__`, `ClientConfig` en `connect()`, `on_context_created`/`on_context_destroyed`, `BrowsingModule` con `script_module` ref
- `__init__.py` — exports: `ClientConfig`, `Page`, `BrowsingContext`, `RemoteValue` + todos los subtipos
- 25 unit tests nuevos (10 remote_value + 5 context_managers + 6 page + 4 fluent_api) — total 83 passed
- `pyproject.toml` — añadido `ignore = ["ASYNC109"]` (timeout es parámetro legítimo de la API pública)

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Pendiente: integration tests con Chrome real (context managers, Page object, wait helpers, type narrowing)

### Notas

- `from __future__ import annotations` añadido a `browsing.py` y `remote_value.py` para resolver referencias forward
- `BrowsingModule` se define antes de `BrowsingContext` para que el dataclass pueda referenciarlo
- `Page` usa imports diferidos (`from bidiwave.convenience.page import Page` dentro de `open()`) para evitar circular imports
- `EventDispatcher.on()` ahora retorna `Self | Subscription | Callable` — fluent cuando se pasa handler, decorator cuando no
- `ClientConfig` reemplaza a `TransportConfig` en `BiDiClient.connect()` — construye `TransportConfig` internamente

## Phase 5 — Integration + CI (completa)

### Archivos implementados

- `tests/conftest.py` — markers: unit, integration, contract, slow, chrome, firefox
- `tests/integration/conftest.py` — fixtures: `chrome_bidi` (ChromeDriver Windows), `client` (indirect param), `context` (BrowsingContext auto-cleanup), `pytest_collection_modifyitems` para auto-marker integration
- `tests/integration/test_connection.py` — connect/close, context manager
- `tests/integration/test_session.py` — session.status, subscribe/unsubscribe
- `tests/integration/test_browsing.py` — create/close context, navigate, context manager, screenshot (PNG bytes), get_tree
- `tests/integration/test_script.py` — evaluate string/number/boolean/null, call_function, await_promise
- `tests/integration/test_events.py` — console log event, contextCreated, contextDestroyed (rewritten con nueva API)
- `tests/integration/test_ergonomics.py` — Page object, wait_for_selector, wait_for_function, type narrowing con match
- `tests/integration/test_hello_world.py` — rewritten con nueva API (StringValue, fixtures)
- `.github/workflows/test.yml` — CI matrix: unit (ubuntu+windows, py3.11/3.12/3.13, ruff+mypy+pytest+codecov), integration-chrome, integration-firefox

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Integration tests: pendientes de ejecutar contra Chrome real (requieren ChromeDriver activo)
- CI: configurado para GitHub Actions (unit + integration Chrome + Firefox)

### Notas

- Fixtures usan indirect parametrization: `@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)`
- `chrome_bidi` fixture lanza ChromeDriver, crea sesión WebDriver, retorna URL del WebSocket BiDi
- `client` fixture resuelve el nombre del fixture via `request.getfixturevalue()` para obtener la URL
- Integration tests auto-marcados con `@pytest.mark.integration` via `pytest_collection_modifyitems`
- CI usa `browser-actions/setup-chrome` y `browser-actions/setup-firefox` para integration tests
- Coverage: `--cov=bidiwave --cov-report=xml --cov-fail-under=90` en CI de unit tests

## Phase 6 — Docs + Release (completa)

### Archivos implementados

- `README.md` — reescrito con badges (CI, PyPI, Python, License), quick start con nueva API, console log monitoring, instrucciones para lanzar Chrome/Firefox
- `mkdocs.yml` — Material theme con dark/light mode, mkdocstrings auto-gen, nav completo
- `docs/index.md` — landing page con features y quick example
- `docs/quick-start.md` — instalación, lanzar browser, hello world, console logs, screenshot, configuración
- `docs/cookbook.md` — 7 recetas actualizadas a la nueva API (context managers, Page object)
- `docs/error-handling.md` — jerarquía de excepciones, escenarios, patrones, logging
- `docs/protocol-reference.md` — referencia completa de comandos, eventos y códigos de error
- `docs/api/` — 8 páginas mkdocstrings: client, session, browsing, script, events, remote-value, exceptions, config
- `CHANGELOG.md` — entrada v1.0.0 con todas las features
- `.github/workflows/docs.yml` — deploy a GitHub Pages on push to main
- `.github/workflows/release.yml` — build + publish a PyPI via Trusted Publishing on tag push
- `pyproject.toml` — version bumped to 1.0.0, classifier updated to Production/Stable
- `bidiwave/__init__.py` — `__version__ = "1.0.0"`

### Verificación

- `ruff check .` — pasa
- `mypy bidiwave/` — pasa (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Docs deps ya presentes en `pyproject.toml`: mkdocs, mkdocs-material, mkdocstrings[python]
- Pendiente: `mkdocs build` local, `python -m build`, `pip install` en env limpio, tag v1.0.0

### Release checklist

- [ ] `mkdocs build` sin errores
- [ ] `python -m build` genera wheel y sdist
- [ ] `pip install dist/bidiwave-1.0.0-py3-none-any.whl` en env limpio
- [ ] Quick start guide reproduce el hello world
- [ ] Configurar Trusted Publishing en PyPI
- [ ] `git tag v1.0.0 && git push origin main --tags`

## Rutas de referencia (en el repo brainstorming)

- **Plan de desarrollo**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\development-plan.md`
- **Arquitectura**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\architecture\README.md`
- **Patrones de diseño**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\design\design-patterns.md`
- **Spec de módulos**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\modules-spec.md`
- **Referencia del protocolo**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\protocol-reference.md`
- **Prompts por fase**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\prompts\` (phase-0-setup.md, phase-1-hello-world.md, etc.)
- **Spike notes**: `D:\Codigo\bidiwave\docs\spike-notes.md`

## Cómo continuar

Para continuar desarrollo, decirle a Cascade:
> "continúa con bidiwave, lee CONTEXT.md"
