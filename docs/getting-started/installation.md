# Installation

## What is WebDriver BiDi?

WebDriver BiDi is a W3C standard bidirectional protocol for browser
automation. Unlike the classic WebDriver protocol (which is request/response
only), BiDi uses a **WebSocket connection** that allows the browser to push
events to your script in real time — console logs, network requests, navigation
events, and more.

bidiwave is a Python client for this protocol. It does **not** use Selenium,
CDP (Chrome DevTools Protocol), or Playwright. It talks directly to the browser
via the W3C standard, which means it works with any browser that implements
BiDi: Chrome, Edge, and Firefox.

### Architecture

```
Your Python script
       │
       ▼
  bidiwave (WebSocket client)
       │
       ▼
  WebDriver BiDi (W3C standard)
       │
       ▼
  ChromeDriver / EdgeDriver / Firefox (driver process)
       │
       ▼
  Browser (Chrome / Edge / Firefox)
```

The driver process acts as a proxy between bidiwave and the browser. You
launch the driver, it exposes a WebSocket endpoint, and bidiwave connects to
it. Firefox is the exception — it exposes BiDi natively without a driver.

## Requirements

- **Python 3.11 or higher** — bidiwave uses modern features like `match`
  statements and `Self` from `typing`.
- **A browser with BiDi support**:
    - Chrome 111+ (via ChromeDriver)
    - Edge 111+ (via EdgeDriver)
    - Firefox 129+ (native BiDi, no driver needed)
- **A driver process** — Chrome and Edge require a driver (ChromeDriver /
  EdgeDriver) running locally or on a remote host. See
  [Browser Setup](../guides/browser-setup.md) for instructions.

## Install

```bash
pip install bidiwave
```

### Development install

If you want to contribute or run the test suite:

```bash
git clone https://github.com/MathiasPaulenko/bidiwave.git
cd bidiwave
pip install -e ".[dev]"
```

This installs `ruff`, `mypy`, `pytest`, `pytest-asyncio`, and `mkdocs` with
the Material theme.

### Optional extras

| Extra | Description |
| ----  | ----------- |
| `dev` | Ruff, mypy, pytest, pytest-asyncio |
| `docs` | MkDocs + Material theme + mkdocstrings |

## Verify

```python
import bidiwave
print(bidiwave.__version__)
```

You should see the version number printed. If you get an `ImportError`, make
sure your Python version is 3.11+ and the package is installed in the correct
environment.

## Next steps

- [Quick Start](quick-start.md) — your first BiDi script in 5 minutes
- [Browser Setup](../guides/browser-setup.md) — how to launch ChromeDriver,
  EdgeDriver, or Firefox with BiDi
- [Configuration](../usage/configuration.md) — timeouts, reconnection, and
  event queue tuning
