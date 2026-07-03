"""Modelos de eventos del protocolo WebDriver BiDi."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


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
        case _:
            return Event(method=method, params=params)
