"""Unit tests for authRequired, fragmentNavigated, load, and navigation event models."""

from bidiwave.protocol.events import (
    BrowsingContextDownloadEndEvent,
    BrowsingContextDownloadWillBeginEvent,
    BrowsingContextFragmentNavigatedEvent,
    BrowsingContextLoadEvent,
    BrowsingContextNavigationAbortedEvent,
    BrowsingContextNavigationCommittedEvent,
    BrowsingContextNavigationFailedEvent,
    BrowsingContextUserPromptClosedEvent,
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


class TestBrowsingContextNavigationAbortedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "navigation": "nav-1",
            "url": "https://example.com",
        }
        event = parse_event("browsingContext.navigationAborted", params)
        assert isinstance(event, BrowsingContextNavigationAbortedEvent)
        assert event.context == "ctx-1"
        assert event.navigation == "nav-1"
        assert event.url == "https://example.com"

    def test_extra_fields_allowed(self) -> None:
        params = {
            "context": "ctx-1",
            "navigation": "nav-2",
            "url": "https://aborted.com",
            "extraField": "value",
        }
        event = parse_event("browsingContext.navigationAborted", params)
        assert isinstance(event, BrowsingContextNavigationAbortedEvent)
        assert event.context == "ctx-1"


class TestBrowsingContextNavigationCommittedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "navigation": "nav-1",
            "url": "https://example.com",
        }
        event = parse_event("browsingContext.navigationCommitted", params)
        assert isinstance(event, BrowsingContextNavigationCommittedEvent)
        assert event.context == "ctx-1"
        assert event.navigation == "nav-1"
        assert event.url == "https://example.com"

    def test_extra_fields_allowed(self) -> None:
        params = {
            "context": "ctx-2",
            "navigation": "nav-3",
            "url": "https://committed.com",
            "extraField": 42,
        }
        event = parse_event("browsingContext.navigationCommitted", params)
        assert isinstance(event, BrowsingContextNavigationCommittedEvent)
        assert event.navigation == "nav-3"


class TestBrowsingContextNavigationFailedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "navigation": "nav-1",
            "url": "https://failed.example.com",
        }
        event = parse_event("browsingContext.navigationFailed", params)
        assert isinstance(event, BrowsingContextNavigationFailedEvent)
        assert event.context == "ctx-1"
        assert event.navigation == "nav-1"
        assert event.url == "https://failed.example.com"

    def test_extra_fields_allowed(self) -> None:
        params = {
            "context": "ctx-3",
            "navigation": "nav-4",
            "url": "https://error.com",
            "errorCode": "networkError",
        }
        event = parse_event("browsingContext.navigationFailed", params)
        assert isinstance(event, BrowsingContextNavigationFailedEvent)
        assert event.context == "ctx-3"


class TestBrowsingContextUserPromptClosedEvent:
    def test_parse_accepted(self) -> None:
        params = {"context": "ctx-1", "accepted": True}
        event = parse_event("browsingContext.userPromptClosed", params)
        assert isinstance(event, BrowsingContextUserPromptClosedEvent)
        assert event.context == "ctx-1"
        assert event.accepted is True
        assert event.user_text is None

    def test_parse_dismissed_with_user_text(self) -> None:
        params = {"context": "ctx-2", "accepted": False, "userText": "hello"}
        event = parse_event("browsingContext.userPromptClosed", params)
        assert isinstance(event, BrowsingContextUserPromptClosedEvent)
        assert event.accepted is False
        assert event.user_text == "hello"

    def test_extra_fields_allowed(self) -> None:
        params = {"context": "ctx-3", "accepted": True, "extraField": 42}
        event = parse_event("browsingContext.userPromptClosed", params)
        assert isinstance(event, BrowsingContextUserPromptClosedEvent)
        assert event.context == "ctx-3"


class TestBrowsingContextDownloadWillBeginEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com/file.zip",
            "suggestedFilename": "file.zip",
        }
        event = parse_event("browsingContext.downloadWillBegin", params)
        assert isinstance(event, BrowsingContextDownloadWillBeginEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com/file.zip"
        assert event.suggested_filename == "file.zip"
        assert event.navigation is None
        assert event.user_context is None

    def test_parse_with_navigation_and_user_context(self) -> None:
        params = {
            "context": "ctx-2",
            "navigation": "nav-1",
            "url": "https://example.com/doc.pdf",
            "userContext": "my-context",
        }
        event = parse_event("browsingContext.downloadWillBegin", params)
        assert isinstance(event, BrowsingContextDownloadWillBeginEvent)
        assert event.navigation == "nav-1"
        assert event.user_context == "my-context"


class TestBrowsingContextDownloadEndEvent:
    def test_parse_completed(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com/file.zip",
            "status": "completed",
            "item": "download-1",
        }
        event = parse_event("browsingContext.downloadEnd", params)
        assert isinstance(event, BrowsingContextDownloadEndEvent)
        assert event.context == "ctx-1"
        assert event.status == "completed"
        assert event.item == "download-1"
        assert event.cancel_reason is None

    def test_parse_canceled(self) -> None:
        params = {
            "context": "ctx-2",
            "url": "https://example.com/file.zip",
            "status": "canceled",
            "cancelReason": "userCanceled",
        }
        event = parse_event("browsingContext.downloadEnd", params)
        assert isinstance(event, BrowsingContextDownloadEndEvent)
        assert event.status == "canceled"
        assert event.cancel_reason == "userCanceled"

    def test_parse_with_user_context(self) -> None:
        params = {
            "context": "ctx-3",
            "url": "https://example.com/file.zip",
            "userContext": "profile-1",
        }
        event = parse_event("browsingContext.downloadEnd", params)
        assert isinstance(event, BrowsingContextDownloadEndEvent)
        assert event.user_context == "profile-1"
