"""Regression tests for input module bug fixes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.input import InputModule
from bidiwave.protocol.results import InputSource, PointerAction, WheelAction

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def input_module(mock_connection: MockConn) -> InputModule:
    return InputModule(mock_connection)


class TestInputSourceParameters:
    """Bug 36: InputSource should support parameters field with pointerType per spec."""

    def test_pointer_source_with_parameters(self) -> None:
        source = InputSource(
            type="pointer",
            id="mouse",
            parameters={"pointerType": "mouse"},
            actions=[{"type": "pointerDown", "button": 0}],
        )
        dumped = source.model_dump(by_alias=True, exclude_none=True)
        assert "parameters" in dumped
        assert dumped["parameters"]["pointerType"] == "mouse"

    def test_pointer_source_without_parameters(self) -> None:
        source = InputSource(type="pointer", id="mouse", actions=[])
        dumped = source.model_dump(by_alias=True, exclude_none=True)
        assert "parameters" not in dumped


class TestPointerActionPointerType:
    """Bug 37: PointerAction should support pointerType field per spec."""

    def test_pointer_action_with_pointer_type(self) -> None:
        action = PointerAction(
            type="pointerDown",
            button=0,
            pointer_type="mouse",
        )
        dumped = action.model_dump(by_alias=True, exclude_none=True)
        assert dumped["pointerType"] == "mouse"

    def test_pointer_action_without_pointer_type(self) -> None:
        action = PointerAction(type="pointerDown", button=0)
        dumped = action.model_dump(by_alias=True, exclude_none=True)
        assert "pointerType" not in dumped


class TestPointerActionElementOrigin:
    """Bug 38: PointerAction.origin should support ElementOrigin {type: 'element', element: ...}."""

    def test_origin_element(self) -> None:
        action = PointerAction(
            type="pointerMove",
            origin={"type": "element", "element": {"sharedId": "elem-1"}},
        )
        assert isinstance(action.origin, dict)
        assert action.origin["type"] == "element"

    def test_origin_viewport(self) -> None:
        action = PointerAction(type="pointerMove")
        assert action.origin == "viewport"

    def test_origin_pointer(self) -> None:
        action = PointerAction(type="pointerMove", origin="pointer")
        assert action.origin == "pointer"


class TestPerformActionsWithParameters:
    """Verify perform_actions sends parameters field when present."""

    async def test_perform_actions_with_pointer_parameters(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                parameters={"pointerType": "mouse"},
                actions=[{"type": "pointerDown", "button": 0}],
            ),
        ]
        await input_module.perform_actions("ctx-1", actions)
        params = mock_connection.send_command.call_args.args[1]
        assert params["actions"][0].get("parameters", {}).get("pointerType") == "mouse"


class TestSetFilesElementFormat:
    """Verify set_files element format matches spec SharedReference."""

    async def test_set_files_element_shared_id(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.set_files("ctx-1", "elem-1", ["/path/to/file.txt"])
        params = mock_connection.send_command.call_args.args[1]
        assert params["element"] == {"sharedId": "elem-1"}
