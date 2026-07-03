# Cookbook — bidiwave

## Ejemplo 1: Console logger

Capturar todos los console logs de una página.

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        logs: list[str] = []

        async def on_log(entry):
            ts = entry.datetime.strftime("%H:%M:%S.%f")[:-3]
            logs.append(f"[{ts}] [{entry.level.upper()}] {entry.text}")
            print(logs[-1])

        client.on("log.entryAdded", on_log)
        await client.session.subscribe(["log.entryAdded"])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(5)

asyncio.run(main())
```

## Ejemplo 2: Screenshot de página completa

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
            print("Screenshot guardado en screenshot.png")

asyncio.run(main())
```

## Ejemplo 3: Extraer datos de una página

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://news.ycombinator.com") as page:
            result = await page.call(
                """() => {
                    const rows = document.querySelectorAll('.athing');
                    return Array.from(rows).slice(0, 10).map(row => {
                        const title = row.querySelector('.titleline > a');
                        return {
                            id: row.id,
                            title: title?.textContent,
                            url: title?.href,
                        };
                    });
                }""",
            )

            for item in result.value:
                print(f"[{item['id']}] {item['title']} — {item['url']}")

asyncio.run(main())
```

## Ejemplo 4: Múltiples tabs en paralelo

```python
import asyncio
from bidiwave import BiDiClient, StringValue

async def scrape_page(client, url):
    async with await client.browsing.open(url) as page:
        result = await page.evaluate("document.title")
        match result:
            case StringValue(value=title):
                return title
            case _:
                return "unknown"

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net",
        ]

        titles = await asyncio.gather(*[scrape_page(client, url) for url in urls])

        for url, title in zip(urls, titles):
            print(f"{url} → {title}")

asyncio.run(main())
```

## Ejemplo 5: Esperar a que un elemento aparezca

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        async with await client.browsing.open("https://example.com") as page:
            found = await page.wait_for_selector("h1", timeout=5)
            print(f"Elemento encontrado: {found}")

asyncio.run(main())
```

## Ejemplo 6: Reconnect handling

```python
import asyncio
from bidiwave import BiDiClient, ClientConfig

async def main():
    config = ClientConfig(max_retries=5)
    async with await BiDiClient.connect("ws://localhost:9222/session", config=config) as client:
        await client.session.new()

        async def on_reconnect():
            print("Reconectado. Recreando sesión...")
            await client.session.new()
            await client.session.subscribe(["log.entryAdded"])

        client.on_reconnect(on_reconnect)

        async def on_disconnect():
            print("Conexión perdida. Reintentando...")

        client.on_disconnect(on_disconnect)

        while True:
            await asyncio.sleep(1)

asyncio.run(main())
```

## Ejemplo 7: Capability-aware code

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        await client.session.new()

        print(f"Browser: {client.capabilities.browser_name} {client.capabilities.browser_version}")
        print(f"Browsing: {client.capabilities.supports_browsing}")
        print(f"Script: {client.capabilities.supports_script}")
        print(f"Network: {client.capabilities.supports_network}")

        if client.capabilities.supports_network:
            # Usar network module
            ...
        else:
            print("Network no soportado en este browser")

asyncio.run(main())
```
