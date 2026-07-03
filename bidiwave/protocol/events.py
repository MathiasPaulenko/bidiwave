"""Modelos de eventos del protocolo WebDriver BiDi."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    """Base para todos los eventos BiDi."""

    model_config = ConfigDict(extra="allow")

    type: str = "event"
    method: str
    params: dict[str, Any] = {}


class LogEntryAddedEvent(BaseModel):
    """Evento log.entryAdded — un console log del browser."""

    model_config = ConfigDict(extra="allow")

    level: Literal["debug", "info", "warn", "error"]
    text: str
    timestamp: int
    source: dict[str, Any]
    type: str = "console"
    args: list[dict[str, Any]] = []


class BrowsingContextCreatedEvent(BaseModel):
    """Evento browsingContext.contextCreated."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    user_context: str = "default"
    original_opener: str | None = None


class BrowsingContextDestroyedEvent(BaseModel):
    """Evento browsingContext.contextDestroyed."""

    model_config = ConfigDict(extra="allow")

    context: str


class BrowsingContextNavigatedEvent(BaseModel):
    """Evento browsingContext.navigationStarted."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    navigation: str | None = None
    status: Literal["pending", "complete", "canceled"] = "pending"


class ScriptMessageEvent(BaseModel):
    """Evento script.message — emitido cuando un script usa script.channel."""

    model_config = ConfigDict(extra="allow")

    realm: str
    source: dict[str, Any]
    channel: str
    data: dict[str, Any]


class NetworkRequestData(BaseModel):
    """Datos de un request de red."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    request: str
    url: str
    method: str
    headers: list[dict[str, str]] = []
    cookies: list[dict[str, Any]] = []
    headers_size: int | None = Field(default=None, alias="headersSize")
    body_size: int | None = Field(default=None, alias="bodySize")
    timings: dict[str, Any] | None = None


class NetworkResponseData(BaseModel):
    """Datos de una respuesta de red."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    url: str
    status: int
    status_text: str = Field(default="", alias="statusText")
    headers: list[dict[str, str]] = []
    mime_type: str = Field(default="", alias="mimeType")
    headers_size: int | None = Field(default=None, alias="headersSize")
    body_size: int | None = Field(default=None, alias="bodySize")
    content: dict[str, Any] | None = None


class NetworkBeforeRequestSentEvent(BaseModel):
    """Evento network.beforeRequestSent — emitido antes de enviar un request."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData
    is_blocked: bool = Field(default=False, alias="isBlocked")
    intercepts: list[str] = []


class NetworkResponseCompletedEvent(BaseModel):
    """Evento network.responseCompleted — emitido cuando un response se completa."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData
    response: NetworkResponseData


class NetworkFetchErrorEvent(BaseModel):
    """Evento network.fetchError — emitido cuando un request falla."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    request: NetworkRequestData
    error_text: str = Field(alias="errorText")


def parse_event(method: str, params: dict[str, Any]) -> BaseModel:
    """Factory que retorna el modelo de evento correcto según method."""
    match method:
        case "log.entryAdded":
            return LogEntryAddedEvent.model_validate(params)
        case "browsingContext.contextCreated":
            return BrowsingContextCreatedEvent.model_validate(params)
        case "browsingContext.contextDestroyed":
            return BrowsingContextDestroyedEvent.model_validate(params)
        case "browsingContext.navigationStarted":
            return BrowsingContextNavigatedEvent.model_validate(params)
        case "script.message":
            return ScriptMessageEvent.model_validate(params)
        case "network.beforeRequestSent":
            return NetworkBeforeRequestSentEvent.model_validate(params)
        case "network.responseCompleted":
            return NetworkResponseCompletedEvent.model_validate(params)
        case "network.fetchError":
            return NetworkFetchErrorEvent.model_validate(params)
        case _:
            return Event(method=method, params=params)
