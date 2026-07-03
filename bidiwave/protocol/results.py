"""Modelos de retorno tipados para los módulos."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class Session(BaseModel):
    """Resultado de session.new."""

    model_config = ConfigDict(extra="allow")
    session_id: str
    capabilities: dict[str, Any]


class SessionStatus(BaseModel):
    """Resultado de session.status."""

    model_config = ConfigDict(extra="allow")
    ready: bool
    message: str | None = None


class Navigation(BaseModel):
    """Resultado de browsing.navigate."""

    model_config = ConfigDict(extra="allow")
    context: str
    url: str
    navigation: str | None = None
    status: Literal["pending", "complete", "canceled"]


class Screenshot(BaseModel):
    """Resultado de browsing.captureScreenshot."""

    model_config = ConfigDict(extra="allow")
    data: str


class InterceptResult(BaseModel):
    """Resultado de network.addIntercept."""

    model_config = ConfigDict(extra="allow")
    intercept: str
