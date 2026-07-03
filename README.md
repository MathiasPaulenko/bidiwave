# bidiwave

WebDriver BiDi for Python — talk to any browser via W3C standard.

Async-first, cross-browser, no Selenium, no CDP.

## Install

```bash
pip install bidiwave
```

## Quick start

```python
import asyncio
from bidiwave import BiDiClient

async def main():
    client = await BiDiClient.connect("ws://localhost:9222/session")
    await client.session.new()
    ctx = await client.browsing.create_context()
    await client.browsing.navigate(ctx.id, "https://example.com")
    result = await client.script.evaluate(ctx.id, "document.title")
    print(result.value)
    await client.close()

asyncio.run(main())
```

## License

MIT
