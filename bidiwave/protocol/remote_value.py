"""RemoteValue — models for remote values of the BiDi protocol."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class RemoteValue(BaseModel):
    """Base for all remote values of the BiDi protocol."""

    model_config = ConfigDict(extra="allow")
    type: str

    @classmethod
    def parse(cls, data: dict[str, Any]) -> RemoteValue:
        """Factory that returns the correct subtype based on type."""
        # script.evaluate/callFunction return {type: "success", result: {...}}
        if data.get("type") == "success" and "result" in data:
            data = data["result"]
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


class ArrayValue(RemoteValue):
    type: Literal["array"] = "array"
    value: list[Any] | None = None
    handle: str | None = None


class HandleValue(RemoteValue):
    """For functions, symbols and objects with circular references."""

    type: str
    handle: str


class NodeValue(RemoteValue):
    """DOM node reference with sharedId."""

    type: Literal["node"] = "node"
    shared_id: str | None = None
    value: dict[str, Any] | None = None
    handle: str | None = None


class ChannelValue(RemoteValue):
    """Channel for preload script communication."""

    type: Literal["channel"] = "channel"
    value: dict[str, Any] | None = None
    handle: str | None = None
