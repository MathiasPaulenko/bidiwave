# Preload

The preload module injects JavaScript before page load. For full usage
examples, see [Preload Scripts](../usage/preload.md).

It is a convenience namespace over `script.addPreloadScript` /
`script.removePreloadScript` — use `client.script` directly if you need
`arguments` (channels) or a `sandbox`.

## Methods

### add_script

Inject a function that runs before the page's own scripts:

```python
script_id = await client.preload.add_script(
    "() => { window.myFlag = true; }",
    contexts=["context-id-1"],
)
# script_id = "preload-script-id"
```

Preload scripts can also be scoped to specific user contexts:

```python
script_id = await client.preload.add_script(
    "() => { window.myFlag = true; }",
    user_contexts=["user-context-id-1"],
)
```

### remove_script

Remove a previously added preload script:

```python
await client.preload.remove_script("preload-script-id")
```

## Reference

::: bidiwave.modules.preload.PreloadModule
