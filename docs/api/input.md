# Input

::: bidiwave.modules.input.InputModule

## Action sources

Actions are grouped by input device type (`InputSource`):

- **`"pointer"`** — mouse, pen, or touch (move, down, up)
- **`"key"`** — keyboard (press, release)
- **`"wheel"`** — scroll (horizontal and vertical)

## Convenience methods

### Click

```python
await client.input.click(context, x=100, y=200)
```

### Double click

```python
await client.input.double_click(context, x=100, y=200)
```

### Type text

```python
await client.input.type_text(context, "Hello, world!")
```

### Press a key

```python
await client.input.press_key(context, "Enter")
```

### Scroll

```python
# Scroll down 500px
await client.input.scroll(context, delta_y=500)
```

### Drag and drop

```python
await client.input.drag_and_drop(
    context,
    start_x=100, start_y=100,
    end_x=300, end_y=300,
    duration=200,
)
```

## Custom action sequences

For fine-grained control, build `InputSource` objects directly:

```python
from bidiwave import InputSource

actions = [
    InputSource(
        type="pointer",
        id="mouse",
        actions=[
            {"type": "pointerMove", "x": 100, "y": 200},
            {"type": "pointerDown", "button": 0},
            {"type": "pointerUp", "button": 0},
        ],
    ),
    InputSource(
        type="key",
        id="keyboard",
        actions=[
            {"type": "key", "value": "a"},
            {"type": "key", "value": "b"},
            {"type": "key", "value": "c"},
        ],
    ),
]

await client.input.perform_actions(context, actions)
```

## Set files

Select files on an `<input type="file">` element:

```python
await client.input.set_files(
    context,
    element=shared_id,
    files=["/path/to/file1.pdf", "/path/to/file2.pdf"],
)
```
