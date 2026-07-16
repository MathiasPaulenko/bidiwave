"""Unit tests for new event models.

Covers: responseStarted, realmCreated, realmDestroyed, userPromptOpened.
"""

from bidiwave.protocol.events import (
    BrowsingContextUserPromptOpenedEvent,
    InputFileDialogOpenedEvent,
    NetworkResponseStartedEvent,
    ScriptRealmCreatedEvent,
    ScriptRealmDestroyedEvent,
    parse_event,
)


class TestNetworkResponseStartedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com/api",
                "method": "GET",
            },
            "response": {
                "url": "https://example.com/api",
                "status": 200,
                "statusText": "OK",
                "mimeType": "application/json",
            },
        }
        event = parse_event("network.responseStarted", params)
        assert isinstance(event, NetworkResponseStartedEvent)
        assert event.context == "ctx-1"
        assert event.request.url == "https://example.com/api"
        assert event.response.status == 200
        assert event.response.status_text == "OK"
        assert event.redirect_count == 0

    def test_parse_with_redirect(self) -> None:
        params = {
            "request": {
                "request": "req-2",
                "url": "https://old.com",
                "method": "GET",
            },
            "response": {
                "url": "https://new.com",
                "status": 301,
            },
            "redirectCount": 2,
        }
        event = parse_event("network.responseStarted", params)
        assert isinstance(event, NetworkResponseStartedEvent)
        assert event.redirect_count == 2
        assert event.context is None


class TestScriptRealmCreatedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "realm": "realm-1",
            "origin": "https://example.com",
            "type": "window",
            "context": "ctx-1",
        }
        event = parse_event("script.realmCreated", params)
        assert isinstance(event, ScriptRealmCreatedEvent)
        assert event.realm == "realm-1"
        assert event.origin == "https://example.com"
        assert event.type == "window"
        assert event.context == "ctx-1"
        assert event.sandbox is None

    def test_parse_sandbox(self) -> None:
        params = {
            "realm": "realm-2",
            "origin": "https://example.com",
            "type": "window",
            "sandbox": "my-sandbox",
        }
        event = parse_event("script.realmCreated", params)
        assert isinstance(event, ScriptRealmCreatedEvent)
        assert event.type == "window"
        assert event.sandbox == "my-sandbox"
        assert event.context is None


class TestScriptRealmDestroyedEvent:
    def test_parse_basic(self) -> None:
        params = {"realm": "realm-1"}
        event = parse_event("script.realmDestroyed", params)
        assert isinstance(event, ScriptRealmDestroyedEvent)
        assert event.realm == "realm-1"


class TestBrowsingContextUserPromptOpenedEvent:
    def test_parse_alert(self) -> None:
        params = {
            "context": "ctx-1",
            "type": "alert",
            "message": "Hello!",
        }
        event = parse_event("browsingContext.userPromptOpened", params)
        assert isinstance(event, BrowsingContextUserPromptOpenedEvent)
        assert event.context == "ctx-1"
        assert event.type == "alert"
        assert event.message == "Hello!"
        assert event.default_value == ""

    def test_parse_prompt(self) -> None:
        params = {
            "context": "ctx-1",
            "type": "prompt",
            "message": "Enter your name:",
            "defaultValue": "John",
        }
        event = parse_event("browsingContext.userPromptOpened", params)
        assert isinstance(event, BrowsingContextUserPromptOpenedEvent)
        assert event.type == "prompt"
        assert event.default_value == "John"

    def test_parse_confirm(self) -> None:
        params = {
            "context": "ctx-2",
            "type": "confirm",
            "message": "Are you sure?",
        }
        event = parse_event("browsingContext.userPromptOpened", params)
        assert isinstance(event, BrowsingContextUserPromptOpenedEvent)
        assert event.type == "confirm"


class TestInputFileDialogOpenedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "element": {"sharedId": "elem-1"},
            "multiple": False,
        }
        event = parse_event("input.fileDialogOpened", params)
        assert isinstance(event, InputFileDialogOpenedEvent)
        assert event.context == "ctx-1"
        assert event.element == {"sharedId": "elem-1"}
        assert event.multiple is False

    def test_parse_multiple(self) -> None:
        params = {
            "context": "ctx-2",
            "multiple": True,
        }
        event = parse_event("input.fileDialogOpened", params)
        assert isinstance(event, InputFileDialogOpenedEvent)
        assert event.context == "ctx-2"
        assert event.multiple is True
        assert event.element is None
