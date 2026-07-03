# bidiwave

WebDriver BiDi for Python — talk to any browser via W3C standard.

[![CI](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/test.yml/badge.svg)](https://github.com/MathiasPaulenko/bidiwave/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/bidiwave)](https://pypi.org/project/bidiwave/)
[![Python](https://img.shields.io/pypi/pyversions/bidiwave)](https://pypi.org/project/bidiwave/)
[![License](https://img.shields.io/github/license/MathiasPaulenko/bidiwave)](LICENSE)

## Features

- **W3C WebDriver BiDi** — estándar, no CDP propietario
- **Cross-browser** — Chrome, Firefox, Edge (Safari cuando soporte BiDi)
- **Async-first** — `async/await` nativo con `asyncio`
- **Event streaming** — console logs, navegación, contexts en tiempo real
- **Type-safe** — Pydantic v2 models, type narrowing con `match`
- **Sin dependencias pesadas** — no requiere Selenium, no requiere Playwright

## Install

```bash
pip install bidiwave
```

## Quick start

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://example.com") as page:
            # Evaluar JS
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

            # Screenshot
            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)

asyncio.run(main())
```

## Console log monitoring

```python
async with await BiDiClient.connect(url) as client:
    await client.session.new()

    async def on_log(entry):
        print(f"[{entry.level}] {entry.text}")

    client.on("log.entryAdded", on_log)
    await client.session.subscribe(["log.entryAdded"])

    async with await client.browsing.open("https://example.com") as page:
        await page.evaluate("console.log('hello!')")
        await asyncio.sleep(2)
```

## Lanzar un browser con BiDi

### Chrome

```bash
google-chrome --headless=new --remote-debugging-port=9222 --enable-bidi
```

### Firefox

```bash
firefox --headless --remote-debugging-port=9223 --no-remote
```

## Documentation

- [Quick Start](https://bidiwave.readthedocs.io/quick-start/)
- [API Reference](https://bidiwave.readthedocs.io/api/)
- [Cookbook](https://bidiwave.readthedocs.io/cookbook/)
- [Error Handling](https://bidiwave.readthedocs.io/error-handling/)

## License

MIT
