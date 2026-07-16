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

### browsing.reload

Reloads a context.

```json
{
  "id": 12,
  "method": "browsingContext.reload",
  "params": {
    "context": "context-id-1",
    "wait": "complete"
  }
}
```

### browsing.traverseHistory

Traverses the history (back/forward).

```json
{
  "id": 13,
  "method": "browsingContext.traverseHistory",
  "params": {
    "context": "context-id-1",
    "delta": -1
  }
}
```

### browsing.handleUserPrompt

Handles a dialog (alert/confirm/prompt).

```json
{
  "id": 14,
  "method": "browsingContext.handleUserPrompt",
  "params": {
    "context": "context-id-1",
    "accept": true
  }
}
```

### browsing.print

Prints a context to PDF.

```json
{
  "id": 15,
  "method": "browsingContext.print",
  "params": {
    "context": "context-id-1",
    "pageRanges": [1, 2]
  }
}
```

### browsing.locateNodes

Locates nodes by locator strategy.

```json
{
  "id": 16,
  "method": "browsingContext.locateNodes",
  "params": {
    "context": "context-id-1",
    "locator": {"type": "css", "value": "div.content"}
  }
}
```

### browsing.activate

Activates a context (brings to front).

```json
{
  "id": 17,
  "method": "browsingContext.activate",
  "params": {
    "context": "context-id-1"
  }
}
```

### browsing.setViewport

Sets the viewport and device pixel ratio.

```json
{
  "id": 18,
  "method": "browsingContext.setViewport",
  "params": {
    "context": "context-id-1",
    "viewport": {"width": 800, "height": 600},
    "devicePixelRatio": 2.0
  }
}
```

### browsing.getViewport

Gets the current viewport and device pixel ratio.

```json
{
  "id": 19,
  "method": "browsingContext.getViewport",
  "params": {
    "context": "context-id-1"
  }
}
```

### script.getRealms

Gets information about available realms.

```json
{
  "id": 20,
  "method": "script.getRealms",
  "params": {}
}
```

### network.addIntercept

Adds a network intercept for request interception.

```json
{
  "id": 21,
  "method": "network.addIntercept",
  "params": {
    "phases": ["beforeRequestSent"],
    "urlPatterns": ["*example.com*"]
  }
}
```

### network.removeIntercept

Removes a network intercept.

```json
{
  "id": 22,
  "method": "network.removeIntercept",
  "params": {
    "intercept": "intercept-id-1"
  }
}
```

### network.continueRequest

Continues a blocked request.

```json
{
  "id": 23,
  "method": "network.continueRequest",
  "params": {
    "request": "request-id-1"
  }
}
```

### network.continueResponse

Continues a blocked response.

```json
{
  "id": 24,
  "method": "network.continueResponse",
  "params": {
    "request": "request-id-1"
  }
}
```

### network.failRequest

Fails a blocked request.

```json
{
  "id": 25,
  "method": "network.failRequest",
  "params": {
    "request": "request-id-1"
  }
}
```

### network.provideResponse

Provides a synthetic response without making the real request.

```json
{
  "id": 26,
  "method": "network.provideResponse",
  "params": {
    "request": "request-id-1",
    "statusCode": 200
  }
}
```

### network.continueWithAuth

Continues a request with authentication credentials.

```json
{
  "id": 27,
  "method": "network.continueWithAuth",
  "params": {
    "request": "request-id-1",
    "credentials": {
      "type": "password",
      "username": "user",
      "password": "pass"
    }
  }
}
```

### network.cancelAuth

Cancels an authentication challenge.

```json
{
  "id": 28,
  "method": "network.cancelAuth",
  "params": {
    "request": "request-id-1"
  }
}
```

### network.addCacheOverride

Adds a cached response override for matching requests.

```json
{
  "id": 29,
  "method": "network.addCacheOverride",
  "params": {
    "url": "https://example.com/api",
    "method": "GET",
    "statusCode": 200
  }
}
```

Response:

```json
{
  "type": "success",
  "id": 29,
  "result": {
    "cache": "cache-id-1"
  }
}
```

### network.removeCacheOverride

Removes a previously added cache override.

```json
{
  "id": 30,
  "method": "network.removeCacheOverride",
  "params": {
    "cache": "cache-id-1"
  }
}
```

### network.setCacheOverride

Replaces all existing cache overrides in a single call.

```json
{
  "id": 31,
  "method": "network.setCacheOverride",
  "params": {
    "url": "https://example.com/api",
    "method": "GET",
    "statusCode": 200
  }
}
```

### network.responseBody

Retrieves the body of a completed response.

```json
{
  "id": 32,
  "method": "network.responseBody",
  "params": {
    "request": "request-id-1"
  }
}
```

Response:

```json
{
  "type": "success",
  "id": 32,
  "result": {
    "body": "SGVsbG8gV29ybGQ=",
    "totalSize": 11
  }
}
```

### input.performActions

Performs input actions (pointer, key, wheel).

```json
{
  "id": 33,
  "method": "input.performActions",
  "params": {
    "context": "context-id-1",
    "actions": []
  }
}
```

### input.releaseActions

Releases all input actions.

```json
{
  "id": 34,
  "method": "input.releaseActions",
  "params": {
    "context": "context-id-1"
  }
}
```

### input.setFiles

Sets files for a file input element.

```json
{
  "id": 35,
  "method": "input.setFiles",
  "params": {
    "context": "context-id-1",
    "element": {"sharedId": "element-id-1"},
    "files": ["/path/to/file.txt"]
  }
}
```

### storage.getCookies

Gets cookies from a browsing context.

```json
{
  "id": 36,
  "method": "storage.getCookies",
  "params": {
    "context": "context-id-1"
  }
}
```

### storage.setCookie

Creates or updates a cookie.

```json
{
  "id": 37,
  "method": "storage.setCookie",
  "params": {
    "context": "context-id-1",
    "cookie": {
      "name": "session",
      "value": "abc123",
      "domain": "example.com"
    }
  }
}
```

### storage.deleteCookies

Deletes cookies by filter (name, domain, path).

```json
{
  "id": 38,
  "method": "storage.deleteCookies",
  "params": {
    "context": "context-id-1",
    "name": "session"
  }
}
```

### storage.deleteCookie

Deletes a single cookie by name.

```json
{
  "id": 39,
  "method": "storage.deleteCookie",
  "params": {
    "context": "context-id-1",
    "name": "session"
  }
}
```

### preload.addPreloadScript

Adds a preload script that runs on every new page load.

```json
{
  "id": 40,
  "method": "preload.addPreloadScript",
  "params": {
    "functionDeclaration": "() => { window.foo = 42; }"
  }
}
```

### preload.removePreloadScript

Removes a preload script.

```json
{
  "id": 41,
  "method": "preload.removePreloadScript",
  "params": {
    "script": "preload-id-1"
  }
}
```

### script.addPreloadScript

Adds a preload script with channel support for bidirectional communication.

```json
{
  "id": 42,
  "method": "script.addPreloadScript",
  "params": {
    "functionDeclaration": "(channel) => { channel('hello'); }",
    "arguments": [{"type": "channel", "value": {"channel": "my-channel"}}]
  }
}
```

### emulation.setGeolocationOverride

Sets a geolocation override.

```json
{
  "id": 43,
  "method": "emulation.setGeolocationOverride",
  "params": {
    "coordinates": {"latitude": 37.7749, "longitude": -122.4194}
  }
}
```

### emulation.setNetworkConditions

Sets network conditions (online/offline).

```json
{
  "id": 44,
  "method": "emulation.setNetworkConditions",
  "params": {
    "offline": false
  }
}
```

### emulation.setTimezoneOverride

Sets a timezone override.

```json
{
  "id": 45,
  "method": "emulation.setTimezoneOverride",
  "params": {
    "timezone": "America/Los_Angeles"
  }
}
```

### emulation.setUserAgentOverride

Sets a user agent override.

```json
{
  "id": 46,
  "method": "emulation.setUserAgentOverride",
  "params": {
    "userAgent": "Mozilla/5.0 (Custom)"
  }
}
```

### permissions.setPermission

Sets a permission state for a website.

```json
{
  "id": 47,
  "method": "permissions.setPermission",
  "params": {
    "descriptor": {"name": "geolocation"},
    "state": "granted",
    "origin": "https://example.com"
  }
}
```

### log.clear

Clears all log entries.

```json
{
  "id": 48,
  "method": "log.clear",
  "params": {}
}
```

### browser.createUserContext

Creates a user context (profile).

```json
{
  "id": 49,
  "method": "browser.createUserContext",
  "params": {}
}
```

### browser.removeUserContext

Removes a user context.

```json
{
  "id": 50,
  "method": "browser.removeUserContext",
  "params": {
    "userContext": "user-context-id-1"
  }
}
```

### browser.getUserContexts

Gets all user contexts.

```json
{
  "id": 51,
  "method": "browser.getUserContexts",
  "params": {}
}
```

### browser.cdp.sendCommand

Sends a CDP command (Chrome DevTools Protocol).

```json
{
  "id": 52,
  "method": "browser.cdp.sendCommand",
  "params": {
    "cdpMethod": "Page.reload",
    "cdpParams": {}
  }
}
```

### browser.cdp.getSession

Gets the CDP session for a browsing context.

```json
{
  "id": 53,
  "method": "browser.cdp.getSession",
  "params": {
    "context": "context-id-1"
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

Levels: `debug`, `info`, `warning`, `error`

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

### browsingContext.navigationStarted

Emitted when a navigation starts.

```json
{
  "type": "event",
  "method": "browsingContext.navigationStarted",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1"
  }
}
```

### browsingContext.navigationAborted

Emitted when a navigation is aborted.

```json
{
  "type": "event",
  "method": "browsingContext.navigationAborted",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1"
  }
}
```

### browsingContext.navigationCommitted

Emitted when navigation is committed (response received, document starts loading).

```json
{
  "type": "event",
  "method": "browsingContext.navigationCommitted",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1"
  }
}
```

### browsingContext.navigationFailed

Emitted when a navigation fails.

```json
{
  "type": "event",
  "method": "browsingContext.navigationFailed",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1"
  }
}
```

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

### script.realmCreated

Emitted when a new realm is created.

```json
{
  "type": "event",
  "method": "script.realmCreated",
  "params": {
    "realm": "realm-id-1",
    "type": "window",
    "context": "context-id-1"
  }
}
```

### script.realmDestroyed

Emitted when a realm is destroyed.

```json
{
  "type": "event",
  "method": "script.realmDestroyed",
  "params": {
    "realm": "realm-id-1"
  }
}
```

### browsingContext.userPromptOpened

Emitted when a dialog (alert/confirm/prompt) opens.

```json
{
  "type": "event",
  "method": "browsingContext.userPromptOpened",
  "params": {
    "context": "context-id-1",
    "type": "alert",
    "message": "Are you sure?"
  }
}
```

### network.beforeRequestSent

Emitted when a request is about to be sent.

```json
{
  "type": "event",
  "method": "network.beforeRequestSent",
  "params": {
    "context": "context-id-1",
    "request": {
      "request": "request-id-1",
      "url": "https://example.com",
      "method": "GET"
    }
  }
}
```

### network.responseStarted

Emitted when response headers are received.

```json
{
  "type": "event",
  "method": "network.responseStarted",
  "params": {
    "context": "context-id-1",
    "request": {"request": "request-id-1"},
    "response": {"url": "https://example.com", "status": 200}
  }
}
```

### network.responseCompleted

Emitted when a response finishes loading.

```json
{
  "type": "event",
  "method": "network.responseCompleted",
  "params": {
    "context": "context-id-1",
    "request": {"request": "request-id-1"},
    "response": {"url": "https://example.com", "status": 200}
  }
}
```

### network.dataReceived

Emitted when response body data is received.

```json
{
  "type": "event",
  "method": "network.dataReceived",
  "params": {
    "context": "context-id-1",
    "request": "request-id-1",
    "data": "SGVsbG8="
  }
}
```

### network.fetchError

Emitted when a request fails.

```json
{
  "type": "event",
  "method": "network.fetchError",
  "params": {
    "context": "context-id-1",
    "request": {"request": "request-id-1"},
    "errorText": "net::ERR_CONNECTION_REFUSED"
  }
}
```

### network.authRequired

Emitted when a request requires authentication.

```json
{
  "type": "event",
  "method": "network.authRequired",
  "params": {
    "context": "context-id-1",
    "request": {"request": "request-id-1"},
    "response": {"status": 401}
  }
}
```

### network.samplingStateChanged

Emitted when network sampling mode changes.

```json
{
  "type": "event",
  "method": "network.samplingStateChanged",
  "params": {
    "context": "context-id-1",
    "sampling": "all"
  }
}
```

### browsingContext.navigationCompleted

Emitted when a navigation completes.

```json
{
  "type": "event",
  "method": "browsingContext.navigationCompleted",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "navigation": "nav-id-1"
  }
}
```

### browsingContext.fragmentNavigated

Emitted when fragment navigation occurs (#anchor).

```json
{
  "type": "event",
  "method": "browsingContext.fragmentNavigated",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com#section"
  }
}
```

### browsingContext.domContentLoaded

Emitted when DOM is parsed but resources still loading (before load).

```json
{
  "type": "event",
  "method": "browsingContext.domContentLoaded",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com"
  }
}
```

### browsingContext.load

Emitted when the page finishes loading.

```json
{
  "type": "event",
  "method": "browsingContext.load",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com"
  }
}
```

### browsingContext.historyUpdated

Chrome-specific event emitted when history entries change (pushState, replaceState).

```json
{
  "type": "event",
  "method": "browsingContext.historyUpdated",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com/page"
  }
}
```

### browsingContext.userPromptClosed

Emitted when a dialog (alert/confirm/prompt) is closed.

```json
{
  "type": "event",
  "method": "browsingContext.userPromptClosed",
  "params": {
    "context": "context-id-1",
    "accepted": true,
    "userText": "response text"
  }
}
```

### browsingContext.downloadWillBegin

Emitted when a download starts.

```json
{
  "type": "event",
  "method": "browsingContext.downloadWillBegin",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com/file.zip",
    "filename": "file.zip"
  }
}
```

### browsingContext.downloadEnd

Emitted when a download finishes.

```json
{
  "type": "event",
  "method": "browsingContext.downloadEnd",
  "params": {
    "context": "context-id-1",
    "status": "success",
    "item": "download-id-1"
  }
}
```

### input.fileDialogOpened

Emitted when a file input dialog opens.

```json
{
  "type": "event",
  "method": "input.fileDialogOpened",
  "params": {
    "context": "context-id-1",
    "element": {"sharedId": "element-id-1"},
    "multiple": false
  }
}
```

### storage.cookieChanged

Emitted when a cookie is created, modified, or deleted.

```json
{
  "type": "event",
  "method": "storage.cookieChanged",
  "params": {
    "context": "context-id-1",
    "cookie": {"name": "session", "value": "abc123"}
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
| `no such element` | Element not found |
| `no such cookie` | Cookie not found |
| `stale element reference` | Element reference is stale |
| `element not interactable` | Element not interactable |
| `insecure certificate` | Insecure certificate |
| `move target out of bounds` | Move target out of bounds |
| `no such alert` | No such alert |
| `no such shadow root` | No such shadow root |
| `detached shadow root` | Detached shadow root |
| `invalid web extension` | Invalid web extension |
| `no such user context` | No such user context |

## Mapping to Pydantic models

Each command and event has a corresponding Pydantic model in `protocol/`. Model names follow the pattern:

- Command params: `session.new` → `NewSessionParams`
- Command result: `network.addCacheOverride` → `AddCacheOverrideResult`
- Event: `log.entryAdded` → `LogEntryAddedEvent`
- Response: always `SuccessResponse` or `ErrorResponse`

### Command parameter models

| Command | Params model |
|---|---|
| `session.new` | `NewSessionParams` |
| `network.addIntercept` | `AddInterceptParams` |
| `network.addCacheOverride` | `AddCacheOverrideParams` |
| `network.setCacheOverride` | `SetCacheOverrideParams` |
| `network.responseBody` | `ResponseBodyParams` |
| `storage.deleteCookie` | `DeleteCookieParams` |
| `script.addPreloadScript` | `ScriptAddPreloadScriptParams` |
| `browsingContext.setViewport` | `ViewportSize` |

### Command result models

| Command | Result model |
|---|---|
| `network.addIntercept` | `InterceptResult` |
| `network.addCacheOverride` | `AddCacheOverrideResult` |
| `network.responseBody` | `ResponseBodyResult` |
| `script.addPreloadScript` | `ScriptAddPreloadScriptResult` |
| `browsingContext.getViewport` | `GetViewportResult` |

### Event models

| Event | Event model |
|---|---|
| `log.entryAdded` | `LogEntryAddedEvent` |
| `browsingContext.contextCreated` | `BrowsingContextCreatedEvent` |
| `browsingContext.contextDestroyed` | `BrowsingContextDestroyedEvent` |
| `browsingContext.navigationStarted` | `BrowsingContextNavigationStartedEvent` |
| `browsingContext.navigationAborted` | `BrowsingContextNavigationAbortedEvent` |
| `browsingContext.navigationCommitted` | `BrowsingContextNavigationCommittedEvent` |
| `browsingContext.navigationFailed` | `BrowsingContextNavigationFailedEvent` |
| `browsingContext.userPromptClosed` | `BrowsingContextUserPromptClosedEvent` |
| `browsingContext.downloadWillBegin` | `BrowsingContextDownloadWillBeginEvent` |
| `browsingContext.downloadEnd` | `BrowsingContextDownloadEndEvent` |
| `input.fileDialogOpened` | `InputFileDialogOpenedEvent` |
| `browsingContext.navigationCompleted` | `BrowsingContextNavigationCompletedEvent` |
| `browsingContext.fragmentNavigated` | `BrowsingContextFragmentNavigatedEvent` |
| `browsingContext.domContentLoaded` | `BrowsingContextDOMContentLoadedEvent` |
| `browsingContext.load` | `BrowsingContextLoadEvent` |
| `browsingContext.historyUpdated` | `BrowsingContextHistoryUpdatedEvent` |
| `browsingContext.userPromptOpened` | `BrowsingContextUserPromptOpenedEvent` |
| `script.message` | `ScriptMessageEvent` |
| `script.realmCreated` | `ScriptRealmCreatedEvent` |
| `script.realmDestroyed` | `ScriptRealmDestroyedEvent` |
| `network.beforeRequestSent` | `NetworkBeforeRequestSentEvent` |
| `network.responseStarted` | `NetworkResponseStartedEvent` |
| `network.responseCompleted` | `NetworkResponseCompletedEvent` |
| `network.dataReceived` | `NetworkDataReceivedEvent` |
| `network.fetchError` | `NetworkFetchErrorEvent` |
| `network.authRequired` | `NetworkAuthRequiredEvent` |
| `network.samplingStateChanged` | `NetworkSamplingStateChangedEvent` |
| `storage.cookieChanged` | `StorageCookieChangedEvent` |
