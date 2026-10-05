"""Regression tests for input module bug fixes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.input import SPECIAL_KEYS, InputModule
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


class TestInputSourceParameters:
    """InputSource should support parameters field with pointerType per spec."""

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


class TestPressKey:
    """press_key translates friendly names to WebDriver key codepoints."""

    async def test_named_key_translates_to_codepoint(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.press_key("ctx-1", "Enter")
        params = mock_connection.send_command.call_args.args[1]
        actions = params["actions"][0]["actions"]
        assert actions[0]["value"] == SPECIAL_KEYS["Enter"]
        assert actions[1]["value"] == SPECIAL_KEYS["Enter"]

    async def test_single_char_passthrough(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.press_key("ctx-1", "a")
        params = mock_connection.send_command.call_args.args[1]
        actions = params["actions"][0]["actions"]
        assert actions[0]["value"] == "a"

    async def test_raw_codepoint_passthrough(
        self,
        input_module: InputModule,
        mock_connection: MockConn,
    ) -> None:
        await input_module.press_key("ctx-1", "\uE008")
        params = mock_connection.send_command.call_args.args[1]
        actions = params["actions"][0]["actions"]
        assert actions[0]["value"] == "\uE008"

    async def test_unknown_name_raises(
        self,
        input_module: InputModule,
    ) -> None:
        with pytest.raises(ValueError, match="Unknown key"):
            await input_module.press_key("ctx-1", "NotAKey")
