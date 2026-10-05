"""Tests unitarios para protocol/commands.py."""


from bidiwave.protocol.commands import Command, NewSessionParams, ViewportSize


class TestCommand:
    def test_basic_serialization(self) -> None:
        cmd = Command(id=1, method="session.new", params={"foo": "bar"})
        data = cmd.model_dump()
        assert data["id"] == 1
        assert data["method"] == "session.new"
        assert data["params"] == {"foo": "bar"}

    def test_default_params(self) -> None:
        cmd = Command(id=1, method="session.status")
        assert cmd.params == {}

    def test_extra_fields_allowed(self) -> None:
        cmd = Command(id=1, method="test", params={}, extra_field="value")
        assert cmd.model_dump()["extra_field"] == "value"

    def test_round_trip(self) -> None:
        cmd = Command(id=42, method="browsingContext.navigate", params={"context": "abc"})
        json_str = cmd.model_dump_json()
        restored = Command.model_validate_json(json_str)
        assert restored.id == 42
        assert restored.method == "browsingContext.navigate"
        assert restored.params == {"context": "abc"}


class TestNewSessionParams:
    def test_default_capabilities(self) -> None:
        params = NewSessionParams()
        assert params.capabilities == {}

    def test_with_capabilities(self) -> None:
        params = NewSessionParams(capabilities={"webSocketUrl": True})
        assert params.capabilities == {"webSocketUrl": True}


class TestViewportSize:
    def test_fields(self) -> None:
        size = ViewportSize(width=800, height=600)
        assert size.model_dump() == {"width": 800, "height": 600}
