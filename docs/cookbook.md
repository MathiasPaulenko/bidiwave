# Cookbook — bidiwave

## Ejemplo 1: Console logger

Capturar todos los console logs de una página.

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
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
        async def on_reconnect():
            print("Reconectado. Recreando sesión...")
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

## Ejemplo 8: Simular input del usuario

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        async with await client.browsing.open("https://example.com") as page:
            ctx = page.context

            # Click en un elemento
            await client.input.click(ctx, x=100, y=200)

            # Escribir texto
            await client.input.type_text(ctx, "Hello, world!")

            # Presionar Enter
            await client.input.press_key(ctx, "Enter")

            # Scroll hacia abajo 500px
            await client.input.scroll(ctx, delta_y=500)

            # Drag and drop
            await client.input.drag_and_drop(ctx, 100, 100, 300, 300)

asyncio.run(main())
```

## Ejemplo 9: Bloquear requests de red

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        # Bloquear todas las requests a dominios de ads
        intercept = await client.network.add_intercept(
            phases=["beforeRequestSent"],
            url_patterns=["*ads.example.com*", "*doubleclick.net*"],
        )

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        # Eliminar el intercept
        await client.network.remove_intercept(intercept.intercept_id)

asyncio.run(main())
```

## Ejemplo 10: Monitorear requests de red

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        requests: list[str] = []

        async def on_request(event):
            url = event.request.url
            method = event.request.method
            requests.append(f"{method} {url}")
            print(f"→ {method} {url}")

        async def on_response(event):
            status = event.response.status
            url = event.request.url
            print(f"← {status} {url}")

        client.on_request(on_request)
        client.on_response(on_response)
        await client.session.subscribe([
            "network.beforeRequestSent",
            "network.responseCompleted",
        ])

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        print(f"\nTotal requests: {len(requests)}")

asyncio.run(main())
```

## Ejemplo 11: Mockear una respuesta HTTP

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    async with await BiDiClient.connect("ws://localhost:9222/session") as client:
        # Intercept en beforeRequestSent
        intercept = await client.network.add_intercept(
            phases=["beforeRequestSent"],
            url_patterns=["*api.example.com/data*"],
        )

        # Cuando se intercepte, proveer una respuesta sintética
        async def on_request(event):
            await client.network.provide_response(
                request=event.request.request,
                status_code=200,
                reason_phrase="OK",
                body="eyJtZXNzYWdlIjogIm1vY2tlZCJ9",  # {"message": "mocked"}
            )

        client.on_request(on_request)

        async with await client.browsing.open("https://example.com") as page:
            await asyncio.sleep(3)

        await client.network.remove_intercept(intercept.intercept_id)

asyncio.run(main())
```
