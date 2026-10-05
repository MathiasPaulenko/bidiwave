# WebDriver BiDi protocol reference

Wire formats below follow the W3C WebDriver BiDi spec and match what
bidiwave sends. Commands not listed here (`browsing.*`, `preload.*`,
`network.*CacheOverride`, `network.responseBody`, `network.cancelAuth`,
`network.dataReceived`, `network.samplingStateChanged`,
`storage.cookieChanged`, `browsingContext.getViewport`, `log.clear`)
**do not exist in the spec**.

## Commands

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

Subscribes to events. `events` is required; `contexts` and
`userContexts` scope the subscription.

```json
{
  "id": 3,
  "method": "session.subscribe",
  "params": {
    "events": ["log.entryAdded", "browsingContext.contextCreated"],
    "contexts": ["context-id-1"],
    "userContexts": ["user-context-id-1"]
  }
}
```

### session.unsubscribe

Removes subscriptions — either by event/contexts or by subscription IDs
returned by `session.subscribe` when it was context-scoped.

```json
{
  "id": 4,
  "method": "session.unsubscribe",
  "params": {
    "events": ["log.entryAdded"],
    "contexts": ["context-id-1"]
  }
}
```

```json
{
  "id": 4,
  "method": "session.unsubscribe",
  "params": {
    "subscriptions": ["subscription-id-1"]
  }
}
```

### browsingContext.create

Creates a new context (tab or window).

```json
{
  "id": 5,
  "method": "browsingContext.create",
  "params": {
    "type": "tab"
  }
}
```

### browsingContext.navigate

Navigates to a URL. `wait`: `"none" | "interactive" | "complete"`.

```json
{
  "id": 6,
  "method": "browsingContext.navigate",
  "params": {
    "context": "context-id-1",
    "url": "https://example.com",
    "wait": "complete"
  }
}
```

### browsingContext.reload

```json
{
  "id": 7,
  "method": "browsingContext.reload",
  "params": {
    "context": "context-id-1",
    "ignoreCache": true,
    "wait": "complete"
  }
}
```

### browsingContext.traverseHistory

Steps through history by a numeric `delta` — negative goes back,
positive goes forward. Returns an empty result.

```json
{
  "id": 8,
  "method": "browsingContext.traverseHistory",
  "params": {
    "context": "context-id-1",
    "delta": -1
  }
}
```

### browsingContext.close

```json
{
  "id": 9,
  "method": "browsingContext.close",
  "params": {
    "context": "context-id-1",
    "promptUnload": false
  }
}
```

### browsingContext.activate

```json
{
  "id": 10,
  "method": "browsingContext.activate",
  "params": {
    "context": "context-id-1"
  }
}
```

### browsingContext.getTree

Returns the context tree.

```json
{
  "id": 11,
  "method": "browsingContext.getTree",
  "params": {
    "root": "context-id-1",
    "maxDepth": 2
  }
}
```

### browsingContext.captureScreenshot

`format` is an ImageFormat object, not a bare string. `quality` is a
float in `0.0-1.0` and only meaningful for JPEG.

```json
{
  "id": 12,
  "method": "browsingContext.captureScreenshot",
  "params": {
    "context": "context-id-1",
    "format": {"type": "image/jpeg", "quality": 0.8},
    "clip": {"type": "box", "x": 0, "y": 0, "width": 800, "height": 600},
    "origin": "viewport"
  }
}
```

Response:

```json
{
  "type": "success",
  "id": 12,
  "result": {
    "data": "iVBORw0KGgo..."
  }
}
```

### browsingContext.print

Prints to PDF. Note `background`, not `printBackground`.

```json
{
  "id": 13,
  "method": "browsingContext.print",
  "params": {
    "context": "context-id-1",
    "background": false,
    "orientation": "portrait",
    "scale": 1.0,
    "margin": {"top": 1, "bottom": 1, "left": 1, "right": 1},
    "page": {"width": 8.5, "height": 11},
    "pageRanges": ["1-3"],
    "shrinkToFit": true
  }
}
```

### browsingContext.setViewport

Both `viewport` and `devicePixelRatio` are nullable — send `null` to
reset. Exactly one of `context`/`userContexts` selects the target.

```json
{
  "id": 14,
  "method": "browsingContext.setViewport",
  "params": {
    "context": "context-id-1",
    "viewport": {"width": 1280, "height": 720},
    "devicePixelRatio": 2.0
  }
}
```

### browsingContext.handleUserPrompt

```json
{
  "id": 15,
  "method": "browsingContext.handleUserPrompt",
  "params": {
    "context": "context-id-1",
    "accept": true,
    "userText": "hello"
  }
}
```

### browsingContext.locateNodes

```json
{
  "id": 16,
  "method": "browsingContext.locateNodes",
  "params": {
    "context": "context-id-1",
    "locator": {"type": "css", "value": "div.item"},
    "maxNodeCount": 10
  }
}
```

### script.evaluate

```json
{
  "id": 17,
  "method": "script.evaluate",
  "params": {
    "expression": "document.title",
    "target": {"context": "context-id-1"},
    "awaitPromise": true,
    "resultOwnership": "root",
    "userActivation": false
  }
}
```

`target` can also be `{"realm": "realm-id"}` or
`{"context": "id", "sandbox": "name"}`.

### script.callFunction

```json
{
  "id": 18,
  "method": "script.callFunction",
  "params": {
    "functionDeclaration": "(a, b) => a + b",
    "arguments": [{"type": "number", "value": 2}, {"type": "number", "value": 3}],
    "target": {"context": "context-id-1"},
    "awaitPromise": true
  }
}
```

### script.disown

```json
{
  "id": 19,
  "method": "script.disown",
  "params": {
    "target": {"context": "context-id-1"},
    "handles": ["handle-1", "handle-2"]
  }
}
```

### script.getRealms

```json
{
  "id": 20,
  "method": "script.getRealms",
  "params": {
    "context": "context-id-1",
    "type": "window"
  }
}
```

### script.addPreloadScript

```json
{
  "id": 21,
  "method": "script.addPreloadScript",
  "params": {
    "functionDeclaration": "() => { window.__flag = true; }",
    "contexts": ["context-id-1"],
    "arguments": [{"type": "channel", "value": {"channel": "my-channel"}}]
  }
}
```

### script.removePreloadScript

```json
{
  "id": 22,
  "method": "script.removePreloadScript",
  "params": {
    "script": "script-id"
  }
}
```

### network.addIntercept

```json
{
  "id": 23,
  "method": "network.addIntercept",
  "params": {
    "phases": ["beforeRequestSent"],
    "contexts": ["context-id-1"],
    "urlPatterns": [{"type": "string", "pattern": "https://example.com/*"}]
  }
}
```

### network.removeIntercept

```json
{
  "id": 24,
  "method": "network.removeIntercept",
  "params": {
    "intercept": "intercept-id"
  }
}
```

### network.continueRequest

```json
{
  "id": 25,
  "method": "network.continueRequest",
  "params": {
    "request": "request-id",
    "url": "https://example.com/",
    "method": "POST",
    "headers": [{"name": "X-Custom", "value": {"type": "string", "value": "x"}}],
    "cookies": [{"name": "c", "value": {"type": "string", "value": "v"}}],
    "body": {"type": "base64", "value": "aGVsbG8="}
  }
}
```

### network.continueResponse

```json
{
  "id": 26,
  "method": "network.continueResponse",
  "params": {
    "request": "request-id",
    "statusCode": 200,
    "reasonPhrase": "OK",
    "credentials": {"type": "password", "username": "u", "password": "p"}
  }
}
```

### network.failRequest

```json
{
  "id": 27,
  "method": "network.failRequest",
  "params": {
    "request": "request-id"
  }
}
```

### network.provideResponse

```json
{
  "id": 28,
  "method": "network.provideResponse",
  "params": {
    "request": "request-id",
    "statusCode": 200,
    "reasonPhrase": "OK",
    "headers": [{"name": "Content-Type", "value": {"type": "string", "value": "application/json"}}],
    "body": {"type": "base64", "value": "e30="}
  }
}
```

### network.continueWithAuth

There is no `cancelAuth` command — cancellation is
`continueWithAuth` with `action: "cancel"`.

```json
{
  "id": 29,
  "method": "network.continueWithAuth",
  "params": {
    "request": "request-id",
    "action": "provideCredentials",
    "credentials": {"type": "password", "username": "u", "password": "p"}
  }
}
```

### network.setCacheBehavior

`cacheBehavior` is required: `"default"` restores normal caching,
`"bypass"` skips the HTTP cache.

```json
{
  "id": 30,
  "method": "network.setCacheBehavior",
  "params": {
    "cacheBehavior": "bypass",
    "contexts": ["context-id-1"]
  }
}
```

### network.setExtraHeaders

```json
{
  "id": 31,
  "method": "network.setExtraHeaders",
  "params": {
    "headers": [{"name": "X-Custom", "value": {"type": "string", "value": "v"}}],
    "contexts": ["context-id-1"]
  }
}
```

### network.addDataCollector / getData / disownData / removeDataCollector

Response bodies are fetched through data collectors — there is no
`responseBody` command.

```json
{
  "id": 32,
  "method": "network.addDataCollector",
  "params": {
    "dataTypes": ["response"],
    "maxEncodedDataSize": 1000000,
    "contexts": ["context-id-1"]
  }
}
```

```json
{
  "id": 33,
  "method": "network.getData",
  "params": {
    "request": "request-id",
    "dataType": "response",
    "collector": "collector-id",
    "disown": true
  }
}
```

```json
{
  "id": 34,
  "method": "network.disownData",
  "params": {
    "collector": "collector-id",
    "request": "request-id",
    "dataType": "response"
  }
}
```

```json
{
  "id": 35,
  "method": "network.removeDataCollector",
  "params": {
    "collector": "collector-id"
  }
}
```

### input.performActions

Key actions are `keyDown`/`keyUp` (no `"key"` action). Element origins
use `{"element": {"sharedId": "..."}}`.

```json
{
  "id": 36,
  "method": "input.performActions",
  "params": {
    "context": "context-id-1",
    "actions": [
      {
        "type": "key",
        "id": "keyboard",
        "actions": [
          {"type": "keyDown", "value": "a"},
          {"type": "keyUp", "value": "a"}
        ]
      }
    ]
  }
}
```

### input.releaseActions

```json
{
  "id": 37,
  "method": "input.releaseActions",
  "params": {
    "context": "context-id-1"
  }
}
```

### input.setFiles

The element is an element reference (`{"sharedId": "..."}`), not a
handle.

```json
{
  "id": 38,
  "method": "input.setFiles",
  "params": {
    "context": "context-id-1",
    "element": {"sharedId": "shared-id-1"},
    "files": ["/path/to/file.pdf"]
  }
}
```

### storage.getCookies

`filter` is a CookieFilter; `partition` is a PartitionDescriptor
(`{"type": "context", "context": "..."}` or
`{"type": "storageKey", "userContext": "...", "sourceOrigin": "..."}`).

```json
{
  "id": 39,
  "method": "storage.getCookies",
  "params": {
    "filter": {"name": "session"},
    "partition": {"type": "context", "context": "context-id-1"}
  }
}
```

### storage.setCookie

The cookie value is a BytesValue (`{"type": "string", "value": "..."}`
or `{"type": "base64", "value": "..."}`).

```json
{
  "id": 40,
  "method": "storage.setCookie",
  "params": {
    "cookie": {
      "name": "session",
      "value": {"type": "string", "value": "abc123"},
      "domain": "example.com",
      "path": "/",
      "httpOnly": true,
      "secure": true,
      "sameSite": "strict"
    },
    "partition": {"type": "context", "context": "context-id-1"}
  }
}
```

### storage.deleteCookies

```json
{
  "id": 41,
  "method": "storage.deleteCookies",
  "params": {
    "filter": {"name": "session"},
    "partition": {"type": "context", "context": "context-id-1"}
  }
}
```

### emulation.setGeolocationOverride

`coordinates` and `error` are nullable — send `null` to clear.

```json
{
  "id": 42,
  "method": "emulation.setGeolocationOverride",
  "params": {
    "coordinates": {"latitude": 35.6762, "longitude": 139.6503, "accuracy": 1.0},
    "contexts": ["context-id-1"]
  }
}
```

### emulation.setNetworkConditions

`networkConditions` is required and nullable — `{type: "offline"}` or
`null` to clear. Throughput/latency are not part of the spec.

```json
{
  "id": 43,
  "method": "emulation.setNetworkConditions",
  "params": {
    "networkConditions": {"type": "offline"},
    "contexts": ["context-id-1"]
  }
}
```

### emulation.setTimezoneOverride

```json
{
  "id": 44,
  "method": "emulation.setTimezoneOverride",
  "params": {
    "timezone": "Asia/Tokyo",
    "contexts": ["context-id-1"]
  }
}
```

### emulation.setUserAgentOverride

```json
{
  "id": 45,
  "method": "emulation.setUserAgentOverride",
  "params": {
    "userAgent": "Mozilla/5.0 ...",
    "contexts": ["context-id-1"]
  }
}
```

### emulation.setLocaleOverride

```json
{
  "id": 46,
  "method": "emulation.setLocaleOverride",
  "params": {
    "locale": "fr-FR",
    "contexts": ["context-id-1"]
  }
}
```

### emulation.setScreenOrientationOverride

```json
{
  "id": 47,
  "method": "emulation.setScreenOrientationOverride",
  "params": {
    "screenOrientation": {"natural": "portrait", "type": "portrait-primary"},
    "contexts": ["context-id-1"]
  }
}
```

### permissions.setPermission

`origin` is required per the W3C Permissions spec.

```json
{
  "id": 48,
  "method": "permissions.setPermission",
  "params": {
    "descriptor": {"name": "geolocation"},
    "state": "granted",
    "origin": "https://example.com",
    "userContext": "user-context-id-1"
  }
}
```

### browser.createUserContext

```json
{
  "id": 49,
  "method": "browser.createUserContext",
  "params": {
    "acceptInsecureCerts": true,
    "proxy": {"proxyType": "manual", "httpProxy": "host:8080"}
  }
}
```

### browser.removeUserContext

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

```json
{
  "id": 51,
  "method": "browser.getUserContexts",
  "params": {}
}
```

### webExtension.install

`extensionData` is a union: `{type: "path"|"archivePath"|"base64", ...}`.

```json
{
  "id": 52,
  "method": "webExtension.install",
  "params": {
    "extensionData": {"type": "archivePath", "path": "/path/to/ext.zip"}
  }
}
```

### webExtension.uninstall

```json
{
  "id": 53,
  "method": "webExtension.uninstall",
  "params": {
    "extension": "extension-id"
  }
}
```

### cdp.sendCommand / cdp.getSession (Chromium extension — not W3C)

ChromeDriver/EdgeDriver expose CDP via `cdp.*` methods. These are
driver extensions, not part of the BiDi spec.

```json
{
  "id": 54,
  "method": "cdp.sendCommand",
  "params": {
    "method": "Performance.getMetrics",
    "params": {},
    "session": "cdp-session-id"
  }
}
```

```json
{
  "id": 55,
  "method": "cdp.getSession",
  "params": {
    "context": "context-id-1"
  }
}
```

## Events

### log.entryAdded

```json
{
  "type": "event",
  "method": "log.entryAdded",
  "params": {
    "type": "console",
    "level": "info",
    "source": {"realm": "realm-id", "context": "context-id"},
    "text": "message",
    "timestamp": 1700000000000,
    "method": "log",
    "args": []
  }
}
```

### browsingContext.contextCreated

```json
{
  "type": "event",
  "method": "browsingContext.contextCreated",
  "params": {
    "context": "context-id",
    "url": "about:blank",
    "children": null,
    "clientWindow": "window-id",
    "originalOpener": null,
    "parent": null,
    "userContext": "default"
  }
}
```

### browsingContext.contextDestroyed

Same params shape as `contextCreated`.

### browsingContext.navigationStarted / navigationCommitted / navigationCompleted / navigationFailed / navigationAborted

```json
{
  "type": "event",
  "method": "browsingContext.navigationCompleted",
  "params": {
    "context": "context-id",
    "navigation": "navigation-id",
    "timestamp": 1700000000000,
    "url": "https://example.com/"
  }
}
```

`navigationFailed` adds `"status": "canceled"`; `navigationCompleted`
may include `status` values beyond the base union in some drivers.

### browsingContext.fragmentNavigated / domContentLoaded / load / historyUpdated

```json
{
  "type": "event",
  "method": "browsingContext.load",
  "params": {
    "context": "context-id",
    "navigation": "navigation-id",
    "timestamp": 1700000000000,
    "url": "https://example.com/"
  }
}
```

`historyUpdated` has `{"context", "url"}` only.

### browsingContext.userPromptOpened

```json
{
  "type": "event",
  "method": "browsingContext.userPromptOpened",
  "params": {
    "context": "context-id",
    "handler": "accept",
    "message": "Are you sure?",
    "type": "confirm",
    "defaultValue": ""
  }
}
```

`handler` is `"accept" | "dismiss" | "ignore"`; `type` is
`"alert" | "confirm" | "prompt" | "beforeunload"`.

### browsingContext.userPromptClosed

```json
{
  "type": "event",
  "method": "browsingContext.userPromptClosed",
  "params": {
    "context": "context-id",
    "accepted": true,
    "type": "confirm",
    "userText": ""
  }
}
```

### browsingContext.downloadWillBegin / downloadEnd

```json
{
  "type": "event",
  "method": "browsingContext.downloadWillBegin",
  "params": {
    "context": "context-id",
    "navigation": "navigation-id",
    "timestamp": 1700000000000,
    "suggestedFilename": "file.pdf",
    "url": "https://example.com/file.pdf"
  }
}
```

```json
{
  "type": "event",
  "method": "browsingContext.downloadEnd",
  "params": {
    "context": "context-id",
    "navigation": "navigation-id",
    "timestamp": 1700000000000,
    "status": "complete",
    "url": "https://example.com/file.pdf",
    "filepath": "/downloads/file.pdf"
  }
}
```

`status` is `"complete" | "canceled"`.

### script.message

```json
{
  "type": "event",
  "method": "script.message",
  "params": {
    "channel": "my-channel",
    "data": {"type": "string", "value": "hello"},
    "source": {"realm": "realm-id", "context": "context-id"}
  }
}
```

### script.realmCreated

```json
{
  "type": "event",
  "method": "script.realmCreated",
  "params": {
    "realm": "realm-id",
    "origin": "https://example.com",
    "type": "window",
    "context": "context-id"
  }
}
```

`type` also covers `dedicated-worker`, `service-worker`, `shared-worker`,
`worker`, `paint-worklet`, `audio-worklet`, `worklet`.

### script.realmDestroyed

```json
{
  "type": "event",
  "method": "script.realmDestroyed",
  "params": {
    "realm": "realm-id"
  }
}
```

### network.beforeRequestSent

```json
{
  "type": "event",
  "method": "network.beforeRequestSent",
  "params": {
    "context": "context-id",
    "isBlocked": true,
    "navigation": "navigation-id",
    "redirectCount": 0,
    "request": {
      "request": "request-id",
      "url": "https://example.com/",
      "method": "GET",
      "headers": [],
      "cookies": [],
      "headersSize": 0,
      "bodySize": 0,
      "timings": {}
    },
    "timestamp": 1700000000000,
    "intercepts": ["intercept-id"]
  }
}
```

### network.responseStarted / responseCompleted

```json
{
  "type": "event",
  "method": "network.responseCompleted",
  "params": {
    "context": "context-id",
    "isBlocked": false,
    "navigation": "navigation-id",
    "redirectCount": 0,
    "request": {"request": "request-id", "url": "...", "method": "GET", "headers": [], "cookies": [], "headersSize": 0, "bodySize": 0, "timings": {}},
    "response": {
      "url": "https://example.com/",
      "protocol": "http/1.1",
      "status": 200,
      "statusText": "OK",
      "fromCache": false,
      "headers": [],
      "mimeType": "text/html",
      "bytesReceived": 1024,
      "headersSize": 200,
      "bodySize": 824,
      "content": {"size": 824}
    },
    "timestamp": 1700000000000
  }
}
```

### network.fetchError

```json
{
  "type": "event",
  "method": "network.fetchError",
  "params": {
    "context": "context-id",
    "isBlocked": false,
    "navigation": "navigation-id",
    "redirectCount": 0,
    "request": {"request": "request-id", "url": "...", "method": "GET", "headers": [], "cookies": [], "headersSize": 0, "bodySize": 0, "timings": {}},
    "errorText": "net::ERR_CONNECTION_REFUSED",
    "timestamp": 1700000000000
  }
}
```

### network.authRequired

Same shape as `responseStarted` — an intercepted request awaiting an
auth decision (`network.continueWithAuth`).

### input.fileDialogOpened

```json
{
  "type": "event",
  "method": "input.fileDialogOpened",
  "params": {
    "context": "context-id",
    "element": {"sharedId": "shared-id"},
    "multiple": false
  }
}
```

## Error responses

Errors use the spec shape — `error` holds the code string, `message`
the human-readable detail:

```json
{
  "type": "error",
  "id": 1,
  "error": "no such frame",
  "message": "Context context-id not found",
  "stacktrace": "..."
}
```

## Error codes

| Code | Exception raised |
| ---- | ---------------- |
| `invalid argument` | `InvalidArgumentError` |
| `invalid session id` | `InvalidSessionIdError` |
| `no such alert` | `NoSuchAlertError` |
| `no such element` | `NoSuchElementError` |
| `no such frame` | `NoSuchFrameError` |
| `no such handle` | `NoSuchHandleError` |
| `no such history entry` | `NoSuchHistoryEntryError` |
| `no such intercept` | `NoSuchInterceptError` |
| `no such node` | `NoSuchNodeError` |
| `no such request` | `NoSuchRequestError` |
| `no such script` | `NoSuchScriptError` |
| `no such storage partition` | `NoSuchStoragePartitionError` |
| `no such user context` | `NoSuchUserContextError` |
| `session not created` | `SessionNotCreatedError` |
| `unable to capture screen` | `UnableToCaptureScreenError` |
| `unable to close browsing context` | `UnableToCloseBrowsingContextError` |
| `unable to set file input` | `UnableToSetFileInputError` |
| `underspecified storage partition` | `UnderspecifiedStoragePartitionError` |
| `unknown command` | `UnknownCommandError` |
| `unknown error` | `UnknownBiDiError` |
| `unsupported operation` | `UnsupportedOperationError` |

Anything else maps to `CommandError`.

## Mapping to Pydantic models

### Command result models

| Command | Result model |
| ------- | ------------ |
| `browsingContext.navigate`/`reload` | `Navigation` |
| `browsingContext.getTree` | `GetTreeResult` |
| `browsingContext.captureScreenshot` | `Screenshot` |
| `browsingContext.print` | `PrintResult` |
| `browsingContext.locateNodes` | `LocateNodesResult` |
| `script.evaluate`/`callFunction` | `RemoteValue` subtype |
| `script.getRealms` | `GetRealmsResult` |
| `script.addPreloadScript` | `AddPreloadScriptResult` |
| `network.addIntercept` | `InterceptResult` |
| `network.addDataCollector` | `AddDataCollectorResult` |
| `storage.getCookies` | `GetCookiesResult` → `list[Cookie]` |
| `browser.createUserContext` | `CreateUserContextResult` |
| `browser.getUserContexts` | `GetUserContextsResult` |
| `webExtension.install` | `WebExtensionResult` |
| `session.new` | `Session` |

### Event models

| Event | Model |
| ----- | ----- |
| `log.entryAdded` | `LogEntryAddedEvent` |
| `browsingContext.contextCreated` | `BrowsingContextCreatedEvent` |
| `browsingContext.contextDestroyed` | `BrowsingContextDestroyedEvent` |
| `browsingContext.navigationStarted` | `BrowsingContextNavigationStartedEvent` |
| `browsingContext.navigationCommitted` | `BrowsingContextNavigationCommittedEvent` |
| `browsingContext.navigationCompleted` | `BrowsingContextNavigationCompletedEvent` |
| `browsingContext.navigationFailed` | `BrowsingContextNavigationFailedEvent` |
| `browsingContext.navigationAborted` | `BrowsingContextNavigationAbortedEvent` |
| `browsingContext.fragmentNavigated` | `BrowsingContextFragmentNavigatedEvent` |
| `browsingContext.domContentLoaded` | `BrowsingContextDOMContentLoadedEvent` |
| `browsingContext.load` | `BrowsingContextLoadEvent` |
| `browsingContext.historyUpdated` | `BrowsingContextHistoryUpdatedEvent` |
| `browsingContext.userPromptOpened` | `BrowsingContextUserPromptOpenedEvent` |
| `browsingContext.userPromptClosed` | `BrowsingContextUserPromptClosedEvent` |
| `browsingContext.downloadWillBegin` | `BrowsingContextDownloadWillBeginEvent` |
| `browsingContext.downloadEnd` | `BrowsingContextDownloadEndEvent` |
| `script.message` | `ScriptMessageEvent` |
| `script.realmCreated` | `ScriptRealmCreatedEvent` |
| `script.realmDestroyed` | `ScriptRealmDestroyedEvent` |
| `network.beforeRequestSent` | `NetworkBeforeRequestSentEvent` |
| `network.responseStarted` | `NetworkResponseStartedEvent` |
| `network.responseCompleted` | `NetworkResponseCompletedEvent` |
| `network.fetchError` | `NetworkFetchErrorEvent` |
| `network.authRequired` | `NetworkAuthRequiredEvent` |
| `input.fileDialogOpened` | `InputFileDialogOpenedEvent` |
