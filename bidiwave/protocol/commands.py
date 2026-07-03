"""Pydantic v2 models for WebDriver BiDi commands."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class Command(BaseModel):
    """Base command for the BiDi protocol."""

    model_config = ConfigDict(extra="allow")

    id: int
    method: str
    params: dict[str, Any] = {}


class NewSessionParams(BaseModel):
    """Parameters for session.new."""

    model_config = ConfigDict(extra="allow")

    capabilities: dict[str, Any] = {}


class NavigateParams(BaseModel):
    """Parameters for browsing.navigate."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    wait: Literal["none", "interactive", "complete"] = "complete"


class EvaluateParams(BaseModel):
    """Parameters for script.evaluate."""

    model_config = ConfigDict(extra="allow")

    expression: str
    target: dict[str, Any]
    await_promise: bool = False


class ScreenshotParams(BaseModel):
    """Parameters for browsingContext.captureScreenshot."""

    model_config = ConfigDict(extra="allow")

    context: str
    format: Literal["png", "jpeg"] = "png"
    quality: int | None = None


class CallFunctionParams(BaseModel):
    """Parameters for script.callFunction."""

    model_config = ConfigDict(extra="allow")

    function_declaration: str
    args: list[dict[str, Any]] = []
    target: dict[str, Any]
    await_promise: bool = False


class DisownParams(BaseModel):
    """Parameters for script.disown."""

    model_config = ConfigDict(extra="allow")

    handles: list[str]
    target: dict[str, Any]


class GetTreeParams(BaseModel):
    """Parameters for browsingContext.getTree."""

    model_config = ConfigDict(extra="allow")

    root: str | None = None
    max_depth: int | None = None


class SubscribeParams(BaseModel):
    """Parameters for session.subscribe."""

    model_config = ConfigDict(extra="allow")

    events: list[str]
    contexts: list[str] | None = None