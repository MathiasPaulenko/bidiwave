# bidiwave

WebDriver BiDi for Python — talk to any browser via W3C standard.

Async-first, cross-browser, type-safe. No Selenium, no CDP.

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

## Quick example

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://example.com") as page:
            result = await page.evaluate("document.title")
            match result:
                case StringValue(value=title):
                    print(f"Title: {title}")

asyncio.run(main())
```

## Next steps

- [Quick Start](quick-start.md) — guía de instalación y primer script
- [API Reference](api/client.md) — referencia completa de la API
- [Cookbook](cookbook.md) — recetas para casos de uso comunes
- [Error Handling](error-handling.md) — guía de manejo de errores
