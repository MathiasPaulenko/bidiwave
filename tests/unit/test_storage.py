"""Unit tests for StorageModule."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.results import Cookie, GetCookiesResult

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def storage_module(mock_connection: MockConn) -> StorageModule:
    return StorageModule(mock_connection)


class TestGetCookies:
    async def test_get_cookies_basic(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "cookies": [
                {"name": "session", "value": "abc123"},
                {"name": "token", "value": "xyz789"},
            ]
        }
        result = await storage_module.get_cookies("ctx-1")
        assert len(result) == 2
        assert isinstance(result[0], Cookie)
        assert result[0].name == "session"
        assert result[0].value == "abc123"
        assert result[1].name == "token"
        mock_connection.send_command.assert_called_once_with(
            "storage.getCookies", {"context": "ctx-1"}
        )

    async def test_get_cookies_empty(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cookies": []}
        result = await storage_module.get_cookies("ctx-1")
        assert result == []

    async def test_get_cookies_with_browsing_context(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = MagicMock()
        ctx.id = "ctx-abc"
        mock_connection.send_command.return_value = {"cookies": []}
        await storage_module.get_cookies(ctx)
        mock_connection.send_command.assert_called_once_with(
            "storage.getCookies", {"context": "ctx-abc"}
        )

    async def test_get_cookies_full_cookie(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {
            "cookies": [
                {
                    "name": "session",
                    "value": "abc123",
                    "domain": "example.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Strict",
                    "expiry": 1735689600,
                }
            ]
        }
        result = await storage_module.get_cookies("ctx-1")
        assert len(result) == 1
        cookie = result[0]
        assert cookie.domain == "example.com"
        assert cookie.http_only is True
        assert cookie.secure is True
        assert cookie.same_site == "strict"
        assert cookie.expires == 1735689600


class TestSetCookie:
    async def test_set_cookie_basic(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        cookie = Cookie(name="session", value="abc123", domain="example.com")
        await storage_module.set_cookie("ctx-1", cookie)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[0] == "storage.setCookie"
        params = call_args.args[1]
        assert params["context"] == "ctx-1"
        assert params["cookie"]["name"] == "session"
        assert params["cookie"]["value"] == {"type": "string", "value": "abc123"}
        assert params["cookie"]["domain"] == "example.com"

    async def test_set_cookie_with_browsing_context(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = MagicMock()
        ctx.id = "ctx-xyz"
        cookie = Cookie(name="token", value="xyz789")
        await storage_module.set_cookie(ctx, cookie)
        call_args = mock_connection.send_command.call_args
        assert call_args.args[1]["context"] == "ctx-xyz"

    async def test_set_cookie_excludes_none_fields(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        cookie = Cookie(name="foo", value="bar")
        await storage_module.set_cookie("ctx-1", cookie)
        params = mock_connection.send_command.call_args.args[1]
        assert "domain" not in params["cookie"]
        assert "expiry" not in params["cookie"]
        assert "sameSite" not in params["cookie"]

    async def test_set_cookie_with_all_fields(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        cookie = Cookie(
            name="session",
            value="abc123",
            domain="example.com",
            path="/app",
            http_only=True,
            secure=True,
            same_site="Lax",
            expires=1735689600,
        )
        await storage_module.set_cookie("ctx-1", cookie)
        params = mock_connection.send_command.call_args.args[1]["cookie"]
        assert params["httpOnly"] is True
        assert params["secure"] is True
        assert params["sameSite"] == "lax"
        assert params["path"] == "/app"
        # Per spec the wire field is "expiry", not "expires"
        assert params["expiry"] == 1735689600
        assert "expires" not in params


class TestDeleteCookies:
    async def test_delete_all_cookies(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies("ctx-1")
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies", {"context": "ctx-1"}
        )

    async def test_delete_cookie_by_name(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies("ctx-1", name="session")
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies",
            {"context": "ctx-1", "name": "session"},
        )

    async def test_delete_cookie_by_domain(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies("ctx-1", domain="example.com")
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies",
            {"context": "ctx-1", "domain": "example.com"},
        )

    async def test_delete_cookie_by_path(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies("ctx-1", path="/app")
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies",
            {"context": "ctx-1", "path": "/app"},
        )

    async def test_delete_cookie_all_filters(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies(
            "ctx-1", name="session", domain="example.com", path="/"
        )
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies",
            {
                "context": "ctx-1",
                "name": "session",
                "domain": "example.com",
                "path": "/",
            },
        )

    async def test_delete_cookies_with_browsing_context(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        ctx = MagicMock()
        ctx.id = "ctx-del"
        await storage_module.delete_cookies(ctx)
        mock_connection.send_command.assert_called_once_with(
            "storage.deleteCookies", {"context": "ctx-del"}
        )


class TestCookieModel:
    def test_cookie_defaults(self) -> None:
        cookie = Cookie(name="foo", value="bar")
        assert cookie.path == "/"
        assert cookie.http_only is False
        assert cookie.secure is False
        assert cookie.domain is None
        assert cookie.same_site is None

    def test_cookie_camel_case_aliases(self) -> None:
        cookie = Cookie.model_validate(
            {
                "name": "test",
                "value": "val",
                "httpOnly": True,
                "sameSite": "Strict",
            }
        )
        assert cookie.http_only is True
        assert cookie.same_site == "strict"

    def test_cookie_serializes_with_aliases(self) -> None:
        cookie = Cookie(
            name="test",
            value="val",
            http_only=True,
            same_site="Lax",
        )
        dumped = cookie.model_dump(by_alias=True, exclude_none=True)
        assert dumped["httpOnly"] is True
        assert dumped["sameSite"] == "lax"


class TestGetCookiesResult:
    def test_empty_result(self) -> None:
        result = GetCookiesResult.model_validate({"cookies": []})
        assert result.cookies == []

    def test_with_cookies(self) -> None:
        result = GetCookiesResult.model_validate(
            {
                "cookies": [
                    {"name": "a", "value": "1"},
                    {"name": "b", "value": "2"},
                ]
            }
        )
        assert len(result.cookies) == 2
        assert result.cookies[0].name == "a"
        assert result.cookies[1].name == "b"


class TestPartitionKey:
    async def test_get_cookies_with_partition_key(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cookies": []}
        await storage_module.get_cookies(
            "ctx-1", partition_key={"userContext": "uc-1"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["partitionKey"] == {"userContext": "uc-1"}

    async def test_set_cookie_with_partition_key(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        cookie = Cookie(name="test", value="abc", domain="example.com")
        await storage_module.set_cookie(
            "ctx-1", cookie, partition_key={"sourceOrigin": "https://example.com"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["partitionKey"] == {"sourceOrigin": "https://example.com"}

    async def test_delete_cookies_with_partition_key(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookies(
            "ctx-1", partition_key={"userContext": "uc-1"}
        )
        params = mock_connection.send_command.call_args.args[1]
        assert params["partitionKey"] == {"userContext": "uc-1"}

    async def test_get_cookies_without_partition_key_omitted(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cookies": []}
        await storage_module.get_cookies("ctx-1")
        params = mock_connection.send_command.call_args.args[1]
        assert "partitionKey" not in params
