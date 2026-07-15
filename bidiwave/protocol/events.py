"""Event models for the WebDriver BiDi protocol."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    """Base for all BiDi events."""

    model_config = ConfigDict(extra="allow")

    type: str = "event"
    method: str
    params: dict[str, Any] = {}


class LogEntryAddedEvent(BaseModel):
    """log.entryAdded event — a console log from the browser."""

    model_config = ConfigDict(extra="allow")

    level: Literal["debug", "info", "warn", "error"]
    text: str
    timestamp: int
    source: dict[str, Any]
    type: str = "console"
    args: list[dict[str, Any]] = []


class BrowsingContextCreatedEvent(BaseModel):
    """browsingContext.contextCreated event."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    user_context: str = "default"
    original_opener: str | None = None


class BrowsingContextDestroyedEvent(BaseModel):
    """browsingContext.contextDestroyed event."""

    model_config = ConfigDict(extra="allow")

    context: str


class BrowsingContextNavigatedEvent(BaseModel):
    """browsingContext.navigationStarted event."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    navigation: str | None = None
    status: Literal["pending", "complete", "canceled"] = "pending"


class ScriptMessageEvent(BaseModel):
    """script.message event — emitted when a script uses script.channel."""

    model_config = ConfigDict(extra="allow")

    realm: str
    source: dict[str, Any]
    channel: str
    data: Any


class NetworkRequestData(BaseModel):
    """Network request data."""

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
    """Network response data."""

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
    """network.beforeRequestSent event — emitted before sending a request."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData
    is_blocked: bool = Field(default=False, alias="isBlocked")
    intercepts: list[str] = []


class NetworkResponseCompletedEvent(BaseModel):
    """network.responseCompleted event — emitted when a response completes."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData
    response: NetworkResponseData


class NetworkFetchErrorEvent(BaseModel):
    """network.fetchError event — emitted when a request fails."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    request: NetworkRequestData
    error_text: str = Field(alias="errorText")


class NetworkResponseStartedEvent(BaseModel):
    """network.responseStarted event — emitted when a response starts.

    Unlike responseCompleted, this fires when headers are received but
    the body may not be fully downloaded yet.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData
    response: NetworkResponseData


class ScriptRealmCreatedEvent(BaseModel):
    """script.realmCreated event — emitted when a new realm is created."""

    model_config = ConfigDict(extra="allow")

    realm: str
    origin: str
    type: str
    context: str | None = None
    sandbox: str | None = None


class ScriptRealmDestroyedEvent(BaseModel):
    """script.realmDestroyed event — emitted when a realm is destroyed."""

    model_config = ConfigDict(extra="allow")

    realm: str


class BrowsingContextUserPromptOpenedEvent(BaseModel):
    """browsingContext.userPromptOpened event — emitted when a dialog opens.

    Dialog types: alert, confirm, prompt, beforeunload.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    handler: str | None = None
    message: str = ""
    default_value: str = Field(default="", alias="defaultValue")
    type: str = "alert"


class NetworkDataReceivedEvent(BaseModel):
    """network.dataReceived event — emitted when response body data arrives.

    Fires in chunks as the response body is received, allowing streaming
    processing of large responses.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    request: str
    redirect_count: int = Field(default=0, alias="redirectCount")
    data: str
    data_size: int = Field(alias="dataSize")


class BrowsingContextNavigationCompletedEvent(BaseModel):
    """browsingContext.navigationCompleted event — emitted when navigation finishes.

    Unlike navigationStarted which fires when navigation begins, this fires
    when the navigation is fully complete (or canceled/failed).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    url: str
    navigation: str | None = None
    status: Literal["pending", "complete", "canceled"] = "complete"


class NetworkAuthRequiredEvent(BaseModel):
    """network.authRequired event — emitted when a request requires authentication.

    The request is blocked until the user provides credentials or the
    interception is handled via continue_with_auth / cancel_auth.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    navigation: str | None = None
    redirect_count: int = Field(default=0, alias="redirectCount")
    request: NetworkRequestData


class BrowsingContextFragmentNavigatedEvent(BaseModel):
    """browsingContext.fragmentNavigated event — emitted on fragment (#anchor) navigation.

    This fires when the URL fragment changes without a full navigation,
    e.g. clicking a link to #section on the same page.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    url: str
    navigation: str | None = None


class BrowsingContextLoadEvent(BaseModel):
    """browsingContext.load event — emitted when the page finishes loading.

    Fires after the window's load event, meaning all resources (images,
    stylesheets, etc.) have been downloaded.
    """

    model_config = ConfigDict(extra="allow")

    context: str
    url: str


class BrowsingContextDOMContentLoadedEvent(BaseModel):
    """browsingContext.domContentLoaded event — emitted when DOM is ready.

    Fires when the document's DOMContentLoaded event occurs, meaning the
    DOM is fully parsed but external resources (images, stylesheets) may
    still be loading. This fires before browsingContext.load.
    """

    model_config = ConfigDict(extra="allow")

    context: str
    url: str


class NetworkSamplingStateChangedEvent(BaseModel):
    """network.samplingStateChanged event — emitted when network sampling changes.

    Sampling determines which requests emit events. When sampling is enabled,
    only a subset of requests trigger network events.
    """

    model_config = ConfigDict(extra="allow")

    context: str | None = None
    sampling: Literal["all", "none"] = "all"


class BrowsingContextHistoryUpdatedEvent(BaseModel):
    """browsingContext.historyUpdated event — emitted when history changes.

    Chrome-specific event fired when the browsing context's history entries
    are updated (e.g. pushState, replaceState, or navigation).
    """

    model_config = ConfigDict(extra="allow")

    context: str
    url: str


def parse_event(method: str, params: dict[str, Any]) -> BaseModel:
    """Factory that returns the correct event model based on method."""
    match method:
        case "log.entryAdded":
            return LogEntryAddedEvent.model_validate(params)
        case "browsingContext.contextCreated":
            return BrowsingContextCreatedEvent.model_validate(params)
        case "browsingContext.contextDestroyed":
            return BrowsingContextDestroyedEvent.model_validate(params)
        case "browsingContext.navigationStarted":
            return BrowsingContextNavigatedEvent.model_validate(params)
        case "browsingContext.navigationCompleted":
            return BrowsingContextNavigationCompletedEvent.model_validate(params)
        case "browsingContext.fragmentNavigated":
            return BrowsingContextFragmentNavigatedEvent.model_validate(params)
        case "browsingContext.domContentLoaded":
            return BrowsingContextDOMContentLoadedEvent.model_validate(params)
        case "browsingContext.load":
            return BrowsingContextLoadEvent.model_validate(params)
        case "browsingContext.historyUpdated":
            return BrowsingContextHistoryUpdatedEvent.model_validate(params)
        case "browsingContext.userPromptOpened":
            return BrowsingContextUserPromptOpenedEvent.model_validate(params)
        case "script.message":
            return ScriptMessageEvent.model_validate(params)
        case "script.realmCreated":
            return ScriptRealmCreatedEvent.model_validate(params)
        case "script.realmDestroyed":
            return ScriptRealmDestroyedEvent.model_validate(params)
        case "network.beforeRequestSent":
            return NetworkBeforeRequestSentEvent.model_validate(params)
        case "network.responseStarted":
            return NetworkResponseStartedEvent.model_validate(params)
        case "network.responseCompleted":
            return NetworkResponseCompletedEvent.model_validate(params)
        case "network.dataReceived":
            return NetworkDataReceivedEvent.model_validate(params)
        case "network.authRequired":
            return NetworkAuthRequiredEvent.model_validate(params)
        case "network.samplingStateChanged":
            return NetworkSamplingStateChangedEvent.model_validate(params)
        case "network.fetchError":
            return NetworkFetchErrorEvent.model_validate(params)
        case _:
            return Event(method=method, params=params)
