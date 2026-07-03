# Browser Setup

WebDriver BiDi requires a **driver process** — a small executable that
acts as a proxy between bidiwave and the browser. The driver receives
WebSocket connections, translates BiDi commands, and controls the browser.

Each browser has its own driver:

| Browser | Driver | BiDi support |
| ------- | ------ | ------------ |
| Chrome | ChromeDriver | Chrome 111+ |
| Edge | EdgeDriver | Edge 111+ |
| Firefox | (none — native BiDi) | Firefox 129+ |

## Chrome

### 1. Download ChromeDriver

Download the version that matches your Chrome installation from
[Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/).

To check your Chrome version, open `chrome://version` in the browser.

### 2. Launch the driver

```bash
chromedriver --port=9515
```

The driver starts listening on port 9515. You can choose any free port —
just make sure bidiwave connects to the same one.

### 3. Connect

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        print(f"Connected to {client.capabilities.browser_name}")
        # ... your code ...

asyncio.run(main())
```

### How the handshake works

When bidiwave connects to `ws://localhost:9515/session`:

1. ChromeDriver accepts the WebSocket connection.
2. bidiwave sends a `session.new` command with `{"webSocketUrl": true}`.
3. ChromeDriver creates a BiDi session and returns the WebSocket URL for
   BiDi communication.
4. bidiwave switches to the BiDi WebSocket and starts the receive loop.

You don't need to handle this manually — `BiDiClient.connect()` does it
all.

## Edge

### 1. Download EdgeDriver

Download from
[Microsoft Edge Driver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
Match the version to your Edge installation.

### 2. Launch the driver

```bash
msedgedriver --port=9516
```

### 3. Connect

```python
async with await BiDiClient.connect("ws://localhost:9516/session") as client:
    print(f"Connected to {client.capabilities.browser_name}")
```

### Edge-specific notes

Edge is based on Chromium, so its BiDi support is identical to Chrome's.
The same driver bugs that affect ChromeDriver also affect EdgeDriver
(notably the `callFunction` bug with primitive arguments — see
[Script](../usage/script.md#call_function)).

## Firefox

Firefox implements BiDi natively — no driver process needed. You launch
Firefox directly with remote debugging enabled:

```bash
firefox --headless --remote-debugging-port=9223 --no-remote
```

- `--headless` — run without a visible window (for CI/CD)
- `--remote-debugging-port=9223` — enable remote debugging on port 9223
- `--no-remote` — start a new Firefox instance instead of connecting to
  an existing one

### Connect

```python
async with await BiDiClient.connect("ws://127.0.0.1:9223/session") as client:
    print(f"Connected to {client.capabilities.browser_name}")
```

### Firefox advantages

Firefox has the most complete BiDi implementation:

- **Network interception** — fully supported (Chrome/Edge have partial
  support)
- **Input simulation** — fully supported including `setFiles`
- **No driver process** — simpler setup, fewer moving parts

## Headless mode

For CI/CD pipelines and automated testing, run the browser in headless
mode (no visible window):

=== "Chrome"

    ```bash
    chromedriver --port=9515 --headless=new
    ```

    The `=new` flag uses Chrome's new headless mode, which is more
    faithful to the real browser than the old headless mode.

=== "Edge"

    ```bash
    msedgedriver --port=9516 --headless=new
    ```

=== "Firefox"

    Firefox headless is controlled by the `--headless` flag when
    launching the browser (shown above).

## Remote drivers

You can connect to a driver running on a remote machine (e.g., in a
Docker container or a Selenium Grid):

```python
async with await BiDiClient.connect("ws://driver-host:9515/session") as client:
    # ...
```

Make sure the driver port is accessible from your machine (firewall,
network, etc.).

## Capabilities

After connecting, `client.capabilities` tells you what the browser
supports:

```python
async with await BiDiClient.connect(url) as client:
    caps = client.capabilities
    print(f"Browser: {caps.browser_name} {caps.browser_version}")
    print(f"Platform: {caps.platform_name}")
    print(f"Vendor: {caps.vendor}")
    print(f"Browsing: {caps.supports_browsing}")
    print(f"Script: {caps.supports_script}")
    print(f"Network: {caps.supports_network}")
    print(f"Input: {caps.supports_input}")
```

### Capability fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `browser_name` | `str` | `"chrome"`, `"MicrosoftEdge"`, `"firefox"` |
| `browser_version` | `str` | Full version string (e.g., `"131.0.6778.87"`) |
| `platform_name` | `str` | OS platform (e.g., `"windows"`, `"linux"`) |
| `vendor` | `str` | Browser vendor |
| `supports_browsing` | `bool` | Browsing context commands available |
| `supports_script` | `bool` | Script evaluation available |
| `supports_network` | `bool` | Network interception available (Firefox only currently) |
| `supports_input` | `bool` | Input simulation available (Firefox only currently) |

### Capability-aware code

Write code that adapts to the browser's capabilities:

```python
if client.capabilities.supports_network:
    await client.network.add_intercept(...)
else:
    print("Network interception not supported on this browser")
```

## Troubleshooting

### "Connection refused"

The driver isn't running or is on a different port. Check:

1. The driver process is running (`tasklist | findstr chromedriver` on
   Windows, `ps aux | grep chromedriver` on Linux).
2. The port matches between the driver and your `connect()` call.
3. No firewall is blocking the port.

### "Handshake failed"

The driver started but the BiDi handshake failed. Common causes:

- **Wrong Chrome/ChromeDriver version** — the driver version must match
  the browser version exactly.
- **BiDi not enabled** — some older drivers don't support BiDi. Make
  sure you're using Chrome 111+ / Edge 111+ / Firefox 129+.

### "Session not found"

The WebSocket URL returned by the driver is stale. This can happen if
the driver was restarted while bidiwave was connected. Use the
reconnection feature (see [Configuration](../usage/configuration.md)).
