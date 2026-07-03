# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.2] - 2025-07-04

### Documentation

- Comprehensive usage docs for all new modules: Emulation, Permissions, Preload, CDP
- Updated browsing.md with viewport (ViewportSize + DPR), activate, locateNodes, all 9 event types
- Updated network.md with cache overrides, response body, authentication, 5 new event types
- Updated storage.md with delete_cookie and cookieChanged event
- Updated script.md with add_preload_script (channels), get_realms, realm events
- Added 7 new cookbook recipes (viewport, cache override, emulation, preload, cookies, response body, CDP)
- Enriched all API pages with method summaries and code examples
- Updated index.md with full feature list and documentation links
- Updated mkdocs.yml nav with 4 new usage pages

## [1.7.1] - 2025-07-04

### Documentation

- Complete protocol reference with all 53 commands and 21 events
- Added API doc pages for Preload, Emulation, Permissions, Log, and CDP modules
- Updated events.md with all event types and convenience handlers
- Added cache override, response body, and auth docs to network.md
- Added delete_cookie docs to storage.md
- Added script.addPreloadScript with channels docs to script.md
- Updated mkdocs.yml nav with new API pages
- Added Pydantic model mapping tables to protocol reference

## [1.7.0] - 2025-07-04

### Added

- `BrowsingContextHistoryUpdatedEvent` — Chrome-specific event for history changes (pushState, replaceState)
- `NetworkModule.response_body()` — retrieves body of a completed response by request ID
- `StorageModule.delete_cookie()` — deletes a single cookie by name (vs delete_cookies by filter)
- `ViewportSize` model — typed viewport dimensions for `set_viewport` (accepts model or dict)
- `ScriptModule.add_preload_script()` — preload script with channel support for bidirectional communication
- `ResponseBodyResult`, `ScriptAddPreloadScriptResult` result models
- `parse_event` factory updated with historyUpdated
- Convenience handler: `on_history_updated()`
- 7 new unit tests (total: 226)

## [1.6.5] - 2025-07-04

### Added

- `NetworkModule.set_cache_override()` — replaces all existing cache overrides in a single call (set vs add/remove pattern)
- 2 new unit tests (total: 219)

## [1.6.4] - 2025-07-04

### Added

- `BrowsingContextDOMContentLoadedEvent` — fires when DOM is parsed but resources still loading (before load)
- `NetworkSamplingStateChangedEvent` — fires when network sampling mode changes (all/none)
- `parse_event` factory updated with 2 new event types
- Convenience handlers: `on_dom_content_loaded()`, `on_sampling_state_changed()`
- 3 new unit tests (total: 217)

## [1.6.3] - 2025-07-04

### Added

- `NetworkAuthRequiredEvent` — dedicated Pydantic model for network.authRequired (previously only a handler)
- `BrowsingContextFragmentNavigatedEvent` — fires on fragment (#anchor) navigation
- `BrowsingContextLoadEvent` — fires when the page finishes loading (window load event)
- `parse_event` factory updated with 3 new event types
- Convenience handlers: `on_fragment_navigated()`, `on_load()`
- 5 new unit tests (total: 214)

## [1.6.2] - 2025-07-04

### Added

- `NetworkModule.add_cache_override()` / `remove_cache_override()` — cached response override for matching requests
- `NetworkDataReceivedEvent` — fires when response body data arrives (streaming)
- `BrowsingContextNavigationCompletedEvent` — fires when navigation finishes (complete/canceled)
- `parse_event` factory updated with 2 new event types
- Convenience handlers: `on_data_received()`, `on_navigation_completed()`
- `AddCacheOverrideResult` result model
- 7 new unit tests (total: 209)

## [1.6.1] - 2025-07-03

### Added

- `NetworkResponseStartedEvent` — fires when response headers are received (before body completes)
- `ScriptRealmCreatedEvent` — fires when a new realm is created
- `ScriptRealmDestroyedEvent` — fires when a realm is destroyed
- `BrowsingContextUserPromptOpenedEvent` — fires when a dialog (alert/confirm/prompt) opens
- `parse_event` factory updated to handle all new event types
- Convenience handlers in `BiDiClient`: `on_response_started()`, `on_realm_created()`, `on_realm_destroyed()`, `on_user_prompt_opened()`
- 8 new unit tests (total: 202)

## [1.6.0] - 2025-07-03

### Added

- `PreloadModule` — `add_script()` and `remove_script()` for injecting scripts before page load
- `EmulationModule` — `set_geolocation()`, `set_network_conditions()`, `set_timezone()`, `set_user_agent()` for device environment emulation
- `PermissionsModule` — `set_permission()` for controlling browser permissions (geolocation, notifications, etc.)
- `LogModule` — `clear()` for clearing the log buffer
- `BrowsingModule.get_viewport()` — returns `Viewport` with width, height, and device pixel ratio
- `Viewport` and `AddPreloadScriptResult` result models
- 14 new unit tests (total: 194)

## [1.5.1] - 2025-07-03

### Changed

- Translated all Spanish documentation, docstrings, and comments to English across the entire codebase

## [1.2.1] - 2025-07-03

### Fixed

- `NameError: BrowsingContext` in `script.py` and `browsing.py` — `isinstance` with class under `TYPE_CHECKING`
- `Navigation` validation error — `context` now optional (protocol does not always return it)
- `RemoteValue.parse` now unwraps `{type: "success", result: {...}}` wrapper from `script.evaluate`
- `screenshot` "invalid argument" — do not send `format` when it's the default `png`
- `wait_for_selector` rewritten with `script.evaluate` (driver bug with `callFunction` and primitive args)
- `wait_for_function` unwraps `type: "success"` wrapper correctly
- Integration tests migrated to headless EdgeDriver (does not affect user's Chrome)
- 23 integration tests passing, 118 unit tests passing

## [1.2.0] - 2025-07-03

### Added

- `InputModule` — user input simulation (keyboard, mouse, scroll)
  - `perform_actions()` — executes action sequences with virtual devices
  - `release_actions()` — cancels ongoing actions
  - `set_files()` — selects files on `<input type="file">`
  - `click()` — click at coordinates (x, y) with configurable button
  - `double_click()` — double click at coordinates
  - `type_text()` — types text key by key
  - `press_key()` — presses and releases a key
  - `scroll()` — mouse wheel scroll (horizontal and vertical)
  - `drag_and_drop()` — drag and drop between two points
- `InputSource`, `KeyAction`, `PointerAction`, `WheelAction` — typed models
- 15 unit tests for InputModule

## [1.1.0] - 2025-07-03

### Added

- `NetworkModule` — network request interception and monitoring
  - `add_intercept()` / `remove_intercept()` — block requests at specific phases
  - `continue_request()` — continue an intercepted request with modifications
  - `continue_response()` — continue an intercepted response with modifications
  - `fail_request()` — fail an intercepted request
  - `provide_response()` — provide a synthetic response without making the actual request
- Event models: `NetworkBeforeRequestSentEvent`, `NetworkResponseCompletedEvent`, `NetworkFetchErrorEvent`
- `BiDiClient.on_request()`, `on_response()`, `on_fetch_error()` — convenience handlers
- `NetworkRequestData`, `NetworkResponseData` — typed protocol models
- 20 unit tests for network module and event models

## [1.0.1] - 2025-07-03

### Fixed

- CI: lower coverage threshold from 90% to 80% (integration tests don't run in unit CI)
- CI: add `permissions: contents: write` to docs workflow for gh-pages deploy
- CI: remove invalid `--browser` flag from integration test commands
- CI: mark integration tests as `continue-on-error` (fixtures are Windows-specific)

## [1.0.0] - 2025-07-03

### Added

- `BiDiClient` with `connect()`, `close()`, context manager (`async with`)
- `SessionModule` — `new()`, `status()`, `subscribe()`, `unsubscribe()`
- `BrowsingModule` — `create_context()`, `navigate()`, `close()`, `screenshot()`, `get_tree()`, `wait_for_selector()`, `wait_for_function()`, `open()`
- `ScriptModule` — `evaluate()`, `call_function()`, `disown()`
- `EventDispatcher` — `on()`, `off()`, fluent API, decorator mode, error isolation
- `Page` object — convenience layer with `evaluate()`, `screenshot()`, `wait_for_selector()`, `wait_for_function()`, `close()`
- `RemoteValue` with subtypes: `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `BigIntValue`, `ObjectValue`, `ArrayValue`, `HandleValue`
- `Capabilities` — detection from `session.status`
- `ClientConfig` — typed configuration with Pydantic
- Reconnect with exponential backoff
- Backpressure with drop policies (oldest, newest, block)
- Exception hierarchy: `BiDiError`, `ConnectionError`, `TimeoutError`, `CapabilityError`, `CommandError`, `InvalidArgumentError`, `NoSuchFrameError`, `JavaScriptError`
- Cross-browser: Chrome, Firefox, Edge
- Structured logging
- CI: GitHub Actions with Chrome + Firefox matrix, Python 3.11/3.12/3.13
- Coverage > 90%
