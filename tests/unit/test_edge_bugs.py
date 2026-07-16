"""Regression tests for edge-case bugs found in deep re-analysis."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from bidiwave.protocol.events import (
    BrowsingContextNavigationCompletedEvent,
    BrowsingContextNavigationStartedEvent,
    BrowsingContextUserPromptOpenedEvent,
    ScriptRealmCreatedEvent,
)
from bidiwave.protocol.remote_value import NumberValue, RemoteValue, StringValue


class TestUserPromptOpenedTypeLiteral:
    """Bug 48/41: type should be Literal["alert","confirm","prompt","beforeunload"] per spec."""

    def test_type_alert(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "type": "alert", "message": "hello",
        })
        assert event.type == "alert"

    def test_type_confirm(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "type": "confirm",
        })
        assert event.type == "confirm"

    def test_type_prompt(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "type": "prompt",
        })
        assert event.type == "prompt"

    def test_type_beforeunload(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "type": "beforeunload",
        })
        assert event.type == "beforeunload"

    def test_type_invalid_rejected(self) -> None:
        with pytest.raises(ValidationError):
            BrowsingContextUserPromptOpenedEvent.model_validate({
                "context": "ctx-1", "type": "dialog",
            })


class TestUserPromptOpenedHandlerLiteral:
    """Bug 48: handler should be Literal["accept","dismiss","default"]|None per spec."""

    def test_handler_accept(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "handler": "accept",
        })
        assert event.handler == "accept"

    def test_handler_dismiss(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "handler": "dismiss",
        })
        assert event.handler == "dismiss"

    def test_handler_default(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1", "handler": "default",
        })
        assert event.handler == "default"

    def test_handler_none(self) -> None:
        event = BrowsingContextUserPromptOpenedEvent.model_validate({
            "context": "ctx-1",
        })
        assert event.handler is None

    def test_handler_invalid_rejected(self) -> None:
        with pytest.raises(ValidationError):
            BrowsingContextUserPromptOpenedEvent.model_validate({
                "context": "ctx-1", "handler": "maybe",
            })


class TestNavigationCompletedCanceledField:
    """Bug 42: navigationCompleted should have canceled field per spec."""

    def test_canceled_true(self) -> None:
        event = BrowsingContextNavigationCompletedEvent.model_validate({
            "context": "ctx-1", "url": "https://example.com", "canceled": True,
        })
        assert event.canceled is True

    def test_canceled_default_false(self) -> None:
        event = BrowsingContextNavigationCompletedEvent.model_validate({
            "context": "ctx-1", "url": "https://example.com",
        })
        assert event.canceled is False


class TestNavigationStartedCanceledField:
    """Bug 44: navigationStarted should have canceled field per spec."""

    def test_canceled_true(self) -> None:
        event = BrowsingContextNavigationStartedEvent.model_validate({
            "context": "ctx-1", "url": "https://example.com", "canceled": True,
        })
        assert event.canceled is True

    def test_canceled_default_false(self) -> None:
        event = BrowsingContextNavigationStartedEvent.model_validate({
            "context": "ctx-1", "url": "https://example.com",
        })
        assert event.canceled is False


class TestScriptRealmCreatedTypeLiteral:
    """Bug 43: ScriptRealmCreatedEvent.type should be Literal per spec."""

    def test_type_window(self) -> None:
        event = ScriptRealmCreatedEvent.model_validate({
            "realm": "r1", "origin": "https://example.com", "type": "window",
        })
        assert event.type == "window"

    def test_type_dedicated_worker(self) -> None:
        event = ScriptRealmCreatedEvent.model_validate({
            "realm": "r2", "origin": "", "type": "dedicated-worker",
        })
        assert event.type == "dedicated-worker"

    def test_type_service_worker(self) -> None:
        event = ScriptRealmCreatedEvent.model_validate({
            "realm": "r3", "origin": "", "type": "service-worker",
        })
        assert event.type == "service-worker"

    def test_type_invalid_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ScriptRealmCreatedEvent.model_validate({
                "realm": "r4", "origin": "", "type": "invalid-realm",
            })


class TestRemoteValueDateType:
    """Bug 45: RemoteValue.parse should handle 'date' type per spec."""

    def test_date_value_parsed(self) -> None:
        rv = RemoteValue.parse({
            "type": "success",
            "result": {"type": "date", "value": "2024-01-01T00:00:00Z"},
        })
        assert rv.type == "date"


class TestRemoteValueRegexpType:
    """Bug 46: RemoteValue.parse should handle 'regexp' type per spec."""

    def test_regexp_value_parsed(self) -> None:
        rv = RemoteValue.parse({
            "type": "success",
            "result": {"type": "regexp", "value": {"pattern": "abc", "flags": "i"}},
        })
        assert rv.type == "regexp"


class TestRemoteValueMapType:
    """Bug 47: RemoteValue.parse should handle 'map' type per spec."""

    def test_map_value_parsed(self) -> None:
        rv = RemoteValue.parse({
            "type": "success",
            "result": {"type": "map", "value": []},
        })
        assert rv.type == "map"


class TestRemoteValueSetType:
    """Bug 47: RemoteValue.parse should handle 'set' type per spec."""

    def test_set_value_parsed(self) -> None:
        rv = RemoteValue.parse({
            "type": "success",
            "result": {"type": "set", "value": []},
        })
        assert rv.type == "set"


class TestCookieValueBytesValue:
    """Bug 51: set_cookie must send value as BytesValue dict per W3C spec."""

    def test_cookie_value_serialized_as_bytes_value(self) -> None:
        from unittest.mock import AsyncMock, MagicMock
        from bidiwave.modules.storage import StorageModule
        from bidiwave.protocol.results import Cookie

        conn = MagicMock()
        conn.send_command = AsyncMock()
        mod = StorageModule(conn)
        cookie = Cookie(name="test", value="abc", domain="example.com")
        import asyncio
        asyncio.run(mod.set_cookie("ctx-1", cookie))
        params = conn.send_command.call_args.args[1]
        assert params["cookie"]["value"] == {"type": "string", "value": "abc"}


class TestLogLevelWarnNormalization:
    """Bug 52: Edge sends 'warn' but W3C spec uses 'warning' — normalize."""

    def test_warn_normalized_to_warning(self) -> None:
        from bidiwave.protocol.events import LogEntryAddedEvent
        event = LogEntryAddedEvent.model_validate({
            "level": "warn",
            "text": "test",
            "timestamp": 123,
            "source": {},
        })
        assert event.level == "warning"


class TestObjectValueListOfPairs:
    """Bug 53: ObjectValue.value receives list-of-pairs from browser, not dict."""

    def test_object_value_list_of_pairs_converted(self) -> None:
        rv = RemoteValue.parse({
            "type": "object",
            "value": [
                ["name", {"type": "string", "value": "test"}],
                ["age", {"type": "number", "value": 42}],
            ],
        })
        assert rv.type == "object"
        assert isinstance(rv.value["name"], StringValue)
        assert rv.value["name"].value == "test"
        assert isinstance(rv.value["age"], NumberValue)
        assert rv.value["age"].value == 42

    def test_object_value_dict_passes_through(self) -> None:
        rv = RemoteValue.parse({
            "type": "object",
            "value": {"name": "test"},
        })
        assert rv.value == {"name": "test"}

    def test_object_value_none_passes_through(self) -> None:
        rv = RemoteValue.parse({
            "type": "object",
        })
        assert rv.value is None


class TestNavigationStartedEventAlias:
    """BrowsingContextNavigatedEvent should be a backward-compatible alias."""

    def test_alias_is_same_class(self) -> None:
        from bidiwave.protocol.events import (
            BrowsingContextNavigatedEvent,
            BrowsingContextNavigationStartedEvent,
        )
        assert BrowsingContextNavigatedEvent is BrowsingContextNavigationStartedEvent


class TestGetTreeResultTyped:
    """get_tree should return typed GetTreeResult with nested children."""

    def test_empty_tree(self) -> None:
        from bidiwave.protocol.results import GetTreeResult
        result = GetTreeResult.model_validate({"contexts": []})
        assert result.contexts == []

    def test_tree_with_nested_children(self) -> None:
        from bidiwave.protocol.results import GetTreeResult
        result = GetTreeResult.model_validate({
            "contexts": [
                {
                    "context": "parent",
                    "url": "https://parent.com",
                    "children": [
                        {"context": "child1", "url": "https://child1.com"},
                        {"context": "child2", "url": "https://child2.com"},
                    ],
                },
            ],
        })
        assert len(result.contexts) == 1
        parent = result.contexts[0]
        assert parent.context == "parent"
        assert parent.url == "https://parent.com"
        assert parent.children is not None
        assert len(parent.children) == 2
        assert parent.children[0].context == "child1"
        assert parent.children[1].context == "child2"

    def test_tree_children_none_from_browser(self) -> None:
        from bidiwave.protocol.results import GetTreeResult
        result = GetTreeResult.model_validate({
            "contexts": [
                {"context": "leaf", "url": "https://leaf.com", "children": None},
            ],
        })
        assert result.contexts[0].children is None

    def test_tree_with_user_context(self) -> None:
        from bidiwave.protocol.results import GetTreeResult
        result = GetTreeResult.model_validate({
            "contexts": [
                {"context": "ctx-1", "url": "https://example.com", "userContext": "uc-1"},
            ],
        })
        assert result.contexts[0].user_context == "uc-1"


class TestBrowsingContextCreatedEventAliases:
    """Bug 54: BrowsingContextCreatedEvent missing aliases for userContext/originalOpener.

    The browser sends camelCase keys (userContext, originalOpener) but the
    model fields were snake_case without aliases, so the values were always
    the defaults instead of the actual browser data.
    """

    def test_user_context_parsed_from_camel_case(self) -> None:
        from bidiwave.protocol.events import BrowsingContextCreatedEvent
        event = BrowsingContextCreatedEvent.model_validate({
            "context": "ctx-1",
            "url": "https://example.com",
            "userContext": "my-context",
        })
        assert event.user_context == "my-context"

    def test_user_context_default(self) -> None:
        from bidiwave.protocol.events import BrowsingContextCreatedEvent
        event = BrowsingContextCreatedEvent.model_validate({
            "context": "ctx-1",
            "url": "https://example.com",
        })
        assert event.user_context == "default"

    def test_original_opener_parsed_from_camel_case(self) -> None:
        from bidiwave.protocol.events import BrowsingContextCreatedEvent
        event = BrowsingContextCreatedEvent.model_validate({
            "context": "ctx-1",
            "url": "https://example.com",
            "originalOpener": "ctx-0",
        })
        assert event.original_opener == "ctx-0"

    def test_original_opener_none(self) -> None:
        from bidiwave.protocol.events import BrowsingContextCreatedEvent
        event = BrowsingContextCreatedEvent.model_validate({
            "context": "ctx-1",
            "url": "https://example.com",
            "originalOpener": None,
        })
        assert event.original_opener is None

    def test_parse_event_context_created_with_user_context(self) -> None:
        from bidiwave.protocol.events import parse_event
        event = parse_event("browsingContext.contextCreated", {
            "context": "ctx-2",
            "url": "https://test.com",
            "userContext": "custom-uc",
            "originalOpener": "ctx-1",
        })
        assert event.user_context == "custom-uc"  # type: ignore[attr-defined]
        assert event.original_opener == "ctx-1"  # type: ignore[attr-defined]


class TestRemoteValueParseDate:
    """Bug 55: RemoteValue.parse should handle 'date' type."""

    def test_parse_date(self) -> None:
        from bidiwave.protocol.remote_value import DateValue
        result = RemoteValue.parse({"type": "date", "value": "2024-01-15T00:00:00.000Z"})
        assert isinstance(result, DateValue)
        assert result.value == "2024-01-15T00:00:00.000Z"

    def test_parse_date_with_handle(self) -> None:
        from bidiwave.protocol.remote_value import DateValue
        result = RemoteValue.parse({"type": "date", "handle": "h1"})
        assert isinstance(result, DateValue)
        assert result.handle == "h1"


class TestRemoteValueParseRegExp:
    """Bug 55: RemoteValue.parse should handle 'regexp' type."""

    def test_parse_regexp(self) -> None:
        from bidiwave.protocol.remote_value import RegExpValue
        result = RemoteValue.parse({"type": "regexp", "value": {"pattern": "abc", "flags": "i"}})
        assert isinstance(result, RegExpValue)
        assert result.value == {"pattern": "abc", "flags": "i"}


class TestRemoteValueParseMap:
    """Bug 55: RemoteValue.parse should handle 'map' type."""

    def test_parse_map(self) -> None:
        from bidiwave.protocol.remote_value import MapValue
        result = RemoteValue.parse({
            "type": "map",
            "value": [["key1", {"type": "string", "value": "val1"}]],
        })
        assert isinstance(result, MapValue)
        assert result.value is not None
        assert len(result.value) == 1

    def test_parse_map_empty(self) -> None:
        from bidiwave.protocol.remote_value import MapValue
        result = RemoteValue.parse({"type": "map", "value": []})
        assert isinstance(result, MapValue)
        assert result.value == []


class TestRemoteValueParseSet:
    """Bug 55: RemoteValue.parse should handle 'set' type."""

    def test_parse_set(self) -> None:
        from bidiwave.protocol.remote_value import SetValue
        result = RemoteValue.parse({
            "type": "set",
            "value": [{"type": "number", "value": 1}, {"type": "number", "value": 2}],
        })
        assert isinstance(result, SetValue)
        assert result.value is not None
        assert len(result.value) == 2

    def test_parse_set_empty(self) -> None:
        from bidiwave.protocol.remote_value import SetValue
        result = RemoteValue.parse({"type": "set", "value": []})
        assert isinstance(result, SetValue)
        assert result.value == []
