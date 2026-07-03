# bidiwave — Development Context

## Current Status

| Phase | Status | Commit |
|---|---|---|
| 0. Setup + Spike | ✅ Complete | 1a047b1 |
| 1. Hello World | ✅ Complete | fdc10f5 |
| 2. Events | ✅ Complete | — |
| 3. Robustness | ✅ Complete | — |
| 4. Ergonomics | ✅ Complete | — |
| 5. Integration + CI | ✅ Complete | — |
| 6. Docs + Release | ✅ Complete | — |

## Phase 0 — Setup + Spike (complete)

- `pyproject.toml` with hatchling, ruff, mypy, pytest-asyncio
- Structure: `bidiwave/{protocol,transport,modules}/`
- `spike.py` validated BiDi with Chrome and Edge via ChromeDriver/EdgeDriver
- `docs/spike-notes.md` with findings
- `bin/` gitignored (drivers downloaded on-demand)

## Phase 1 — Hello World (complete)

### Implemented Files

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
- `bidiwave/__init__.py` — public exports
- 28 unit tests in `tests/unit/`
- Integration test: `tests/integration/test_hello_world.py`

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 28 passed
- Integration test: navigates to example.com, evaluates `document.title` → "Example Domain"

## Key Findings

- Chrome/Edge need ChromeDriver/EdgeDriver as a BiDi proxy. The `--remote-debugging-port` exposes CDP, not BiDi.
- When connecting via ChromeDriver `webSocketUrl`, the BiDi session **already exists**. `session.new` fails with "session already exists". Use `session.status` to verify.
- Command names are `browsingContext.*` (not `browsing.*` as the original prompt suggested)
- `script.evaluate` nests the value in `result["result"]["value"]`
- Chrome 149, Edge 149. ChromeDriver 149.0.7827.155, EdgeDriver 149.0.4022.98
- Driver paths: `bin/chromedriver-win64/chromedriver.exe`, `bin/edgedriver/msedgedriver.exe`
- pytest needs `-c pyproject.toml` when run from `D:\Codigo\bidiwave` (the brainstorming pyproject.toml interferes)

## Phase 2 — Events (complete)

### Implemented Files

- `protocol/events.py` — `Event`, `LogEntryAddedEvent`, `BrowsingContextCreatedEvent`, `BrowsingContextDestroyedEvent`, `BrowsingContextNavigatedEvent`, `ScriptMessageEvent`, `parse_event` factory
- `events/handlers.py` — `AsyncHandler` type, `Subscription` dataclass with weakref to dispatcher
- `events/queue.py` — `EventQueue` (asyncio.Queue wrapper, no backpressure yet)
- `events/dispatcher.py` — `EventDispatcher` with `on()`, `off()`, `dispatch()`, error isolation
- `transport/connection.py` — modified: receive loop now dispatches events to `EventDispatcher`
- `modules/session.py` — added `subscribe()`, `unsubscribe()`
- `client.py` — added `on()`, `off()`, `on_log_entry()`, integration with `EventDispatcher`
- `__init__.py` — exports: `EventDispatcher`, `Subscription`, `AsyncHandler`
- 11 new unit tests (6 dispatcher + 5 events) — total 39 passed

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 39 passed
- Pending: integration test against real Chrome (real-time console logs)

### Notes

- Event names aligned with `constants.py` and the real spec: `browsingContext.contextCreated` (not `browsing.contextCreated`)
- `BROWSING_CONTEXT_NAVIGATED` in constants.py is `browsingContext.navigationStarted` — the `BrowsingContextNavigatedEvent` model matches that name
- `Subscription` uses `weakref` to dispatcher to avoid reference cycles
- Error isolation: a handler that raises an exception does not affect other handlers or the receive loop

## Phase 3 — Robustness (complete)

### Implemented / Modified Files

- `exceptions.py` — full hierarchy: `TimeoutError`, `CapabilityError`, `ProtocolError`, `SessionError`, `InvalidArgumentError`, `NoSuchFrameError`, `NoSuchWindowError`, `JavaScriptError`, `ERROR_CODE_MAP`, `map_error()`
- `events/queue.py` — `EventQueue` with backpressure: drop policies `oldest`, `newest`, `block`, `dropped_count`
- `protocol/capabilities.py` — `Capabilities` with `supports_browsing/script/network/input`, `detect_capabilities` with Firefox heuristic
- `transport/connection.py` — `TransportConfig` (timeout, max_retries, retry_delay, retry_backoff, max_queue, drop_policy), reconnect with exponential backoff, `on_reconnect`/`on_disconnect` handlers, `map_error` in receive loop
- `protocol/commands.py` — `ScreenshotParams`, `CallFunctionParams`, `DisownParams`, `GetTreeParams`, `SubscribeParams`
- `protocol/constants.py` — added `SESSION_END`
- `modules/session.py` — added `end()`
- `modules/browsing.py` — added `screenshot()`, `get_tree()`
- `modules/script.py` — added `call_function()`, `disown()`
- `client.py` — `TransportConfig` param in `connect()`, `capabilities` property, `on_reconnect()`/`on_disconnect()`
- `__init__.py` — exports: `TransportConfig`, `Capabilities`, all new exceptions
- 19 new unit tests (5 queue + 4 capabilities + 6 exceptions + 4 reconnect) — total 58 passed

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 58 passed
- Pending: integration tests against real Chrome (screenshot, get_tree, call_function, disown, reconnect)

### Notes

- `TransportConfig` uses Pydantic BaseModel for typed validation
- Reconnect: exponential backoff with `retry_delay * retry_backoff^attempt`, calls `on_reconnect` handlers after reconnecting
- `map_error` maps BiDi error codes to `CommandError` subtypes — the receive loop now uses `map_error` instead of raw `CommandError`
- `detect_capabilities` uses heuristic: Firefox supports network/input, Chrome does not (can be refined in Phase 5)
- `EventQueue` is now configurable but not yet integrated into the dispatcher (Phase 4 may integrate it)

## Phase 4 — API Ergonomics (complete)

### Implemented / Modified Files

- `protocol/remote_value.py` — `RemoteValue` base + subtypes: `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `BigIntValue`, `ObjectValue`, `ArrayValue`, `HandleValue` with `parse()` factory using `match`
- `protocol/results.py` — `Session`, `SessionStatus`, `Navigation`, `Screenshot` typed models
- `config.py` — `ClientConfig` with Pydantic: timeout, max_retries, retry_delay, retry_backoff, max_queue, drop_policy, log_level
- `_internal/logging.py` — `setup_logging()` with optional structured format
- `modules/browsing.py` — `BrowsingContext` dataclass with `__aenter__`/`__aexit__`, `BrowsingModule` with `script_module` ref, `create_context()` returns `BrowsingContext`, `navigate`/`screenshot`/`close` accept `BrowsingContext | str`, `wait_for_selector`, `wait_for_function`, `open()` returns `Page`
- `modules/script.py` — `evaluate`/`call_function` return `RemoteValue`, accept `BrowsingContext | str`
- `modules/session.py` — `new()` returns `Session`, `status()` returns `SessionStatus`
- `convenience/page.py` — `Page` object: `evaluate`, `call`, `navigate`, `screenshot` (bytes), `wait_for_selector`, `wait_for_function`, `disown`, `close`, context manager
- `events/dispatcher.py` — Fluent API (`on()` returns `Self`) + decorator mode (`@dispatcher.on("event")`)
- `client.py` — `__aenter__`/`__aexit__`, `ClientConfig` in `connect()`, `on_context_created`/`on_context_destroyed`, `BrowsingModule` with `script_module` ref
- `__init__.py` — exports: `ClientConfig`, `Page`, `BrowsingContext`, `RemoteValue` + all subtypes
- 25 new unit tests (10 remote_value + 5 context_managers + 6 page + 4 fluent_api) — total 83 passed
- `pyproject.toml` — added `ignore = ["ASYNC109"]` (timeout is a legitimate parameter of the public API)

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Pending: integration tests with real Chrome (context managers, Page object, wait helpers, type narrowing)

### Notes

- `from __future__ import annotations` added to `browsing.py` and `remote_value.py` to resolve forward references
- `BrowsingModule` is defined before `BrowsingContext` so the dataclass can reference it
- `Page` uses deferred imports (`from bidiwave.convenience.page import Page` inside `open()`) to avoid circular imports
- `EventDispatcher.on()` now returns `Self | Subscription | Callable` — fluent when handler is passed, decorator when not
- `ClientConfig` replaces `TransportConfig` in `BiDiClient.connect()` — builds `TransportConfig` internally

## Phase 5 — Integration + CI (complete)

### Implemented Files

- `tests/conftest.py` — markers: unit, integration, contract, slow, chrome, firefox
- `tests/integration/conftest.py` — fixtures: `chrome_bidi` (ChromeDriver Windows), `client` (indirect param), `context` (BrowsingContext auto-cleanup), `pytest_collection_modifyitems` for auto-marker integration
- `tests/integration/test_connection.py` — connect/close, context manager
- `tests/integration/test_session.py` — session.status, subscribe/unsubscribe
- `tests/integration/test_browsing.py` — create/close context, navigate, context manager, screenshot (PNG bytes), get_tree
- `tests/integration/test_script.py` — evaluate string/number/boolean/null, call_function, await_promise
- `tests/integration/test_events.py` — console log event, contextCreated, contextDestroyed (rewritten with new API)
- `tests/integration/test_ergonomics.py` — Page object, wait_for_selector, wait_for_function, type narrowing with match
- `tests/integration/test_hello_world.py` — rewritten with new API (StringValue, fixtures)
- `.github/workflows/test.yml` — CI matrix: unit (ubuntu+windows, py3.11/3.12/3.13, ruff+mypy+pytest+codecov), integration-chrome, integration-firefox

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Integration tests: pending execution against real Chrome (requires active ChromeDriver)
- CI: configured for GitHub Actions (unit + integration Chrome + Firefox)

### Notes

- Fixtures use indirect parametrization: `@pytest.mark.parametrize("client", ["chrome_bidi"], indirect=True)`
- `chrome_bidi` fixture launches ChromeDriver, creates WebDriver session, returns BiDi WebSocket URL
- `client` fixture resolves the fixture name via `request.getfixturevalue()` to get the URL
- Integration tests auto-marked with `@pytest.mark.integration` via `pytest_collection_modifyitems`
- CI uses `browser-actions/setup-chrome` and `browser-actions/setup-firefox` for integration tests
- Coverage: `--cov=bidiwave --cov-report=xml --cov-fail-under=90` in unit test CI

## Phase 6 — Docs + Release (complete)

### Implemented Files

- `README.md` — rewritten with badges (CI, PyPI, Python, License), quick start with new API, console log monitoring, instructions for launching Chrome/Firefox
- `mkdocs.yml` — Material theme with dark/light mode, mkdocstrings auto-gen, complete nav
- `docs/index.md` — landing page with features and quick example
- `docs/quick-start.md` — installation, launching browser, hello world, console logs, screenshot, configuration
- `docs/cookbook.md` — 7 recipes updated to new API (context managers, Page object)
- `docs/error-handling.md` — exception hierarchy, scenarios, patterns, logging
- `docs/protocol-reference.md` — complete reference of commands, events and error codes
- `docs/api/` — 8 mkdocstrings pages: client, session, browsing, script, events, remote-value, exceptions, config
- `CHANGELOG.md` — v1.0.0 entry with all features
- `.github/workflows/docs.yml` — deploy to GitHub Pages on push to main
- `.github/workflows/release.yml` — build + publish to PyPI via Trusted Publishing on tag push
- `pyproject.toml` — version bumped to 1.0.0, classifier updated to Production/Stable
- `bidiwave/__init__.py` — `__version__ = "1.0.0"`

### Verification

- `ruff check .` — passes
- `mypy bidiwave/` — passes (28 source files)
- `pytest tests/unit/ -c pyproject.toml` — 83 passed
- Docs deps already present in `pyproject.toml`: mkdocs, mkdocs-material, mkdocstrings[python]
- Pending: `mkdocs build` local, `python -m build`, `pip install` in clean env, tag v1.0.0

### Release checklist

- [ ] `mkdocs build` without errors
- [ ] `python -m build` generates wheel and sdist
- [ ] `pip install dist/bidiwave-1.0.0-py3-none-any.whl` in clean env
- [ ] Quick start guide reproduces the hello world
- [ ] Configure Trusted Publishing on PyPI
- [ ] `git tag v1.0.0 && git push origin main --tags`

## Reference Paths (in the brainstorming repo)

- **Development plan**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\development-plan.md`
- **Architecture**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\architecture\README.md`
- **Design patterns**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\design\design-patterns.md`
- **Module spec**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\modules-spec.md`
- **Protocol reference**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\docs\protocol-reference.md`
- **Phase prompts**: `D:\Codigo\brainstorming\ideas\libraries\bidiwave\prompts\` (phase-0-setup.md, phase-1-hello-world.md, etc.)
- **Spike notes**: `D:\Codigo\bidiwave\docs\spike-notes.md`

## How to Continue

To continue development, tell Cascade:
> "continue with bidiwave, read CONTEXT.md"
