# Permissions

The permissions module grants or denies browser permissions without user
dialogs. For full usage examples, see [Permissions](../usage/permissions.md).

## Methods

### set_permission

Grant, deny, or reset a browser permission:

```python
await client.permissions.set_permission(
    descriptor={"name": "geolocation"},
    state="granted",
    contexts=["context-id-1"],
)
```

## Reference

::: bidiwave.modules.permissions.PermissionsModule
