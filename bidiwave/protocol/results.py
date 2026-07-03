"""Modelos de retorno tipados para los módulos."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    context: str | None = None
    url: str
    navigation: str | None = None
    status: str = "complete"


class Screenshot(BaseModel):
    """Resultado de browsing.captureScreenshot."""

    model_config = ConfigDict(extra="allow")
    data: str


class InterceptResult(BaseModel):
    """Resultado de network.addIntercept."""

    model_config = ConfigDict(extra="allow")
    intercept: str


class InputSource(BaseModel):
    """Fuente de input para input.performActions (un dispositivo virtual)."""

    model_config = ConfigDict(extra="allow")

    type: Literal["none", "key", "pointer", "wheel"]
    id: str
    actions: list[dict[str, Any]] = []


class KeyAction(BaseModel):
    """Una acción de teclado individual."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["key"] = "key"
    value: str
    duration: int | None = None


class PointerAction(BaseModel):
    """Una acción de puntero individual (mouse/touch)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["pointer"] = "pointer"
    subtype: Literal[
        "pointerMove",
        "pointerDown",
        "pointerUp",
        "pointerCancel",
    ]
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


class WheelAction(BaseModel):
    """Una acción de scroll individual."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: Literal["wheel"] = "wheel"
    x: int = 0
    y: int = 0
    delta_x: int = Field(default=0, alias="deltaX")
    delta_y: int = Field(default=0, alias="deltaY")
    duration: int | None = None
    origin: Literal["pointer", "viewport"] | dict[str, Any] = "viewport"


class Cookie(BaseModel):
    """Cookie del browser (storage.getCookies / storage.setCookie)."""

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


class GetCookiesResult(BaseModel):
    """Resultado de storage.getCookies."""

    model_config = ConfigDict(extra="allow")

    cookies: list[Cookie] = []


class PrintResult(BaseModel):
    """Resultado de browsingContext.print."""

    model_config = ConfigDict(extra="allow")

    data: str


class LocateNodesResult(BaseModel):
    """Resultado de browsingContext.locateNodes."""

    model_config = ConfigDict(extra="allow")

    nodes: list[dict[str, Any]] = []


class RealmInfo(BaseModel):
    """Información de un realm (script.getRealms)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    realm: str
    origin: str
    type: str
    context: str | None = None
    sandbox: str | None = None


class GetRealmsResult(BaseModel):
    """Resultado de script.getRealms."""

    model_config = ConfigDict(extra="allow")

    realms: list[RealmInfo] = []
