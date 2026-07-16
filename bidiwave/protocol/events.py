"""Event models for the WebDriver BiDi protocol."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bidiwave.protocol.remote_value import RemoteValue


class Event(BaseModel):
    """Base for all BiDi events."""

    model_config = ConfigDict(extra="allow")

    type: str = "event"
    method: str
    params: dict[str, Any] = {}


class ScriptSource(BaseModel):
    """script.Source — identifies the realm and browsing context of a script."""

    model_config = ConfigDict(extra="allow")

    realm: str | None = None
    context: str | None = None


class LogEntryAddedEvent(BaseModel):
    """log.entryAdded event — a console log from the browser."""

    model_config = ConfigDict(extra="allow")

    level: Literal["debug", "info", "warning", "error"]
    text: str
    timestamp: int
    source: ScriptSource
    type: Literal["console", "javascript"] = "console"
    args: list[RemoteValue] = []
    stack_trace: dict[str, Any] | None = Field(default=None, alias="stackTrace")
    method: str | None = None

    @field_validator("args", mode="before")
    @classmethod
    def normalize_args(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [
                RemoteValue.parse(item) if isinstance(item, dict) and item.get("type") else item
                for item in v
            ]
        return v

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, v: Any) -> Any:
        if v == "warn":
            return "warning"
        return v


class BrowsingContextCreatedEvent(BaseModel):
    """browsingContext.contextCreated event."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    url: str
    user_context: str = Field(default="default", alias="userContext")
    original_opener: str | None = Field(default=None, alias="originalOpener")


class BrowsingContextDestroyedEvent(BaseModel):
    """browsingContext.contextDestroyed event."""

    model_config = ConfigDict(extra="allow")

    context: str


class BrowsingContextNavigationStartedEvent(BaseModel):
    """browsingContext.navigationStarted event."""

    model_config = ConfigDict(extra="allow")

    context: str
    url: str
    navigation: str | None = None
    status: Literal["pending", "complete", "canceled"] = "pending"
    canceled: bool = False


# Backward-compatible alias
BrowsingContextNavigatedEvent = BrowsingContextNavigationStartedEvent


class BrowsingContextNavigationAbortedEvent(BaseModel):
    """browsingContext.navigationAborted event — emitted when a navigation is aborted."""

    model_config = ConfigDict(extra="allow")

    context: str
    navigation: str
    url: str


class BrowsingContextNavigationCommittedEvent(BaseModel):
    """browsingContext.navigationCommitted event — emitted when navigation is committed.

    Fires after the response is received and the new document starts loading.
    """

    model_config = ConfigDict(extra="allow")

    context: str
    navigation: str
    url: str


class BrowsingContextNavigationFailedEvent(BaseModel):
    """browsingContext.navigationFailed event — emitted when a navigation fails."""

    model_config = ConfigDict(extra="allow")

    context: str
    navigation: str
    url: str


class ScriptMessageEvent(BaseModel):
    """script.message event — emitted when a script uses script.channel."""

    model_config = ConfigDict(extra="allow")

    realm: str
    source: ScriptSource
    channel: str
    data: Any


class NetworkRequestData(BaseModel):
    """Network request data."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    request: str
    url: str
    method: str
    headers: list[dict[str, Any]] = []
    cookies: list[dict[str, Any]] = []
    headers_size: int | None = Field(default=None, alias="headersSize")
    body_size: int | None = Field(default=None, alias="bodySize")
    timings: dict[str, Any] | None = None
    initiator: dict[str, Any] | None = None


class NetworkResponseData(BaseModel):
    """Network response data."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    url: str
    status: int
    status_text: str = Field(default="", alias="statusText")
    headers: list[dict[str, Any]] = []
    mime_type: str = Field(default="", alias="mimeType")
    headers_size: int | None = Field(default=None, alias="headersSize")
    body_size: int | None = Field(default=None, alias="bodySize")
    content: dict[str, Any] | None = None
    from_cache: bool = Field(default=False, alias="fromCache")
    from_service_worker: bool = Field(default=False, alias="fromServiceWorker")


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
    type: Literal["window", "dedicated-worker", "shared-worker", "service-worker", "worker"]
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
    handler: Literal["accept", "dismiss", "default"] | None = None
    message: str = ""
    default_value: str = Field(default="", alias="defaultValue")
    type: Literal["alert", "confirm", "prompt", "beforeunload"] = "alert"


class BrowsingContextUserPromptClosedEvent(BaseModel):
    """browsingContext.userPromptClosed event — emitted when a dialog is closed.

    The accepted field is true if the user accepted the dialog, false if dismissed.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    accepted: bool = False
    user_text: str | None = Field(default=None, alias="userText")


class BrowsingContextDownloadWillBeginEvent(BaseModel):
    """browsingContext.downloadWillBegin event — emitted when a download starts.

    Fired before the download begins, allowing interception or cancellation.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    navigation: str | None = None
    url: str
    suggested_filename: str | None = Field(default=None, alias="suggestedFilename")
    user_context: str | None = Field(default=None, alias="userContext")


class BrowsingContextDownloadEndEvent(BaseModel):
    """browsingContext.downloadEnd event — emitted when a download finishes.

    The status field indicates whether the download succeeded or was cancelled.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    navigation: str | None = None
    url: str
    user_context: str | None = Field(default=None, alias="userContext")
    status: Literal["completed", "canceled"] = "completed"
    cancel_reason: str | None = Field(default=None, alias="cancelReason")
    item: str | None = None


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
    data_size: int = Field(default=0, alias="dataSize")


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
    canceled: bool = False


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
    response: NetworkResponseData | None = None


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


class InputFileDialogOpenedEvent(BaseModel):
    """input.fileDialogOpened event — emitted when a file dialog is opened.

    This fires when a file input element triggers a native file dialog,
    allowing the user to set files via input.setFiles instead.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    element: dict[str, Any] | None = None
    multiple: bool = False


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
            return BrowsingContextNavigationStartedEvent.model_validate(params)
        case "browsingContext.navigationAborted":
            return BrowsingContextNavigationAbortedEvent.model_validate(params)
        case "browsingContext.navigationCommitted":
            return BrowsingContextNavigationCommittedEvent.model_validate(params)
        case "browsingContext.navigationFailed":
            return BrowsingContextNavigationFailedEvent.model_validate(params)
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
        case "browsingContext.userPromptClosed":
            return BrowsingContextUserPromptClosedEvent.model_validate(params)
        case "browsingContext.downloadWillBegin":
            return BrowsingContextDownloadWillBeginEvent.model_validate(params)
        case "browsingContext.downloadEnd":
            return BrowsingContextDownloadEndEvent.model_validate(params)
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
        case "input.fileDialogOpened":
            return InputFileDialogOpenedEvent.model_validate(params)
        case _:
            return Event(method=method, params=params)
