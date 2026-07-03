"""Pydantic v2 models for WebDriver BiDi commands."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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


class AddPreloadScriptParams(BaseModel):
    """Parameters for preload.addPreloadScript."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    function_declaration: str
    arguments: list[dict[str, Any]] | None = None
    contexts: list[str] | None = None
    sandbox: str | None = None


class RemovePreloadScriptParams(BaseModel):
    """Parameters for preload.removePreloadScript."""

    model_config = ConfigDict(extra="allow")

    script: str


class SetGeolocationParams(BaseModel):
    """Parameters for emulation.setGeolocationOverride."""

    model_config = ConfigDict(extra="allow")

    coordinates: dict[str, float] | None = None
    contexts: list[str] | None = None


class SetNetworkConditionsParams(BaseModel):
    """Parameters for emulation.setNetworkConditions."""

    model_config = ConfigDict(extra="allow")

    offline: bool | None = None
    download_throughput: int | None = None
    upload_throughput: int | None = None
    latency: int | None = None
    contexts: list[str] | None = None


class SetTimezoneParams(BaseModel):
    """Parameters for emulation.setTimezoneOverride."""

    model_config = ConfigDict(extra="allow")

    timezone: str
    contexts: list[str] | None = None


class SetUserAgentParams(BaseModel):
    """Parameters for emulation.setUserAgentOverride."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    user_agent: str
    accept_language: str | None = None
    platform: str | None = None
    contexts: list[str] | None = None


class SetPermissionParams(BaseModel):
    """Parameters for permissions.setPermission."""

    model_config = ConfigDict(extra="allow")

    descriptor: dict[str, Any]
    state: Literal["granted", "denied", "prompt"]
    contexts: list[str] | None = None
    origin: str | None = None


class GetViewportParams(BaseModel):
    """Parameters for browsingContext.getViewport."""

    model_config = ConfigDict(extra="allow")

    context: str


class AddCacheOverrideParams(BaseModel):
    """Parameters for network.addCacheOverride."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contexts: list[str] | None = None
    url: str | None = None
    method: str | None = None
    status_code: int | None = Field(default=None, alias="statusCode")
    headers: list[dict[str, str]] | None = None
    body: dict[str, Any] | None = None


class RemoveCacheOverrideParams(BaseModel):
    """Parameters for network.removeCacheOverride."""

    model_config = ConfigDict(extra="allow")

    cache: str


class SetCacheOverrideParams(BaseModel):
    """Parameters for network.setCacheOverride.

    Unlike addCacheOverride which returns an ID for later removal,
    setCacheOverride replaces all existing overrides in a single call.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    contexts: list[str] | None = None
    url: str
    method: str = "GET"
    status_code: int = Field(default=200, alias="statusCode")
    headers: list[dict[str, str]] | None = None
    body: str | None = None