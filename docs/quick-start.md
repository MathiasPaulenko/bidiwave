# Quick Start

## Instalación

```bash
pip install bidiwave
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

## Hello world

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

## Console log monitoring

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async def on_log(entry):
            print(f"[{entry.level}] {entry.text}")

        client.on("log.entryAdded", on_log)
        await client.session.subscribe(["log.entryAdded"])

        async with await client.browsing.open("https://example.com") as page:
            await page.evaluate("console.log('hello!')")
            await asyncio.sleep(2)

asyncio.run(main())
```

## Screenshot

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://example.com") as page:
            screenshot = await page.screenshot()
            with open("screenshot.png", "wb") as f:
                f.write(screenshot)

asyncio.run(main())
```

## Configuration

```python
from bidiwave import BiDiClient, ClientConfig

config = ClientConfig(
    timeout=60.0,
    max_retries=5,
    retry_delay=1.0,
    retry_backoff=2.0,
    max_queue=1000,
    drop_policy="oldest",
    log_level="INFO",
)

client = await BiDiClient.connect("ws://localhost:9222/session", config=config)
```

## Next steps

- [API Reference](api/client.md) — referencia completa
- [Cookbook](cookbook.md) — más ejemplos
- [Error Handling](error-handling.md) — manejo de errores
