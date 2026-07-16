"""Typed result models for modules."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Session(BaseModel):
    """Result of session.new."""

    model_config = ConfigDict(extra="allow")
    session_id: str
    capabilities: dict[str, Any]


class SessionStatus(BaseModel):
    """Result of session.status."""

    model_config = ConfigDict(extra="allow")
    ready: bool
    message: str | None = None


class Navigation(BaseModel):
    """Result of browsing.navigate."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    url: str = ""
    navigation: str | None = None
    status: str = "complete"


class Screenshot(BaseModel):
    """Result of browsing.captureScreenshot."""

    model_config = ConfigDict(extra="allow")
    data: str


class InterceptResult(BaseModel):
    """Result of network.addIntercept."""

    model_config = ConfigDict(extra="allow")
    intercept: str


class InputSource(BaseModel):
    """Input source for input.performActions (a virtual device)."""

    model_config = ConfigDict(extra="allow")

    type: Literal["none", "key", "pointer", "wheel"]
    id: str
    actions: list[dict[str, Any]] = []
    parameters: dict[str, Any] | None = None


class KeyAction(BaseModel):
    """An individual keyboard action."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["keyDown", "keyUp"]
    value: str
    duration: int | None = None


class PointerAction(BaseModel):
    """An individual pointer action (mouse/touch)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["pointerMove", "pointerDown", "pointerUp", "pointerCancel"]
    button: int | None = None
    x: int | float | None = None
    y: int | float | None = None
    width: int | None = None
    height: int | None = None
    pressure: float | None = None
    tangential_pressure: float | None = Field(
        default=None, alias="tangentialPressure"
    )
    tilt_x: int | None = Field(default=None, alias="tiltX")
    tilt_y: int | None = Field(default=None, alias="tiltY")
    twist: int | None = None
    altitude_angle: float | None = Field(
        default=None, alias="altitudeAngle"
    )
    azimuth_angle: float | None = Field(
        default=None, alias="azimuthAngle"
    )
    duration: int | None = None
    origin: Literal["pointer", "viewport"] | dict[str, Any] = "viewport"
    pointer_type: Literal["mouse", "pen", "touch"] | None = Field(
        default=None, alias="pointerType"
    )


class WheelAction(BaseModel):
    """An individual scroll action."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["scroll"] = "scroll"
    x: int = 0
    y: int = 0
    delta_x: int = Field(default=0, alias="deltaX")
    delta_y: int = Field(default=0, alias="deltaY")
    duration: int | None = None
    origin: Literal["pointer", "viewport"] | dict[str, Any] = "viewport"


class Cookie(BaseModel):
    """Browser cookie (storage.getCookies / storage.setCookie)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str
    value: str
    domain: str | None = None
    path: str = "/"
    size: int | None = None
    http_only: bool = Field(default=False, alias="httpOnly")
    secure: bool = False
    same_site: str | None = Field(default=None, alias="sameSite")
    expires: int | None = None
    priority: str | None = None
    same_party: bool | None = Field(default=None, alias="sameParty")
    source_scheme: str | None = Field(default=None, alias="sourceScheme")
    source_port: int | None = Field(default=None, alias="sourcePort")

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, v: Any) -> str:
        if isinstance(v, dict):
            return v.get("value", "")
        return v

    @field_validator("same_site", mode="before")
    @classmethod
    def normalize_same_site(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.lower()
        return v


class GetCookiesResult(BaseModel):
    """Result of storage.getCookies."""

    model_config = ConfigDict(extra="allow")

    cookies: list[Cookie] = []


class PrintResult(BaseModel):
    """Result of browsingContext.print."""

    model_config = ConfigDict(extra="allow")

    data: str


class LocateNodesResult(BaseModel):
    """Result of browsingContext.locateNodes."""

    model_config = ConfigDict(extra="allow")

    nodes: list[dict[str, Any]] = []


class RealmInfo(BaseModel):
    """Information about a realm (script.getRealms)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    realm: str
    origin: str
    type: str
    context: str | None = None
    sandbox: str | None = None


class GetRealmsResult(BaseModel):
    """Result of script.getRealms."""

    model_config = ConfigDict(extra="allow")

    realms: list[RealmInfo] = []


class UserContextInfo(BaseModel):
    """Information about a user context (isolated profile)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    user_context: str = Field(alias="userContext")


class GetUserContextsResult(BaseModel):
    """Result of browser.getUserContexts."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    user_contexts: list[UserContextInfo] = Field(default_factory=list, alias="userContexts")


class CDPGetSessionResult(BaseModel):
    """Result of browser.cdp.getSession."""

    model_config = ConfigDict(extra="allow")

    session: str | None = None


class AddPreloadScriptResult(BaseModel):
    """Result of preload.addPreloadScript."""

    model_config = ConfigDict(extra="allow")

    script: str


class Viewport(BaseModel):
    """Viewport dimensions (browsingContext.getViewport)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    width: int
    height: int
    device_pixel_ratio: float = Field(default=1.0, alias="devicePixelRatio")


class GetViewportResult(BaseModel):
    """Result of browsingContext.getViewport."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    viewport: Viewport
    device_pixel_ratio: float = Field(default=1.0, alias="devicePixelRatio")


class AddCacheOverrideResult(BaseModel):
    """Result of network.addCacheOverride."""

    model_config = ConfigDict(extra="allow")

    cache: str


class ResponseBodyResult(BaseModel):
    """Result of network.responseBody.

    Returns the response body as base64-encoded content with
    the total size of the body.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: str
    total_size: int = Field(default=0, alias="totalSize")


class ScriptAddPreloadScriptResult(BaseModel):
    """Result of script.addPreloadScript.

    Returns the preload script ID and optionally a channel
    for bidirectional communication.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    script: str
    channel: str | None = None


class BrowsingContextInfo(BaseModel):
    """Information about a single browsing context in the tree."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str
    url: str = ""
    user_context: str = Field(default="default", alias="userContext")
    original_opener: str | None = Field(default=None, alias="originalOpener")
    children: list["BrowsingContextInfo"] | None = Field(default=None)


class GetTreeResult(BaseModel):
    """Result of browsingContext.getTree."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contexts: list[BrowsingContextInfo] = Field(default_factory=list)


BrowsingContextInfo.model_rebuild()


class ClientWindowInfo(BaseModel):
    """Information about a browser client window."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    client_window: str = Field(alias="clientWindow")
    state: Literal["normal", "minimized", "maximized", "fullscreen"] = "normal"
    width: int = 0
    height: int = 0
    x: int = 0
    y: int = 0
    active: bool = False


class GetClientWindowsResult(BaseModel):
    """Result of browser.getClientWindows."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    client_windows: list[ClientWindowInfo] = Field(
        default_factory=list, alias="clientWindows"
    )
