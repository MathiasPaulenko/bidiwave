"""RemoteValue — modelos para valores remotos del protocolo BiDi."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class RemoteValue(BaseModel):
    """Base para todos los valores remotos del protocolo BiDi."""

    model_config = ConfigDict(extra="allow")
    type: str

    @classmethod
    def parse(cls, data: dict[str, Any]) -> RemoteValue:
        """Factory que retorna el subtipo correcto según type."""
        # script.evaluate/callFunction retornan {type: "success", result: {...}}
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
    """Para functions, symbols y objetos con referencias circulares."""

    type: str
    handle: str
