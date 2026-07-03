"""Unit tests for domContentLoaded and samplingStateChanged event models."""

from bidiwave.protocol.events import (
    BrowsingContextDOMContentLoadedEvent,
    NetworkSamplingStateChangedEvent,
    parse_event,
)


class TestBrowsingContextDOMContentLoadedEvent:
    def test_parse_basic(self) -> None:
        params = {
            "context": "ctx-1",
            "url": "https://example.com",
        }
        event = parse_event("browsingContext.domContentLoaded", params)
        assert isinstance(event, BrowsingContextDOMContentLoadedEvent)
        assert event.context == "ctx-1"
        assert event.url == "https://example.com"


class TestNetworkSamplingStateChangedEvent:
    def test_parse_all(self) -> None:
        params = {
            "context": "ctx-1",
            "sampling": "all",
        }
        event = parse_event("network.samplingStateChanged", params)
        assert isinstance(event, NetworkSamplingStateChangedEvent)
        assert event.context == "ctx-1"
        assert event.sampling == "all"

    def test_parse_none(self) -> None:
        params = {
            "sampling": "none",
        }
        event = parse_event("network.samplingStateChanged", params)
        assert isinstance(event, NetworkSamplingStateChangedEvent)
        assert event.sampling == "none"
        assert event.context is None
