"""RemoteValue — models for remote values of the BiDi protocol."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bidiwave.exceptions import JavaScriptError


class RemoteValue(BaseModel):
    """Base for all remote values of the BiDi protocol."""

    model_config = ConfigDict(extra="allow")
    type: str

    @classmethod
    def parse(cls, data: dict[str, Any]) -> RemoteValue:
        """Factory that returns the correct subtype based on type."""
        # script.evaluate/callFunction return {type: "success", result: {...}}
        if data.get("type") == "success":
            if "result" in data:
                data = data["result"]
            else:
                return UndefinedValue.model_validate({"type": "undefined"})
        # JS exception — raise immediately
        if data.get("type") == "exception":
            details = data.get("exceptionDetails", {})
            raise JavaScriptError(
                "javascript error",
                details.get("text", "Unknown JavaScript error"),
            )
        type_name = data.get("type", "")
        match type_name:
            case "string":
                return StringValue.model_validate(data)
            case "number":
                return NumberValue.model_validate(data)
            case "boolean":
                return BooleanValue.model_validate(data)
            case "null":
                return NullValue.model_validate(data)
            case "undefined":
                return UndefinedValue.model_validate(data)
            case "bigint":
                return BigIntValue.model_validate(data)
            case "object":
                return ObjectValue.model_validate(data)
            case "array":
                return ArrayValue.model_validate(data)
            case "symbol" | "function":
                return HandleValue.model_validate(data)
            case "date":
                return DateValue.model_validate(data)
            case "regexp":
                return RegExpValue.model_validate(data)
            case "map":
                return MapValue.model_validate(data)
            case "set":
                return SetValue.model_validate(data)
            case "weakmap":
                return WeakMapValue.model_validate(data)
            case "weakset":
                return WeakSetValue.model_validate(data)
            case "generator":
                return GeneratorValue.model_validate(data)
            case "error":
                return ErrorValue.model_validate(data)
            case "proxy":
                return ProxyValue.model_validate(data)
            case "promise":
                return PromiseValue.model_validate(data)
            case "typedarray":
                return TypedArrayValue.model_validate(data)
            case "arraybuffer":
                return ArrayBufferValue.model_validate(data)
            case "nodelist":
                return NodeListValue.model_validate(data)
            case "htmlcollection":
                return HTMLCollectionValue.model_validate(data)
            case "window":
                return WindowValue.model_validate(data)
            case "node":
                return NodeValue.model_validate(data)
            case "channel":
                return ChannelValue.model_validate(data)
            case _:
                return RemoteValue.model_validate(data)


class StringValue(RemoteValue):
    type: Literal["string"] = "string"
    value: str


class NumberValue(RemoteValue):
    type: Literal["number"] = "number"
    value: int | float


class BooleanValue(RemoteValue):
    type: Literal["boolean"] = "boolean"
    value: bool


class NullValue(RemoteValue):
    type: Literal["null"] = "null"


class UndefinedValue(RemoteValue):
    type: Literal["undefined"] = "undefined"


class BigIntValue(RemoteValue):
    type: Literal["bigint"] = "bigint"
    value: str


class ObjectValue(RemoteValue):
    type: Literal["object"] = "object"
    value: dict[str, Any] | None = None
    handle: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, v: Any) -> dict[str, Any] | None:
        if isinstance(v, list):
            result: dict[str, Any] = {}
            for pair in v:
                if isinstance(pair, list) and len(pair) == 2:
                    key, val = pair
                    if isinstance(val, dict) and val.get("type"):
                        result[key] = RemoteValue.parse(val)
                    elif isinstance(val, dict) and "value" in val:
                        result[key] = val["value"]
                    else:
                        result[key] = val
                else:
                    return v  # type: ignore[return-value]
            return result
        return v  # type: ignore[no-any-return]


class ArrayValue(RemoteValue):
    type: Literal["array"] = "array"
    value: list[Any] | None = None
    handle: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, v: Any) -> list[Any] | None:
        if isinstance(v, list):
            result: list[Any] = []
            for item in v:
                if isinstance(item, dict) and item.get("type"):
                    result.append(RemoteValue.parse(item))
                else:
                    result.append(item)
            return result
        return v  # type: ignore[no-any-return]


class HandleValue(RemoteValue):
    """For functions, symbols and objects with circular references."""

    type: str
    handle: str


class NodeValue(RemoteValue):
    """DOM node reference with sharedId."""

    type: Literal["node"] = "node"
    shared_id: str | None = Field(default=None, alias="sharedId")
    value: dict[str, Any] | None = None
    handle: str | None = None
    node_properties: dict[str, Any] | None = Field(
        default=None, alias="nodeProperties"
    )


class ChannelValue(RemoteValue):
    """Channel for preload script communication."""

    type: Literal["channel"] = "channel"
    value: dict[str, Any] | None = None
    handle: str | None = None


class DateValue(RemoteValue):
    """JavaScript Date object."""

    type: Literal["date"] = "date"
    value: str | None = None
    handle: str | None = None


class RegExpValue(RemoteValue):
    """JavaScript RegExp object."""

    type: Literal["regexp"] = "regexp"
    value: dict[str, Any] | None = None
    handle: str | None = None


class MapValue(RemoteValue):
    """JavaScript Map object — value is list of [key, value] pairs."""

    type: Literal["map"] = "map"
    value: list[list[Any]] | None = None
    handle: str | None = None


class SetValue(RemoteValue):
    """JavaScript Set object — value is list of entries."""

    type: Literal["set"] = "set"
    value: list[Any] | None = None
    handle: str | None = None


class WeakMapValue(RemoteValue):
    """JavaScript WeakMap object — always returned as handle."""

    type: Literal["weakmap"] = "weakmap"
    handle: str | None = None


class WeakSetValue(RemoteValue):
    """JavaScript WeakSet object — always returned as handle."""

    type: Literal["weakset"] = "weakset"
    handle: str | None = None


class GeneratorValue(RemoteValue):
    """JavaScript Generator object — always returned as handle."""

    type: Literal["generator"] = "generator"
    handle: str | None = None


class ErrorValue(RemoteValue):
    """JavaScript Error object."""

    type: Literal["error"] = "error"
    value: dict[str, Any] | None = None
    handle: str | None = None


class ProxyValue(RemoteValue):
    """JavaScript Proxy object — always returned as handle."""

    type: Literal["proxy"] = "proxy"
    handle: str | None = None


class PromiseValue(RemoteValue):
    """JavaScript Promise object — always returned as handle."""

    type: Literal["promise"] = "promise"
    handle: str | None = None


class TypedArrayValue(RemoteValue):
    """JavaScript TypedArray object (Int8Array, Uint8Array, etc.)."""

    type: Literal["typedarray"] = "typedarray"
    value: list[Any] | None = None
    handle: str | None = None


class ArrayBufferValue(RemoteValue):
    """JavaScript ArrayBuffer object."""

    type: Literal["arraybuffer"] = "arraybuffer"
    value: list[Any] | None = None
    handle: str | None = None


class NodeListValue(RemoteValue):
    """DOM NodeList object."""

    type: Literal["nodelist"] = "nodelist"
    value: list[Any] | None = None
    handle: str | None = None


class HTMLCollectionValue(RemoteValue):
    """DOM HTMLCollection object."""

    type: Literal["htmlcollection"] = "htmlcollection"
    value: list[Any] | None = None
    handle: str | None = None


class WindowValue(RemoteValue):
    """Window object — always returned as handle."""

    type: Literal["window"] = "window"
    handle: str | None = None
    value: dict[str, Any] | None = None
