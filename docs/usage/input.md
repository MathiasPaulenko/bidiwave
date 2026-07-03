# Input Simulation

The input module simulates user interactions — mouse clicks, keyboard
typing, scrolling, and drag-and-drop. It uses the WebDriver BiDi
`input.performActions` command, which models input as a sequence of
**actions** grouped by **input source** (virtual device).

## How input works

BiDi models input as a timeline of actions from multiple virtual devices.
Each device is an `InputSource` with a `type`, an `id`, and a list of
actions. All actions from all sources are executed in parallel — like a
real user pressing a key while moving the mouse.

```
InputSource (type="pointer", id="mouse")
  ├── pointerMove to (100, 200)
  ├── pointerDown button 0
  └── pointerUp button 0

InputSource (type="key", id="keyboard")
  ├── key "a"
  ├── key "b"
  └── key "c"
```

### Input source types

| Type | Description | Actions |
| ---- | ----------- | ------- |
| `"pointer"` | Mouse, pen, or touch | `pointerMove`, `pointerDown`, `pointerUp`, `pointerCancel` |
| `"key"` | Keyboard | `key` (press and release) |
| `"wheel"` | Scroll wheel | `scroll` (horizontal and vertical) |
| `"none"` | No-op (used for pauses) | `pause` |

## Convenience methods

bidiwave provides high-level methods for common interactions so you don't
have to build `InputSource` objects manually:

### Click

Click at viewport coordinates (x, y):

```python
await client.input.click(ctx, x=100, y=200)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `x` | `int \| float` | (required) | Viewport X coordinate |
| `y` | `int \| float` | (required) | Viewport Y coordinate |
| `button` | `int` | `0` | 0 = left, 1 = middle, 2 = right |
| `duration` | `int` | `0` | Press duration in ms |

### Double click

```python
await client.input.double_click(ctx, x=100, y=200)
```

### Type text

Types each character as a separate key press. Useful for filling input
fields:

```python
await client.input.type_text(ctx, "Hello, world!")
```

!!! note "Character-by-character"
    `type_text` sends each character individually, which triggers keydown
    and keyup events for each one. This is how a real user types.

### Press a key

Presses and releases a single key. Use the WebDriver key format:

```python
await client.input.press_key(ctx, "Enter")
await client.input.press_key(ctx, "Tab")
await client.input.press_key(ctx, "Escape")
await client.input.press_key(ctx, "a")
```

Common key names: `Enter`, `Tab`, `Escape`, `Backspace`, `Delete`, `ArrowUp`,
`ArrowDown`, `ArrowLeft`, `ArrowRight`, `Home`, `End`, `PageUp`, `PageDown`,
`Space`, `Shift`, `Control`, `Alt`, `Meta`.

### Scroll

```python
# Scroll down 500px
await client.input.scroll(ctx, delta_y=500)

# Scroll right 200px from position (100, 100)
await client.input.scroll(ctx, delta_x=200, x=100, y=100)

# Smooth scroll over 300ms
await client.input.scroll(ctx, delta_y=500, duration=300)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `delta_x` | `int` | `0` | Horizontal scroll (positive = right) |
| `delta_y` | `int` | `0` | Vertical scroll (positive = down) |
| `x` | `int` | `0` | Pointer X position during scroll |
| `y` | `int` | `0` | Pointer Y position during scroll |
| `duration` | `int \| None` | `None` | Scroll duration in ms |

### Drag and drop

Drag from one position to another:

```python
await client.input.drag_and_drop(
    ctx,
    start_x=100, start_y=100,
    end_x=300, end_y=300,
    duration=200,  # smooth drag over 200ms
)
```

## Custom action sequences

For fine-grained control, build `InputSource` objects directly. This lets
you combine multiple devices and control every action:

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

### Pointer actions

| Action type | Parameters | Description |
| ----------- | ---------- | ----------- |
| `pointerMove` | `x`, `y`, `duration`, `origin` | Move pointer to coordinates |
| `pointerDown` | `button` | Press a button (0=left, 1=middle, 2=right) |
| `pointerUp` | `button` | Release a button |
| `pointerCancel` | (none) | Cancel the pointer action |

The `origin` field controls the coordinate system:

- `"viewport"` (default) — coordinates are relative to the viewport
- `"pointer"` — coordinates are relative to the current pointer position
- `{"element-6066-11e4-a52e-4f735466cecf": "shared-id"}` — relative to an element

### Key actions

| Action type | Parameters | Description |
| ----------- | ---------- | ----------- |
| `key` | `value` | Press and release a key |
| `pause` | `duration` | Wait for `duration` ms |

Each `key` action sends a `keydown` followed by a `keyup`. To hold a key
(e.g., Shift while clicking), use two separate actions: `{"type": "key",
"value": "Shift"}` to press, then later `{"type": "key", "value": "Shift"}`
to release.

### Wheel actions

| Action type | Parameters | Description |
| ----------- | ---------- | ----------- |
| `scroll` | `x`, `y`, `deltaX`, `deltaY`, `duration`, `origin` | Scroll at position |

## Release actions

Cancel all in-progress input for a context. This releases any pressed
keys or buttons:

```python
await client.input.release_actions(ctx)
```

Use this if an action sequence fails midway and you want to reset the
input state.

## File upload

Set files on an `<input type="file">` element:

```python
await client.input.set_files(
    ctx,
    element=shared_id,  # shared ID of the input element
    files=["/path/to/file1.pdf", "/path/to/file2.pdf"],
)
```

To get the `shared_id`, evaluate JavaScript to find the element:

```python
from bidiwave import ObjectValue

result = await page.evaluate("document.querySelector('input[type=file]')")
match result:
    case ObjectValue(handle=h) if h:
        await client.input.set_files(ctx, element=h, files=["/path/to/file.pdf"])
        await page.disown([h])
```

!!! note "Firefox only"
    The `input.setFiles` command is only supported by Firefox. Chrome and
    Edge don't implement this BiDi command yet.

## API reference

See [Input API](../api/input.md) for the complete `InputModule` and
`InputSource` reference.
