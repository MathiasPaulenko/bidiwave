"""Tests unitarios para transport/serializer.py."""

import json

from bidiwave.transport.serializer import deserialize_message, serialize_command


class TestSerializeCommand:
    def test_produces_valid_json(self) -> None:
        result = serialize_command(1, "session.new", {"capabilities": {}})
        data = json.loads(result)
        assert data["id"] == 1
        assert data["method"] == "session.new"
        assert data["params"] == {"capabilities": {}}

    def test_with_empty_params(self) -> None:
        result = serialize_command(5, "session.status", {})
        data = json.loads(result)
        assert data["id"] == 5
        assert data["params"] == {}


class TestDeserializeMessage:
    def test_parses_json(self) -> None:
        raw = '{"type": "success", "id": 1, "result": {"value": 42}}'
        data = deserialize_message(raw)
        assert data["type"] == "success"
        assert data["id"] == 1
        assert data["result"] == {"value": 42}

    def test_round_trip(self) -> None:
        original = serialize_command(10, "browsing.navigate", {"context": "ctx", "url": "https://x"})
        data = deserialize_message(original)
        assert data["id"] == 10
        assert data["method"] == "browsing.navigate"
        assert data["params"]["url"] == "https://x"
