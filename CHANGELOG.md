# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.2] - 2026-07-17

### Fixed — W3C WebDriver BiDi Spec Compliance

#### Network Module
- `continue_request`: `post_data` now sent as `body` with `BytesValue` instead of raw `postData`
- `fail_request`: removed non-spec `error` parameter — only `request` is sent per CDDL
- `continue_response`: removed non-spec `body` parameter; added `credentials` parameter
- `provide_response`: body now wrapped as `BytesValue` per spec
- `add_data_collector`: replaced non-spec `collector` dict with `data_types`, `max_encoded_data_size`, and optional `collector_type` per `network.AddDataCollectorParameters`
- `get_data`: replaced non-spec `context`/`url` with `request` (required), `data_type` (required), optional `collector` and `disown` per `network.GetDataParameters`
- `disown_data`: now requires `collector`, `request`, and `data_type` per `network.DisownDataParameters`; removed non-spec `url`

#### Emulation Module
- `set_network_conditions`: replaced `download_throughput`/`upload_throughput`/`latency` with spec-compliant `networkConditions: {type: "offline"}` or `null` per `emulation.SetNetworkConditionsParameters`
- `set_user_agent`: removed non-spec `accept_language` and `platform` parameters per `emulation.SetUserAgentOverrideParameters`
- `set_screen_orientation`: uses `screenOrientation` key (not `orientation`) with spec-compliant kebab-case types (e.g. `"portrait-primary"`) per `emulation.SetScreenOrientationOverrideParameters`

#### Protocol & Models
- `Cookie.expires`: wire field is now `expiry` (alias) per W3C BiDi spec
- `HandleValue.handle`: made optional (`str | None`) to support `ownership: "none"` scenarios

#### Infrastructure
- `setup_logging`: now re-applies formatter to existing handlers on subsequent calls instead of silently discarding new format

### Tests
- Updated all affected unit tests to assert spec-compliant wire formats
- Added regression tests for `HandleValue` without handle
- Added unit tests for `setup_logging` reconfiguration behavior

## [1.8.1] - 2026-07-16

### Added

#### New Modules

- `WebExtensionModule` — `install()` and `uninstall()` for browser extension management (Bug 70)
- `PermissionsModule` — `set_permission()` for controlling browser permissions (separate W3C spec)

#### New Commands

- `BrowsingModule.close_browser()` — `browser.close` (Bug 61)
- `BrowsingModule.get_client_windows()` — `browser.getClientWindows` (Bug 66)
- `BrowsingModule.set_client_window_state()` — `browser.setClientWindowState` (Bug 66)
- `BrowsingModule.activate()` — `browsingContext.activate`
- `BrowsingModule.locate_nodes()` — `browsingContext.locateNodes` with `serializationOptions` (Bug 72)
- `EmulationModule.set_locale()` — `emulation.setLocaleOverride` (Bug 64)
- `EmulationModule.set_screen_orientation()` — `emulation.setScreenOrientationOverride` (Bug 64)
- `NetworkModule.add_data_collector()` / `get_data()` / `disown_data()` / `remove_data_collector()` (Bug 68)
- `NetworkModule.set_cache_behavior()` — `network.setCacheBehavior` (Bug 67)
- `NetworkModule.set_extra_headers()` — `network.setExtraHeaders` (Bug 65)
- `ScriptModule.add_preload_script()` / `remove_preload_script()` — with channel support (Bug 50)
- `ScriptModule.get_realms()` — `script.getRealms`
- `InputModule.set_files()` — `input.setFiles`

#### New Events

- `BrowsingContextDownloadWillBeginEvent` / `BrowsingContextDownloadEndEvent` (Bug 63)
- `BrowsingContextUserPromptClosedEvent` (Bug 62)
- `BrowsingContextNavigationAbortedEvent` / `NavigationCommittedEvent` / `NavigationFailedEvent` (Bug 48)
- `BrowsingContextHistoryUpdatedEvent`
- `InputFileDialogOpenedEvent` (Bug 69)
- `ScriptMessageEvent` / `ScriptRealmCreatedEvent` / `ScriptRealmDestroyedEvent`

#### New Remote Value Types

- `DateValue`, `RegExpValue`, `MapValue`, `SetValue` (Bug 55)
- `WeakMapValue`, `WeakSetValue`, `GeneratorValue`, `ErrorValue`, `ProxyValue`, `PromiseValue` (Bug 71)
- `TypedArrayValue`, `ArrayBufferValue`, `NodeListValue`, `HTMLCollectionValue`, `WindowValue` (Bug 71)
- `ChannelValue` for preload script channel communication

#### New Protocol Models

- `ScriptSource` — typed `script.Source` (realm + context) for `LogEntryAddedEvent` and `ScriptMessageEvent` (Bug 74)
- `NodeValue` — `nodeProperties` field and `sharedId` alias (Bug 73)
- `ObjectValue` / `ArrayValue` — parse nested `RemoteValue` objects via `RemoteValue.parse()` (Bug 73)
- `SerializationOptions` support in `evaluate`, `callFunction`, and `locateNodes` (Bug 72)

#### New Error Codes

- 11 new exception types: `NoSuchElementException`, `NoSuchCookieException`, `StaleElementReferenceException`, `ElementNotInteractableException`, `InsecureCertificateException`, `MoveTargetOutOfBoundsException`, `NoSuchAlertException`, `NoSuchShadowRootException`, `DetachedShadowRootException`, `InvalidWebExtensionException`, `NoSuchUserContextException` (Bug 57)

#### New BiDiClient Convenience Methods

- `on_navigation_started()`, `on_navigation_aborted()`, `on_navigation_committed()`, `on_navigation_failed()`
- `on_user_prompt_closed()`, `on_download_will_begin()`, `on_download_end()`
- `on_script_message()`

#### New Parameters

- `browser.createUserContext` — `acceptInsecureCerts` parameter
- `browsingContext.create` — `referenceContext`, `background`, and `userContext` in result (Bug 75)
- `browsingContext.captureScreenshot` — `clip` and `origin` parameters
- `emulation.setGeolocationOverride` — `userContexts` and `error` parameters (Bug 74)
- `emulation.setTimezoneOverride` — `userContexts` parameter (Bug 74)
- `network.addIntercept` — `url_patterns` accepts `NetworkUrlPattern` dicts (Bug 75)
- `network.continueRequest` — `post_data` parameter
- `network.continueResponse` / `provideResponse` — `cookies` parameter
- `network.continueWithAuth` — validates `credentials` required for `provideCredentials`
- `network.authRequired` event — optional `response` field
- `script.evaluate` / `callFunction` — `serializationOptions`, `userActivation` parameters
- `script.callFunction` — `this` parameter
- `storage.getCookies` — `filter` and `partitionKey` parameters
- `storage.setCookie` / `deleteCookies` — `partitionKey` parameter
- `PreloadModule.add_script` — `userContexts` parameter (Bug 76)
- `session.subscribe` — returns subscription result from server (Bug 76)

### Changed

- `BrowsingContextNavigatedEvent` renamed to `BrowsingContextNavigationStartedEvent` (backward-compatible alias kept)
- `LogEntryAddedEvent.level` — `"warn"` normalized to `"warning"` per W3C spec (Bug 52)
- `LogEntryAddedEvent.type` — changed to `Literal["console", "javascript"]` per spec
- `LogEntryAddedEvent.source` — typed as `ScriptSource` (Bug 74)
- `LogEntryAddedEvent.args` — typed as `list[RemoteValue]` with auto-parsing (Bug 75)
- `LogEntryAddedEvent` — added `stackTrace` and `method` fields per spec
- `ScriptMessageEvent.source` — typed as `ScriptSource` (Bug 74)
- `ScriptRealmCreatedEvent.type` — changed to `Literal["window", "dedicated-worker", "shared-worker", "service-worker", "worker"]` per spec (Bug 45)
- `BrowsingContextUserPromptOpenedEvent.type` — `Literal["alert", "confirm", "prompt", "beforeunload"]` (Bug 41)
- `BrowsingContextUserPromptOpenedEvent.handler` — `Literal["accept", "dismiss", "default"] | None` (Bug 42)
- `BrowsingContextCreatedEvent` — `populate_by_name=True`, aliases for `userContext`/`originalOpener` (Bug 54)
- `browsingContext.print` — sends `printBackground` per spec instead of `background` (Bug 74)
- `browsingContext.print` — `pageRanges` accepts `list[int | str]` per spec
- `Cookie.sameSite` — normalized to lowercase (`strict`, `lax`, `none`) per spec
- `Cookie.value` — accepts `BytesValue` dict format `{type: 'base64', value: '...'}` per spec (Bug 51)
- `network.cancel_auth` — uses `continueWithAuth` with `action="cancel"` instead of non-existent `network.cancelAuth`
- `storage.delete_cookie` — uses `deleteCookies` with name filter instead of non-existent `storage.deleteCookie`
- `Page.wait_for_function` — uses `awaitPromise=True` with Promise wrapper instead of client-side polling (Bug 77)
- `Page.__aexit__` — suppresses close exceptions only when already exiting with an exception (Bug 77)
- `BiDiClient.set_auto_prompt` / `disable_auto_prompt` — track subscription state, avoid duplicate subscribe/unsubscribe (Bug 77)
- Network headers type annotations — `list[dict[str, Any]]` for structured header values
- `get_tree` — returns typed `GetTreeResult` with `children` list

### Fixed

- `NETWORK_CANCEL_AUTH` dead constant removed from constants.py
- `STORAGE_DELETE_COOKIE` dead constant removed from constants.py
- `TransportConfig` — `max_queue` / `drop_policy` dead code removed (Bug 77)
- `add_intercept` — validates empty `phases` list
- `ResponseBodyResult.total_size` — default=0 for browsers that omit `totalSize`
- `NetworkDataReceivedEvent.data_size` — default=0
- `ObjectValue.value` — normalizes list-of-pairs format from browsers (Bug 53)
- `RemoteValue.parse` — handles all spec types including `date`, `regexp`, `map`, `set`, `weakmap`, `weakset`, `generator`, `error`, `proxy`, `promise`, `typedarray`, `arraybuffer`, `nodelist`, `htmlcollection`, `window` (Bugs 46-49, 71)
- `RemoteValue.parse` — unwraps `{type: "success", result: {...}}` wrapper from `script.evaluate`
- `RemoteValue.parse` — raises `JavaScriptError` on `{type: "exception"}` responses

### Tests

- 642 tests total (607 passed, 5 skipped, 3 xfailed, 27 new integration tests)
- Unit tests: 505+ covering all new events, commands, models, and convenience methods
- Integration tests: 43 tests (16 cross-module, 14 edge-case E2E, 13 new feature tests)

## [1.8.0] - 2026-07-15

### Fixed

#### Critical
- `reconnect` — `reject_all` on pending commands during reconnection
- `command timeout` — leak when command completes after timeout fires
- `key action types` — `keyDown`/`keyUp` correctly typed per spec
- `capability detection` — proper parsing of `session.status` capabilities

#### High Priority
- `malformed JSON` handling — graceful error instead of crash
- `event parse errors` — isolated per-event, no cascade failure
- `async dispatch` — proper task scheduling for event handlers
- `exception shadowing` — original errors preserved in cleanup paths
- `auto-prompt ordering` — subscribe before navigation, not after

#### Medium Priority
- `connection timeout` — proper cleanup on connect failure
- `receive loop crash` — guarded against unexpected message formats
- `close cleanup` — ordered shutdown prevents resource leaks
- `falsy checks` — `0`/`""`/`False` no longer treated as `None`
- `logging handlers` — duplicate handlers prevented on reconfigure
- `remote value types` — correct parsing for edge-case types
- `context leak` — browsing contexts properly tracked and cleaned
- `double-close` — idempotent close on `BiDiClient` and `Page`
- `exception masking` — `__aexit__` preserves original exception

#### Low Priority
- `action model types` — `InputSource`/`KeyAction`/`PointerAction` field validation
- `constant names` — aligned with W3C spec command names
- `error code map` — complete mapping of all BiDi error codes
- `bytes handling` — proper `BytesValue` serialization
- `quality validation` — input validation on public API boundaries
- `EventQueue` — removed dead code

### Tests
- Fixed test expectations for `keyDown`/`keyUp`, capability defaults, prompt handler
- Ruff lint and mypy type fixes for CI

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
- `EventDispatcher` — `on()`, `off()`, decorator mode, error isolation
- `Page` object — convenience layer with `evaluate()`, `screenshot()`, `wait_for_selector()`, `wait_for_function()`, `close()`
- `RemoteValue` with subtypes: `StringValue`, `NumberValue`, `BooleanValue`, `NullValue`, `UndefinedValue`, `BigIntValue`, `ObjectValue`, `ArrayValue`, `HandleValue`
- `Capabilities` — detection from `session.status`
- `ClientConfig` — typed configuration with Pydantic
- Reconnect with exponential backoff
- Exception hierarchy: `BiDiError`, `BiDiConnectionError`, `BiDiTimeoutError`, `CapabilityError`, `CommandError`, `InvalidArgumentError`, `NoSuchFrameError`, `JavaScriptError`
- Cross-browser: Chrome, Firefox, Edge
- Structured logging
- CI: GitHub Actions with Chrome + Firefox matrix, Python 3.11/3.12/3.13
- Coverage > 90%
