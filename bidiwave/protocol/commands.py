"""Modelos Pydantic v2 para comandos WebDriver BiDi."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class Command(BaseModel):
    """Comando base del protocolo BiDi."""

    model_config = ConfigDict(extra="allow")

    id: int
    method: str
    params: dict[str, Any] = {}


class NewSessionParams(BaseModel):
    """Parámetros para session.new."""

    model_config = ConfigDict(extra="allow")

    capabilities: dict[str, Any] = {}


class NavigateParams(BaseModel):
    """Parámetros para browsing.navigate."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    wait: Literal["none", "interactive", "complete"] = "complete"


class EvaluateParams(BaseModel):
    """Parámetros para script.evaluate."""

    model_config = ConfigDict(extra="allow")

    expression: str
    target: dict[str, Any]
    await_promise: bool = False


class ScreenshotParams(BaseModel):
    """Parámetros para browsingContext.captureScreenshot."""

    model_config = ConfigDict(extra="allow")

    context: str
    format: Literal["png", "jpeg"] = "png"
    quality: int | None = None


class CallFunctionParams(BaseModel):
    """Parámetros para script.callFunction."""

    model_config = ConfigDict(extra="allow")

    function_declaration: str
    args: list[dict[str, Any]] = []
    target: dict[str, Any]
    await_promise: bool = False


class DisownParams(BaseModel):
    """Parámetros para script.disown."""

    model_config = ConfigDict(extra="allow")

    handles: list[str]
    target: dict[str, Any]


class GetTreeParams(BaseModel):
    """Parámetros para browsingContext.getTree."""

    model_config = ConfigDict(extra="allow")

    root: str | None = None
    max_depth: int | None = None


class SubscribeParams(BaseModel):
    """Parámetros para session.subscribe."""

    model_config = ConfigDict(extra="allow")

    events: list[str]
    contexts: list[str] | None = None