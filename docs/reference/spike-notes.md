# Spike notes — bidiwave

## Objective

Document the findings from the BiDi validation spike with Chrome and Edge.

## Summary

BiDi works correctly for Chrome and Edge using ChromeDriver/EdgeDriver
as a proxy. It is not possible to connect BiDi directly to the browser;
the driver is needed as an intermediary.

## Chrome

- **Browser version**: 149.0.7827.201
- **ChromeDriver**: 149.0.7827.155 (win64)
- **Driver path**: `bin/chromedriver-win64/chromedriver.exe`
- **Driver port**: 9515
- **Flow**:
  1. Launch `chromedriver --port=9515`
  2. POST `http://localhost:9515/session` with `{"capabilities":{"alwaysMatch":{"webSocketUrl":true}}}`
  3. Response includes `value.capabilities.webSocketUrl` → `ws://localhost:9515/session/{sessionId}`
  4. Connect to that URL via WebSocket
  5. Send `session.status` → response `{"type":"success","result":{"ready":false,"message":"already connected"}}`
- **Does it work?**: Yes

## Edge

- **Browser version**: 149.0.4022.98
- **EdgeDriver**: 149.0.4022.98 (win64)
- **Driver path**: `bin/edgedriver/msedgedriver.exe`
- **Driver port**: 9516
- **Flow**: identical to Chrome, using `msedgedriver --port=9516`
- **Does it work?**: Yes

## Differences found

- Chrome and Edge use the same flow (both are Chromium).
- `build.version` differs: Chrome reports `149.0.7827.155`, Edge reports `149.0.4022.98`.
- `session.status` responds `ready: false` and `message: "already connected"` in both cases,
  confirming that the BiDi session is already active when connecting via `webSocketUrl`.

## Additional notes

- The browser's `--remote-debugging-port` exposes CDP, not BiDi. It does not work for direct BiDi.
- The ChromeDriver download URL comes from
  `https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json`
  (milestone 149 → version 149.0.7827.155).
- The EdgeDriver download URL is `https://msedgedriver.microsoft.com/{version}/edgedriver_win64.zip`
  (the old `msedgedriver.azureedge.net` is deprecated).
- Firefox exposes BiDi natively at `ws://127.0.0.1:{port}/session` without needing a driver,
  but was not tested in this spike because it was not installed.
