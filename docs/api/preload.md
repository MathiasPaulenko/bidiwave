# Preload

The preload module injects JavaScript before page load. For full usage
examples, see [Preload Scripts](../usage/preload.md).

## Methods

### add_preload_script

Inject a function that runs before the page's own scripts:

```python
result = await client.preload.add_preload_script(
    function_declaration="() => { window.myFlag = true; }",
    contexts=["context-id-1"],
)
# result.script = "preload-script-id"
```

### remove_preload_script

Remove a previously added preload script:

```python
await client.preload.remove_preload_script("preload-script-id")
```

## Reference

::: bidiwave.modules.preload.PreloadModule
