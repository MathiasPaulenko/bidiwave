"""Unit tests for authRequired, fragmentNavigated, and load event models."""

from bidiwave.protocol.events import (
    BrowsingContextFragmentNavigatedEvent,
    BrowsingContextLoadEvent,
    NetworkAuthRequiredEvent,
    parse_event,
)


class TestNetworkAuthRequiredEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "request": {
                "request": "req-1",
                "url": "https://example.com/protected",
                "method": "GET",
            },
        }
        event = parse_event("network.authRequired", params)
        assert isinstance(event, NetworkAuthRequiredEvent)
        assert event.context == "ctx-1"
        assert event.request.url == "https://example.com/protected"
        assert event.request.method == "GET"
        assert event.redirect_count == 0

    def test_parse_no_context(self) -> None:
        params = {
            "request": {
                "request": "req-2",
                "url": "https://secure.com/api",
                "method": "POST",
            },
            "redirectCount": 1,
        }
        event = parse_event("network.authRequired", params)
        assert isinstance(event, NetworkAuthRequiredEvent)
        assert event.context is None
        assert event.redirect_count == 1


class TestBrowsingContextFragmentNavigatedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com/page#section",
            "navigation": "nav-1",
        }
        event = parse_event("browsingContext.fragmentNavigated", params)
        assert isinstance(event, BrowsingContextFragmentNavigatedEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com/page#section"
        assert event.navigation == "nav-1"

    def test_parse_no_navigation(self) -> None:
        params = {
            "context": "ctx-2",
            "url": "https://example.com/page#top",
        }
        event = parse_event("browsingContext.fragmentNavigated", params)
        assert isinstance(event, BrowsingContextFragmentNavigatedEvent)
        assert event.navigation is None


class TestBrowsingContextLoadEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com",
        }
        event = parse_event("browsingContext.load", params)
        assert isinstance(event, BrowsingContextLoadEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com"
