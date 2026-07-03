"""Modelos de respuesta del protocolo WebDriver BiDi."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ErrorData(BaseModel):
    """Datos de error en una ErrorResponse."""

    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    stacktrace: str | None = None


class SuccessResponse(BaseModel):
    """Respuesta exitosa del browser."""

    model_config = ConfigDict(extra="allow")

    type: Literal["success"]
    id: int
    result: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Respuesta de error del browser."""

    model_config = ConfigDict(extra="allow")

    type: Literal["error"]
    id: int
    error: ErrorData


def parse_response(data: dict[str, Any]) -> SuccessResponse | ErrorResponse:
    """Factory que retorna SuccessResponse o ErrorResponse según el campo type."""
    if data.get("type") == "success":
        return SuccessResponse.model_validate(data)
    if data.get("type") == "error":
        return ErrorResponse.model_validate(data)
    msg = f"Unknown response type: {data.get('type')}"
    raise ValueError(msg)