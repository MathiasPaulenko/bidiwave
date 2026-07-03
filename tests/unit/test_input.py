"""Unit tests for InputModule."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.input import InputModule
from bidiwave.protocol.results import InputSource

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def input_module(mock_connection: MockConn) -> InputModule:
    return InputModule(mock_connection)


class TestPerformActions:
    async def test_perform_actions_basic(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {"type": "pointerMove", "x": 100, "y": 200},
                    {"type": "pointerDown", "button": 0},
                ],
            ),
        ]
        await input_module.perform_actions("ctx-1", actions)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "input.performActions"
        assert call_args.args[1]["context"] == "ctx-1"
        assert len(call_args.args[1]["actions"]) == 1
        assert call_args.args[1]["actions"][0]["type"] == "pointer"
        assert call_args.args[1]["actions"][0]["id"] == "mouse"

    async def test_perform_actions_multiple_sources(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        actions = [
            InputSource(type="key", id="keyboard", actions=[{"type": "key", "value": "a"}]),
            InputSource(type="pointer", id="mouse", actions=[{"type": "pointerDown", "button": 0}]),
        ]
        await input_module.perform_actions("ctx-1", actions)
        call_args = mock_connection.send_command.call_args
        assert len(call_args.args[1]["actions"]) == 2


class TestReleaseActions:
    async def test_release_actions(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.release_actions("ctx-1")
        mock_connection.send_command.assert_called_once_with(
            "input.releaseActions", {"context": "ctx-1"}
        )


class TestSetFiles:
    async def test_set_files(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.set_files("ctx-1", "elem-1", ["/path/to/file.txt"])
        mock_connection.send_command.assert_called_once_with(
            "input.setFiles",
            {
                "context": "ctx-1",
                "element": {"sharedId": "elem-1"},
                "files": ["/path/to/file.txt"],
            },
        )

    async def test_set_files_multiple(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.set_files(
            "ctx-1", "elem-1", ["/a.txt", "/b.txt"]
        )
        call_args = mock_connection.send_command.call_args
        assert len(call_args.args[1]["files"]) == 2


class TestClick:
    async def test_click_default_button(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.click("ctx-1", 100, 200)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "input.performActions"
        actions = call_args.args[1]["actions"]
        assert actions[0]["type"] == "pointer"
        assert len(actions[0]["actions"]) == 3
        assert actions[0]["actions"][0]["type"] == "pointerMove"
        assert actions[0]["actions"][0]["x"] == 100
        assert actions[0]["actions"][0]["y"] == 200
        assert actions[0]["actions"][1]["type"] == "pointerDown"
        assert actions[0]["actions"][1]["button"] == 0
        assert actions[0]["actions"][2]["type"] == "pointerUp"
        assert actions[0]["actions"][2]["button"] == 0

    async def test_click_right_button(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.click("ctx-1", 50, 50, button=2)
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["actions"][1]["button"] == 2
        assert actions[0]["actions"][2]["button"] == 2


class TestDoubleClick:
    async def test_double_click(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.double_click("ctx-1", 100, 200)
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"][0]["actions"]
        assert len(actions) == 5
        assert actions[0]["type"] == "pointerMove"
        assert actions[1]["type"] == "pointerDown"
        assert actions[2]["type"] == "pointerUp"
        assert actions[3]["type"] == "pointerDown"
        assert actions[4]["type"] == "pointerUp"


class TestTypeText:
    async def test_type_text(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.type_text("ctx-1", "hello")
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["type"] == "key"
        assert len(actions[0]["actions"]) == 5
        assert actions[0]["actions"][0]["value"] == "h"
        assert actions[0]["actions"][4]["value"] == "o"

    async def test_type_text_empty(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.type_text("ctx-1", "")
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert len(actions[0]["actions"]) == 0


class TestPressKey:
    async def test_press_key(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.press_key("ctx-1", "Enter")
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["type"] == "key"
        assert len(actions[0]["actions"]) == 2
        assert actions[0]["actions"][0]["value"] == "Enter"
        assert actions[0]["actions"][1]["value"] == "Enter"


class TestScroll:
    async def test_scroll_vertical(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.scroll("ctx-1", delta_y=500)
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["type"] == "wheel"
        assert actions[0]["actions"][0]["deltaY"] == 500
        assert actions[0]["actions"][0]["deltaX"] == 0

    async def test_scroll_horizontal(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.scroll("ctx-1", delta_x=-200)
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["actions"][0]["deltaX"] == -200

    async def test_scroll_with_duration(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.scroll("ctx-1", delta_y=100, duration=200)
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"]
        assert actions[0]["actions"][0]["duration"] == 200


class TestDragAndDrop:
    async def test_drag_and_drop(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.drag_and_drop(
            "ctx-1", 10, 20, 100, 200, duration=50
        )
        call_args = mock_connection.send_command.call_args
        actions = call_args.args[1]["actions"][0]["actions"]
        assert len(actions) == 4
        assert actions[0]["type"] == "pointerMove"
        assert actions[0]["x"] == 10
        assert actions[0]["y"] == 20
        assert actions[1]["type"] == "pointerDown"
        assert actions[2]["type"] == "pointerMove"
        assert actions[2]["x"] == 100
        assert actions[2]["y"] == 200
        assert actions[2]["duration"] == 50
        assert actions[3]["type"] == "pointerUp"
