"""Input module for the WebDriver BiDi protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from bidiwave.protocol.constants import (
    INPUT_PERFORM_ACTIONS,
    INPUT_RELEASE_ACTIONS,
    INPUT_SET_FILES,
)
from bidiwave.protocol.results import InputSource
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext

PointerType = Literal["mouse", "pen", "touch"]


class InputModule:
    """Module for simulating user input (keyboard, mouse, scroll).

    Commands:
        - perform_actions — executes a sequence of input actions
        - release_actions — cancels all in-progress actions
        - set_files — selects files on an <input type="file">

    Example:
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {"type": "pointerMove", "x": 100, "y": 200},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await client.input.perform_actions(context, actions)
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def perform_actions(
        self,
        context: BrowsingContext | str,
        actions: list[InputSource],
    ) -> None:
        """Executes a sequence of input actions in a context.

        Args:
            context: BrowsingContext or context ID where to execute actions.
            actions: List of InputSource, each representing a
                virtual device (keyboard, mouse, wheel) with its actions.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "actions": [a.model_dump(by_alias=True, exclude_none=True) for a in actions],
        }
        await self._connection.send_command(INPUT_PERFORM_ACTIONS, params)

    async def release_actions(
        self,
        context: BrowsingContext | str,
    ) -> None:
        """Cancels all in-progress input actions for a context.

        Args:
            context: BrowsingContext or context ID.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(
            INPUT_RELEASE_ACTIONS, {"context": ctx_id}
        )

    async def set_files(
        self,
        context: BrowsingContext | str,
        element: str,
        files: list[str],
    ) -> None:
        """Selects files on an <input type="file"> element.

        Args:
            context: BrowsingContext or context ID.
            element: Shared ID of the file input element.
            files: List of absolute file paths to select.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "element": {"sharedId": element},
            "files": files,
        }
        await self._connection.send_command(INPUT_SET_FILES, params)

    async def click(
        self,
        context: BrowsingContext | str,
        x: int | float,
        y: int | float,
        button: int = 0,
        duration: int = 0,
    ) -> None:
        """Convenience: click at coordinates (x, y).

        Args:
            context: BrowsingContext or context ID.
            x: X coordinate relative to the viewport.
            y: Y coordinate relative to the viewport.
            button: 0 = left, 1 = middle, 2 = right.
            duration: Press duration in ms.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {
                        "type": "pointerMove",
                        "x": x,
                        "y": y,
                        "duration": duration,
                    },
                    {"type": "pointerDown", "button": button},
                    {"type": "pointerUp", "button": button},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def double_click(
        self,
        context: BrowsingContext | str,
        x: int | float,
        y: int | float,
    ) -> None:
        """Convenience: double click at coordinates (x, y).

        Args:
            context: BrowsingContext or context ID.
            x: X coordinate relative to the viewport.
            y: Y coordinate relative to the viewport.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {"type": "pointerMove", "x": x, "y": y},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def type_text(
        self,
        context: BrowsingContext | str,
        text: str,
    ) -> None:
        """Convenience: types text key by key.

        Args:
            context: BrowsingContext or context ID.
            text: Text to type.
        """
        key_actions: list[dict[str, Any]] = []
        for char in text:
            key_actions.append({"type": "key", "value": char})
        actions = [
            InputSource(type="key", id="keyboard", actions=key_actions),
        ]
        await self.perform_actions(context, actions)

    async def press_key(
        self,
        context: BrowsingContext | str,
        key: str,
    ) -> None:
        """Convenience: presses and releases a key.

        Uses the protocol key format (e.g: "Enter", "Tab", "Escape",
        or a literal character like "a").

        Args:
            context: BrowsingContext or context ID.
            key: Key to press (e.g: "Enter", "a", "Escape").
        """
        actions = [
            InputSource(
                type="key",
                id="keyboard",
                actions=[
                    {"type": "key", "value": key},
                    {"type": "key", "value": key},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def scroll(
        self,
        context: BrowsingContext | str,
        delta_x: int = 0,
        delta_y: int = 0,
        x: int = 0,
        y: int = 0,
        duration: int | None = None,
    ) -> None:
        """Convenience: mouse wheel scroll.

        Args:
            context: BrowsingContext or context ID.
            delta_x: Horizontal scroll amount (positive = right).
            delta_y: Vertical scroll amount (positive = down).
            x: X coordinate of the pointer during scroll.
            y: Y coordinate of the pointer during scroll.
            duration: Scroll duration in ms.
        """
        wheel_action: dict[str, Any] = {
            "type": "scroll",
            "x": x,
            "y": y,
            "deltaX": delta_x,
            "deltaY": delta_y,
        }
        if duration is not None:
            wheel_action["duration"] = duration
        actions = [
            InputSource(type="wheel", id="wheel", actions=[wheel_action]),
        ]
        await self.perform_actions(context, actions)

    async def drag_and_drop(
        self,
        context: BrowsingContext | str,
        start_x: int | float,
        start_y: int | float,
        end_x: int | float,
        end_y: int | float,
        duration: int = 100,
    ) -> None:
        """Convenience: drag and drop from (start_x, start_y) to (end_x, end_y).

        Args:
            context: BrowsingContext or context ID.
            start_x: Initial X coordinate.
            start_y: Initial Y coordinate.
            end_x: Final X coordinate.
            end_y: Final Y coordinate.
            duration: Movement duration in ms.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {
                        "type": "pointerMove",
                        "x": start_x,
                        "y": start_y,
                        "duration": 0,
                    },
                    {"type": "pointerDown", "button": 0},
                    {
                        "type": "pointerMove",
                        "x": end_x,
                        "y": end_y,
                        "duration": duration,
                    },
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await self.perform_actions(context, actions)
