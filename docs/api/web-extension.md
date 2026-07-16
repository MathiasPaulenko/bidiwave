# Web Extension

The web extension module installs and uninstalls browser extensions.

## Methods

### install

Install a browser extension from an archive file:

```python
result = await client.web_extension.install("/path/to/extension.zip")
print(result.extension)  # extension ID
```

### uninstall

Uninstall a previously installed extension:

```python
await client.web_extension.uninstall("extension-id")
```

## Reference

::: bidiwave.modules.webextension.WebExtensionModule
