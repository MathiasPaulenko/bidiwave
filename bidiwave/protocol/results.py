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
