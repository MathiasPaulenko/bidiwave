# Script

## Evaluate an expression

```python
result = await client.script.evaluate(ctx, "document.title")
```

The result is a `RemoteValue` — use `match` for type narrowing:

```python
from bidiwave import StringValue, NumberValue, BooleanValue, NullValue

result = await client.script.evaluate(ctx, "document.title")
match result:
    case StringValue(value=title):
        print(f"Title: {title}")
    case NullValue():
        print("No title")
    case _:
        print(f"Unexpected: {result}")
```

## Await a Promise

```python
result = await client.script.evaluate(
    ctx,
    "new Promise(r => setTimeout(() => r('done'), 1000))",
    await_promise=True,
)
```

## Call a function

```python
result = await client.script.call_function(
    ctx,
    "(a, b) => a + b",
    args=[{"type": "number", "value": 2}, {"type": "number", "value": 3}],
)
```

!!! warning "Driver bug"
    Some drivers (ChromeDriver/EdgeDriver) have a bug with `callFunction` and
    primitive args. If you get `NaN`, use `evaluate` with an inline expression
    instead.

## Disown handles

```python
await client.script.disown(ctx, handles=["handle-id-1"])
```

## RemoteValue types

| Type | Python class |
|---|---|
| `string` | `StringValue` |
| `number` | `NumberValue` |
| `boolean` | `BooleanValue` |
| `bigint` | `BigIntValue` |
| `null` | `NullValue` |
| `undefined` | `UndefinedValue` |
| `object` | `ObjectValue` |
| `array` | `ArrayValue` |
| `symbol` | `HandleValue` |
| `function` | `HandleValue` |
