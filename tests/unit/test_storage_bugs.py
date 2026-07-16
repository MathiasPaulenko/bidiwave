"""Regression tests for storage module bug fixes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.results import Cookie

MockConn = MagicMock


@pytest.fixture
def mock_connection() -> MockConn:
    conn = MagicMock()
    conn.send_command = AsyncMock()
    return conn


@pytest.fixture
def storage_module(mock_connection: MockConn) -> StorageModule:
    return StorageModule(mock_connection)


class TestCookieValueBytesValue:
    """Bug 27: Cookie.value accepts BytesValue {type: 'base64', value: '...'} per spec."""

    def test_cookie_accepts_string_value(self) -> None:
        cookie = Cookie(name="foo", value="bar")
        assert cookie.value == "bar"

    def test_cookie_accepts_bytes_value_dict(self) -> None:
        cookie = Cookie.model_validate({
            "name": "foo",
            "value": {"type": "base64", "value": "YmFy"},
        })
        assert cookie.value == "YmFy"

    def test_cookie_serializes_bytes_value(self) -> None:
        cookie = Cookie.model_validate({
            "name": "foo",
            "value": {"type": "base64", "value": "YmFy"},
        })
        dumped = cookie.model_dump(by_alias=True, exclude_none=True)
        assert dumped["value"] == "YmFy"


class TestCookieSameSiteEnum:
    """Bug 28: Cookie.same_site should accept case-insensitive 'strict', 'lax', 'none' per spec."""

    def test_same_site_lower_strict(self) -> None:
        cookie = Cookie.model_validate({"name": "foo", "value": "bar", "sameSite": "strict"})
        assert cookie.same_site == "strict"

    def test_same_site_lower_lax(self) -> None:
        cookie = Cookie.model_validate({"name": "foo", "value": "bar", "sameSite": "lax"})
        assert cookie.same_site == "lax"

    def test_same_site_lower_none(self) -> None:
        cookie = Cookie.model_validate({"name": "foo", "value": "bar", "sameSite": "none"})
        assert cookie.same_site == "none"

    def test_same_site_upper_strict_normalized(self) -> None:
        cookie = Cookie.model_validate({"name": "foo", "value": "bar", "sameSite": "Strict"})
        assert cookie.same_site == "strict"

    def test_same_site_upper_lax_normalized(self) -> None:
        cookie = Cookie.model_validate({"name": "foo", "value": "bar", "sameSite": "Lax"})
        assert cookie.same_site == "lax"


class TestGetCookiesFilter:
    """Bug 29: get_cookies should accept filter parameter per spec."""

    async def test_get_cookies_with_filter(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cookies": []}
        await storage_module.get_cookies("ctx-1", filter={"name": "session"})
        params = mock_connection.send_command.call_args.args[1]
        assert "filter" in params
        assert params["filter"]["name"] == "session"

    async def test_get_cookies_without_filter_omits_field(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        mock_connection.send_command.return_value = {"cookies": []}
        await storage_module.get_cookies("ctx-1")
        params = mock_connection.send_command.call_args.args[1]
        assert "filter" not in params


class TestDeleteCookieUsesDeleteCookies:
    """Bug 30: delete_cookie should use storage.deleteCookies with name filter, not non-existent storage.deleteCookie."""  # noqa: E501

    async def test_delete_cookie_uses_delete_cookies_command(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        await storage_module.delete_cookie("ctx-1", "session")
        command = mock_connection.send_command.call_args.args[0]
        assert command == "storage.deleteCookies"
        params = mock_connection.send_command.call_args.args[1]
        assert params["name"] == "session"
        assert params["context"] == "ctx-1"


class TestSetCookieDomainValidation:
    """Bug 31: set_cookie should warn/validate when domain is missing for cross-context cookies."""

    async def test_set_cookie_without_domain_still_works(
        self,
        storage_module: StorageModule,
        mock_connection: MockConn,
    ) -> None:
        cookie = Cookie(name="foo", value="bar")
        await storage_module.set_cookie("ctx-1", cookie)
        params = mock_connection.send_command.call_args.args[1]
        assert params["cookie"]["name"] == "foo"
