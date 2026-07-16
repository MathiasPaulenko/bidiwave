"""Unit tests for locate_nodes, activate, and set_viewport."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.protocol.results import LocateNodesResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def browsing_module(mock_connection: MockConn) -> BrowsingModule:
    return BrowsingModule(mock_connection)


CTX_ID = "ctx-1"


class TestLocateNodes:
    async def test_locate_css(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "nodes": [{"sharedId": "node-1"}, {"sharedId": "node-2"}]
        }
        result = await browsing_module.locate_nodes(
            CTX_ID, {"type": "css", "value": "div.product"}
        )
        assert isinstance(result, LocateNodesResult)
        assert len(result.nodes) == 2
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.locateNodes"
        assert call.args[1]["context"] == CTX_ID
        assert call.args[1]["locator"] == {"type": "css", "value": "div.product"}

    async def test_locate_xpath(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"nodes": []}
        await browsing_module.locate_nodes(
            CTX_ID, {"type": "xpath", "value": "//div[@id='foo']"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["locator"]["type"] == "xpath"

    async def test_locate_with_max_node_count(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"nodes": []}
        await browsing_module.locate_nodes(
            CTX_ID, {"type": "css", "value": "li"}, max_node_count=5
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["maxNodeCount"] == 5

    async def test_locate_with_start_nodes(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"nodes": []}
        start = [{"sharedId": "iframe-1"}]
        await browsing_module.locate_nodes(
            CTX_ID, {"type": "css", "value": "a"}, start_nodes=start
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["startNodes"] == start

    async def test_locate_empty_result(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {}
        result = await browsing_module.locate_nodes(
            CTX_ID, {"type": "css", "value": "div"}
        )
        assert result.nodes == []


    async def test_locate_nodes_with_serialization_options(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"nodes": []}
        await browsing_module.locate_nodes(
            CTX_ID,
            {"type": "css", "value": "div"},
            serialization_options={"maxDomDepth": 1, "includeShadowTree": "all"},
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["serializationOptions"] == {
            "maxDomDepth": 1,
            "includeShadowTree": "all",
        }


class TestActivate:
    async def test_activate(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.activate(CTX_ID)
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.activate", {"context": CTX_ID}
        )


class TestSetViewport:
    async def test_set_viewport_basic(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(
            CTX_ID, viewport={"width": 1920, "height": 1080}
        )
        call = mock_connection.send_command.call_args
        assert call.args[0] == "browsingContext.setViewport"
        assert call.args[1]["context"] == CTX_ID
        assert call.args[1]["viewport"] == {"width": 1920, "height": 1080}

    async def test_set_viewport_with_dpr(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(
            CTX_ID,
            viewport={"width": 800, "height": 600},
            device_pixel_ratio=2.0,
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["devicePixelRatio"] == 2.0

    async def test_set_viewport_reset(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        await browsing_module.set_viewport(CTX_ID, viewport=None)
        params = mock_connection.send_command.call_args.args[1]
        assert "viewport" not in params
        assert "devicePixelRatio" not in params
