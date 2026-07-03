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