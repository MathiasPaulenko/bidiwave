"""Unit tests for PreloadModule, EmulationModule, PermissionsModule, LogModule, and getViewport."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.browsing import BrowsingModule
from bidiwave.modules.emulation import EmulationModule
from bidiwave.modules.log import LogModule
from bidiwave.modules.permissions import PermissionsModule
from bidiwave.modules.preload import PreloadModule
from bidiwave.modules.script import ScriptModule
from bidiwave.modules.webextension import WebExtensionModule
from bidiwave.protocol.results import Viewport

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def preload_module(mock_connection: MockConn) -> PreloadModule:
    return PreloadModule(mock_connection)


@pytest.fixture
def emulation_module(mock_connection: MockConn) -> EmulationModule:
    return EmulationModule(mock_connection)


@pytest.fixture
def permissions_module(mock_connection: MockConn) -> PermissionsModule:
    return PermissionsModule(mock_connection)


@pytest.fixture
def log_module(mock_connection: MockConn) -> LogModule:
    return LogModule(mock_connection)


@pytest.fixture
def browsing_module(mock_connection: MockConn) -> BrowsingModule:
    script = ScriptModule(mock_connection)
    return BrowsingModule(mock_connection, script_module=script)


@pytest.fixture
def web_extension_module(mock_connection: MockConn) -> WebExtensionModule:
    return WebExtensionModule(mock_connection)


class TestPreloadAddScript:
    async def test_add_script_basic(
        self,
        preload_module: PreloadModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-1"}
        result = await preload_module.add_script("() => { window.x = 1; }")
        assert result == "preload-1"
        mock_connection.send_command.assert_called_once_with(
            "preload.addPreloadScript",
            {"functionDeclaration": "() => { window.x = 1; }"},
        )

    async def test_add_script_with_arguments(
        self,
        preload_module: PreloadModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-2"}
        result = await preload_module.add_script(
            "(v) => { window.x = v; }",
            arguments=[{"type": "string", "value": "hello"}],
        )
        assert result == "preload-2"
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "preload.addPreloadScript"
        assert call_args.args[1]["arguments"] == [{"type": "string", "value": "hello"}]

    async def test_add_script_with_contexts_and_sandbox(
        self,
        preload_module: PreloadModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-3"}
        await preload_module.add_script(
            "() => {}",
            contexts=["ctx-1", "ctx-2"],
            sandbox="my-sandbox",
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["contexts"] == ["ctx-1", "ctx-2"]
        assert call_args.args[1]["sandbox"] == "my-sandbox"

    async def test_add_script_with_user_contexts(
        self,
        preload_module: PreloadModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"script": "preload-4"}
        await preload_module.add_script(
            "() => {}",
            user_contexts=["uc-1", "uc-2"],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["userContexts"] == ["uc-1", "uc-2"]


class TestPreloadRemoveScript:
    async def test_remove_script(
        self,
        preload_module: PreloadModule,
        mock_connection: MockConn,
    ) -> None:
        await preload_module.remove_script("preload-1")
        mock_connection.send_command.assert_called_once_with(
            "preload.removePreloadScript", {"script": "preload-1"}
        )


class TestEmulationGeolocation:
    async def test_set_geolocation(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_geolocation(
            coordinates={"latitude": 37.77, "longitude": -122.42},
            contexts=["ctx-1"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setGeolocationOverride"
        assert call_args.args[1]["coordinates"] == {
            "latitude": 37.77,
            "longitude": -122.42,
        }
        assert call_args.args[1]["contexts"] == ["ctx-1"]

    async def test_set_geolocation_clear(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_geolocation()
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setGeolocationOverride"
        assert call_args.args[1] == {}

    async def test_set_geolocation_with_user_contexts(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_geolocation(
            coordinates={"latitude": 40.0, "longitude": -74.0},
            user_contexts=["uc-1", "uc-2"],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["userContexts"] == ["uc-1", "uc-2"]

    async def test_set_geolocation_with_error(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_geolocation(
            error={"type": "positionUnavailable"},
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["error"] == {"type": "positionUnavailable"}
        assert "coordinates" not in params


class TestEmulationNetworkConditions:
    async def test_set_network_offline(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_network_conditions(offline=True)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setNetworkConditions"
        assert call_args.args[1]["offline"] is True

    async def test_set_network_throttle(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_network_conditions(
            download_throughput=50000,
            upload_throughput=20000,
            latency=100,
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["downloadThroughput"] == 50000
        assert call_args.args[1]["uploadThroughput"] == 20000
        assert call_args.args[1]["latency"] == 100


class TestEmulationTimezone:
    async def test_set_timezone(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_timezone("America/New_York")
        mock_connection.send_command.assert_called_once_with(
            "emulation.setTimezoneOverride",
            {"timezone": "America/New_York"},
        )

    async def test_set_timezone_with_user_contexts(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_timezone(
            "Europe/London",
            user_contexts=["uc-1"],
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["timezone"] == "Europe/London"
        assert params["userContexts"] == ["uc-1"]


class TestEmulationUserAgent:
    async def test_set_user_agent(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_user_agent(
            "MyBot/1.0",
            accept_language="en-US",
            platform="Windows",
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setUserAgentOverride"
        assert call_args.args[1]["userAgent"] == "MyBot/1.0"
        assert call_args.args[1]["acceptLanguage"] == "en-US"
        assert call_args.args[1]["platform"] == "Windows"


class TestEmulationLocale:
    async def test_set_locale(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_locale("fr-FR", contexts=["ctx-1"])
        mock_connection.send_command.assert_called_once_with(
            "emulation.setLocaleOverride",
            {"locale": "fr-FR", "contexts": ["ctx-1"]},
        )

    async def test_set_locale_with_user_contexts(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_locale("en-US", user_contexts=["uc-1"])
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setLocaleOverride"
        assert call_args.args[1]["locale"] == "en-US"
        assert call_args.args[1]["userContexts"] == ["uc-1"]

    async def test_set_locale_clear(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_locale()
        mock_connection.send_command.assert_called_once_with(
            "emulation.setLocaleOverride", {}
        )


class TestEmulationScreenOrientation:
    async def test_set_screen_orientation(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_screen_orientation(
            {"type": "portraitPrimary", "angle": 0},
            contexts=["ctx-1"],
        )
        mock_connection.send_command.assert_called_once_with(
            "emulation.setScreenOrientationOverride",
            {"orientation": {"type": "portraitPrimary", "angle": 0},
             "contexts": ["ctx-1"]},
        )

    async def test_set_screen_orientation_with_user_contexts(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_screen_orientation(
            {"type": "landscapePrimary"},
            user_contexts=["uc-1"],
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "emulation.setScreenOrientationOverride"
        assert call_args.args[1]["orientation"]["type"] == "landscapePrimary"
        assert call_args.args[1]["userContexts"] == ["uc-1"]

    async def test_set_screen_orientation_clear(
        self,
        emulation_module: EmulationModule,
        mock_connection: MockConn,
    ) -> None:
        await emulation_module.set_screen_orientation()
        mock_connection.send_command.assert_called_once_with(
            "emulation.setScreenOrientationOverride", {}
        )


class TestPermissionsSet:
    async def test_set_permission_granted(
        self,
        permissions_module: PermissionsModule,
        mock_connection: MockConn,
    ) -> None:
        await permissions_module.set_permission(
            descriptor={"name": "geolocation"},
            state="granted",
            contexts=["ctx-1"],
        )
        mock_connection.send_command.assert_called_once_with(
            "permissions.setPermission",
            {
                "descriptor": {"name": "geolocation"},
                "state": "granted",
                "contexts": ["ctx-1"],
            },
        )

    async def test_set_permission_with_origin(
        self,
        permissions_module: PermissionsModule,
        mock_connection: MockConn,
    ) -> None:
        await permissions_module.set_permission(
            descriptor={"name": "notifications"},
            state="denied",
            origin="https://example.com",
        )
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["origin"] == "https://example.com"
        assert "contexts" not in call_args.args[1]


class TestLogClear:
    async def test_clear_all(
        self,
        log_module: LogModule,
        mock_connection: MockConn,
    ) -> None:
        await log_module.clear()
        mock_connection.send_command.assert_called_once_with(
            "log.clear", {}
        )

    async def test_clear_context(
        self,
        log_module: LogModule,
        mock_connection: MockConn,
    ) -> None:
        await log_module.clear("ctx-1")
        mock_connection.send_command.assert_called_once_with(
            "log.clear", {"context": "ctx-1"}
        )


class TestGetViewport:
    async def test_get_viewport(
        self,
        browsing_module: BrowsingModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "viewport": {"width": 1920, "height": 1080, "devicePixelRatio": 2.0},
        }
        result = await browsing_module.get_viewport("ctx-1")
        assert isinstance(result, Viewport)
        assert result.width == 1920
        assert result.height == 1080
        assert result.device_pixel_ratio == 2.0
        mock_connection.send_command.assert_called_once_with(
            "browsingContext.getViewport", {"context": "ctx-1"}
        )


class TestWebExtensionInstall:
    async def test_install(
        self,
        web_extension_module: WebExtensionModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"extension": "ext-123"}
        result = await web_extension_module.install("/path/to/ext.zip")
        mock_connection.send_command.assert_called_once_with(
            "webExtension.install", {"archivePath": "/path/to/ext.zip"}
        )
        assert result.extension == "ext-123"


class TestWebExtensionUninstall:
    async def test_uninstall(
        self,
        web_extension_module: WebExtensionModule,
        mock_connection: MockConn,
    ) -> None:
        await web_extension_module.uninstall("ext-123")
        mock_connection.send_command.assert_called_once_with(
            "webExtension.uninstall", {"extension": "ext-123"}
        )


class TestSessionSubscribe:
    async def test_subscribe_returns_result(
        self,
        mock_connection: MockConn,
    ) -> None:
        from bidiwave.modules.session import SessionModule
        mock_connection.send_command.return_value = {"subscriptions": []}
        session_module = SessionModule(mock_connection)
        result = await session_module.subscribe(["log.entryAdded"])
        assert result is not None
        assert isinstance(result, dict)

    async def test_subscribe_with_contexts(
        self,
        mock_connection: MockConn,
    ) -> None:
        from bidiwave.modules.session import SessionModule
        mock_connection.send_command.return_value = {}
        session_module = SessionModule(mock_connection)
        await session_module.subscribe(["log.entryAdded"], contexts=["ctx-1"])
        params = mock_connection.send_command.call_args.args[1]
        assert params["contexts"] == ["ctx-1"]
