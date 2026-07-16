"""Unit tests for network event models and parse_event."""

from bidiwave.protocol.events import (
    NetworkBeforeRequestSentEvent,
    NetworkFetchErrorEvent,
    NetworkResponseCompletedEvent,
    parse_event,
)


class TestNetworkBeforeRequestSentEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com/api",
                "method": "GET",
                "headers": [],
                "cookies": [],
            },
        }
        event = parse_event("network.beforeRequestSent", params)
        assert isinstance(event, NetworkBeforeRequestSentEvent)
        assert event.context == "ctx-1"
        assert event.request.url == "https://example.com/api"
        assert event.request.method == "GET"
        assert event.is_blocked is False
        assert event.intercepts == []

    def test_parse_blocked(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-2",
                "url": "https://blocked.com",
                "method": "POST",
            },
            "isBlocked": True,
            "intercepts": ["intercept-1"],
        }
        event = parse_event("network.beforeRequestSent", params)
        assert isinstance(event, NetworkBeforeRequestSentEvent)
        assert event.is_blocked is True
        assert event.intercepts == ["intercept-1"]


class TestNetworkResponseCompletedEvent:
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
        event = parse_event("network.responseCompleted", params)
        assert isinstance(event, NetworkResponseCompletedEvent)
        assert event.response.status == 200
        assert event.response.status_text == "OK"
        assert event.response.mime_type == "application/json"

    def test_parse_with_redirect(self) -> None:
        params = {
            "context": "ctx-1",
            "redirectCount": 2,
            "request": {
                "request": "req-3",
                "url": "https://final.com",
                "method": "GET",
            },
            "response": {
                "url": "https://final.com",
                "status": 301,
            },
        }
        event = parse_event("network.responseCompleted", params)
        assert isinstance(event, NetworkResponseCompletedEvent)
        assert event.redirect_count == 2
        assert event.response.status == 301


class TestNetworkFetchErrorEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://failed.com",
                "method": "GET",
            },
            "errorText": "net::ERR_CONNECTION_REFUSED",
        }
        event = parse_event("network.fetchError", params)
        assert isinstance(event, NetworkFetchErrorEvent)
        assert event.error_text == "net::ERR_CONNECTION_REFUSED"
        assert event.request.url == "https://failed.com"

    def test_parse_no_context(self) -> None:
        params = {
            "request": {
                "request": "req-2",
                "url": "https://no-context.com",
                "method": "GET",
            },
            "errorText": "net::ERR_TIMED_OUT",
        }
        event = parse_event("network.fetchError", params)
        assert isinstance(event, NetworkFetchErrorEvent)
        assert event.context is None


class TestNetworkRequestDataInitiator:
    def test_request_with_initiator(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
                "initiator": {"type": "script", "stackTrace": {"callFrames": []}},
            },
        }
        event = parse_event("network.beforeRequestSent", params)
        assert isinstance(event, NetworkBeforeRequestSentEvent)
        assert event.request.initiator is not None
        assert event.request.initiator["type"] == "script"

    def test_request_without_initiator_defaults_none(self) -> None:
        params = {
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
        }
        event = parse_event("network.beforeRequestSent", params)
        assert isinstance(event, NetworkBeforeRequestSentEvent)
        assert event.request.initiator is None


class TestNetworkResponseDataCacheFields:
    def test_response_from_cache(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
            "response": {
                "url": "https://example.com",
                "status": 200,
                "fromCache": True,
            },
        }
        event = parse_event("network.responseCompleted", params)
        assert isinstance(event, NetworkResponseCompletedEvent)
        assert event.response.from_cache is True

    def test_response_from_service_worker(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
            "response": {
                "url": "https://example.com",
                "status": 200,
                "fromServiceWorker": True,
            },
        }
        event = parse_event("network.responseCompleted", params)
        assert isinstance(event, NetworkResponseCompletedEvent)
        assert event.response.from_service_worker is True

    def test_response_defaults_false(self) -> None:
        params = {
            "request": {
                "request": "req-1",
                "url": "https://example.com",
                "method": "GET",
            },
            "response": {
                "url": "https://example.com",
                "status": 200,
            },
        }
        event = parse_event("network.responseCompleted", params)
        assert isinstance(event, NetworkResponseCompletedEvent)
        assert event.response.from_cache is False
        assert event.response.from_service_worker is False
