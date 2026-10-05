"""Typed result models for modules."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Session(BaseModel):
    """Result of session.new."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    session_id: str = Field(alias="sessionId")
    capabilities: dict[str, Any]


class SessionStatus(BaseModel):
    """Result of session.status."""

    model_config = ConfigDict(extra="allow")
    ready: bool
    message: str | None = None


class Navigation(BaseModel):
    """Result of browsingContext.navigate."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    url: str = ""
    navigation: str | None = None


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
    expires: int | None = Field(default=None, alias="expiry")
    priority: str | None = None
    same_party: bool | None = Field(default=None, alias="sameParty")
    source_scheme: str | None = Field(default=None, alias="sourceScheme")
    source_port: int | None = Field(default=None, alias="sourcePort")

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, v: Any) -> str:
        if isinstance(v, dict):
            return str(v.get("value", ""))
        return str(v)

    @field_validator("same_site", mode="before")
    @classmethod
    def normalize_same_site(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.lower()
        return v


class GetCookiesResult(BaseModel):
    """Result of storage.getCookies."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    cookies: list[Cookie] = []
    partition_key: dict[str, Any] | None = Field(default=None, alias="partitionKey")


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
    """Result of cdp.getSession (Chromium extension)."""

    model_config = ConfigDict(extra="allow")

    session: str | None = None


class AddPreloadScriptResult(BaseModel):
    """Result of script.addPreloadScript."""

    model_config = ConfigDict(extra="allow")

    script: str


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
