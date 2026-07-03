# Browser Setup

WebDriver BiDi requires a driver process as an intermediary between your script and the browser.

## Chrome

### 1. Download ChromeDriver

Download from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/).

### 2. Launch the driver

```bash
chromedriver --port=9515
```

### 3. Connect

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    # The driver creates a session and returns a WebSocket URL
    # Use bidiwave's connect helper which handles the handshake
    async with await BiDiClient.connect("ws://localhost:9515/session") as client:
        print(f"Connected to {client.capabilities.browser_name}")

asyncio.run(main())
```

## Edge

### 1. Download EdgeDriver

Download from [Microsoft Edge Driver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).

### 2. Launch the driver

```bash
msedgedriver --port=9516
```

### 3. Connect

```python
async with await BiDiClient.connect("ws://localhost:9516/session") as client:
    print(f"Connected to {client.capabilities.browser_name}")
```

## Firefox

Firefox exposes BiDi natively without a driver:

```bash
firefox --headless --remote-debugging-port=9223 --no-remote
```

```python
async with await BiDiClient.connect("ws://127.0.0.1:9223/session") as client:
    print(f"Connected to {client.capabilities.browser_name}")
```

## Headless mode

For CI/CD, launch the browser in headless mode:

=== "Chrome"

    ```bash
    chromedriver --port=9515 --headless=new
    ```

=== "Edge"

    ```bash
    msedgedriver --port=9516 --headless=new
    ```

## Capabilities

Check what the browser supports:

```python
async with await BiDiClient.connect(url) as client:
    caps = client.capabilities
    print(f"Browser: {caps.browser_name} {caps.browser_version}")
    print(f"Browsing: {caps.supports_browsing}")
    print(f"Script: {caps.supports_script}")
    print(f"Network: {caps.supports_network}")
```
