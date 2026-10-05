"""Pydantic v2 models for WebDriver BiDi commands.

Modules send most commands as raw dicts (they are simpler to build
conditionally); only models actually used by the public API live here.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


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


class ViewportSize(BaseModel):
    """Viewport dimensions for browsingContext.setViewport.

    Represents the CSS pixel dimensions of the viewport.
    """

    model_config = ConfigDict(extra="allow")

    width: int
    height: int
