"""Response types for BiDi protocol messages.

Per the W3C WebDriver BiDi spec, every command response is either:

    SuccessResponse = {type: "success", id: js-uint, result: ResultData}
    ErrorResponse   = {type: "error", id: js-uint / null,
                       error: ErrorCode, message: text, ?stacktrace: text}
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class SuccessResponse(BaseModel):
    """Successful command response."""

    model_config = ConfigDict(extra="allow")

    type: Literal["success"]
    id: int
    result: dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response to a command.

    `error` carries the ErrorCode string (e.g. "invalid argument"),
    `message` is a human-readable description, and `stacktrace` is
    optionally provided by the remote end. `id` may be null when the
    remote end cannot correlate the error with a command.
    """

    model_config = ConfigDict(extra="allow")

    type: Literal["error"]
    id: int | None
    error: str
    message: str
    stacktrace: str | None = None


def parse_response(data: dict[str, Any]) -> SuccessResponse | ErrorResponse:
    """Parses a raw response dict into the appropriate model."""
    resp_type = data.get("type")
    if resp_type == "success":
        return SuccessResponse.model_validate(data)
    if resp_type == "error":
        return ErrorResponse.model_validate(data)
    raise ValueError(f"Unknown response type: {resp_type}")
