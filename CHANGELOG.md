# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-03

### Added

- `BiDiClient` con `connect()`, `close()`, context manager (`async with`)
- `SessionModule` — `new()`, `status()`, `subscribe()`, `unsubscribe()`
- `BrowsingModule` — `create_context()`, `navigate()`, `close()`, `screenshot()`, `get_tree()`, `wait_for_selector()`, `wait_for_function()`, `open()`
- `ScriptModule` — `evaluate()`, `call_function()`, `disown()`
- `EventDispatcher` — `on()`, `off()`, fluent API, decorator mode, error isolation
- `Page` object — convenience layer con `evaluate()`, `screenshot()`, `wait_for_selector()`, `wait_for_function()`, `close()`
- `RemoteValue` con subtipos: `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `BigIntValue`, `ObjectValue`, `ArrayValue`, `HandleValue`
- `Capabilities` — detection desde `session.status`
- `ClientConfig` — configuración tipada con Pydantic
- Reconnect con backoff exponencial
- Backpressure con drop policies (oldest, newest, block)
- Jerarquía de excepciones: `BiDiError`, `ConnectionError`, `TimeoutError`, `CapabilityError`, `CommandError`, `InvalidArgumentError`, `NoSuchFrameError`, `JavaScriptError`
- Cross-browser: Chrome, Firefox, Edge
- Logging estructurado
- CI: GitHub Actions con matrix Chrome + Firefox, Python 3.11/3.12/3.13
- Coverage > 90%
