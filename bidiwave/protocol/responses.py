"""Response models for the WebDriver BiDi protocol."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class ErrorData(BaseModel):
    """Error data in an ErrorResponse."""

    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    stacktrace: str | None = None


class SuccessResponse(BaseModel):
    """Successful response from the browser."""

    model_config = ConfigDict(extra="allow")

    type: Literal["success"]
    id: int
    result: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Error response from the browser."""

    model_config = ConfigDict(extra="allow")

    type: Literal["error"]
    id: int
    error: ErrorData


def parse_response(data: dict[str, Any]) -> SuccessResponse | ErrorResponse:
    """Factory that returns SuccessResponse or ErrorResponse based on the type field."""
    if data.get("type") == "success":
        return SuccessResponse.model_validate(data)
    if data.get("type") == "error":
        return ErrorResponse.model_validate(data)
    msg = f"Unknown response type: {data.get('type')}"
    raise ValueError(msg)