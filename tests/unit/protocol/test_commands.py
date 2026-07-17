"""Tests unitarios para protocol/commands.py."""

import json

from bidiwave.protocol.commands import Command, EvaluateParams, NavigateParams, NewSessionParams


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
        cmd = Command(id=42, method="browsing.navigate", params={"context": "abc"})
        json_str = cmd.model_dump_json()
        restored = Command.model_validate_json(json_str)
        assert restored.id == 42
        assert restored.method == "browsing.navigate"
        assert restored.params == {"context": "abc"}


class TestNewSessionParams:
    def test_default_capabilities(self) -> None:
        params = NewSessionParams()
        assert params.capabilities == {}

    def test_with_capabilities(self) -> None:
        params = NewSessionParams(capabilities={"webSocketUrl": True})
        assert params.capabilities == {"webSocketUrl": True}


class TestNavigateParams:
    def test_defaults(self) -> None:
        params = NavigateParams(context="ctx1", url="https://example.com")
        assert params.wait == "complete"

    def test_custom_wait(self) -> None:
        params = NavigateParams(context="ctx1", url="https://example.com", wait="none")
        assert params.wait == "none"

    def test_extra_allowed(self) -> None:
        params = NavigateParams(context="ctx1", url="https://example.com", extra="foo")
        assert params.model_dump()["extra"] == "foo"


class TestEvaluateParams:
    def test_defaults(self) -> None:
        params = EvaluateParams(expression="1+1", target={"context": "ctx1"})
        assert params.await_promise is False

    def test_with_await_promise(self) -> None:
        params = EvaluateParams(
            expression="Promise.resolve(1)", target={"context": "ctx1"}, await_promise=True
        )
        assert params.await_promise is True

    def test_serialization_round_trip(self) -> None:
        params = EvaluateParams(expression="document.title", target={"context": "ctx1"})
        data = json.loads(params.model_dump_json())
        assert data["expression"] == "document.title"
        assert data["target"] == {"context": "ctx1"}
        assert data["await_promise"] is False

    def test_serialization_options_and_user_activation(self) -> None:
        params = EvaluateParams(
            expression="1+1",
            target={"context": "ctx1"},
            serialization_options={"maxDomDepth": 1},
            user_activation=True,
        )
        data = params.model_dump(by_alias=True)
        assert data["serializationOptions"] == {"maxDomDepth": 1}
        assert data["userActivation"] is True
