# Input Simulation

## Action sources

Actions are grouped by input device type (`InputSource`):

- **`"pointer"`** — mouse, pen, or touch (move, down, up)
- **`"key"`** — keyboard (press, release)
- **`"wheel"`** — scroll (horizontal and vertical)

## Convenience methods

### Click

```python
await client.input.click(ctx, x=100, y=200)
```

### Double click

```python
await client.input.double_click(ctx, x=100, y=200)
```

### Type text

```python
await client.input.type_text(ctx, "Hello, world!")
```

### Press a key

```python
await client.input.press_key(ctx, "Enter")
```

Key format: `"Enter"`, `"Tab"`, `"Escape"`, `"a"`, etc.

### Scroll

```python
# Scroll down 500px
await client.input.scroll(ctx, delta_y=500)

# Scroll right 200px from position (100, 100)
await client.input.scroll(ctx, delta_x=200, x=100, y=100)
```

### Drag and drop

```python
await client.input.drag_and_drop(
    ctx,
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

await client.input.perform_actions(ctx, actions)
```

## Release actions

Cancel all in-progress actions:

```python
await client.input.release_actions(ctx)
```

## Set files

Select files on an `<input type="file">` element:

```python
await client.input.set_files(
    ctx,
    element=shared_id,
    files=["/path/to/file1.pdf", "/path/to/file2.pdf"],
)
```
