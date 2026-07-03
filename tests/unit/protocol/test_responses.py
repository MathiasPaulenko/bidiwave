"""Tests unitarios para protocol/responses.py."""

import pytest

from bidiwave.protocol.responses import (
    ErrorData,
    ErrorResponse,
    SuccessResponse,
    parse_response,
)


class TestParseResponse:
    def test_success_response(self) -> None:
        data = {"type": "success", "id": 1, "result": {"sessionId": "abc"}}
        resp = parse_response(data)
        assert isinstance(resp, SuccessResponse)
        assert resp.id == 1
        assert resp.result == {"sessionId": "abc"}

    def test_error_response(self) -> None:
        data = {
            "type": "error",
            "id": 2,
            "error": {"code": "invalid argument", "message": "bad params"},
        }
        resp = parse_response(data)
        assert isinstance(resp, ErrorResponse)
        assert resp.id == 2
        assert resp.error.code == "invalid argument"
        assert resp.error.message == "bad params"

    def test_error_response_with_stacktrace(self) -> None:
        data = {
            "type": "error",
            "id": 3,
            "error": {
                "code": "javascript error",
                "message": "ReferenceError",
                "stacktrace": "at line 1",
            },
        }
        resp = parse_response(data)
        assert isinstance(resp, ErrorResponse)
        assert resp.error.stacktrace == "at line 1"

    def test_error_data_optional_stacktrace(self) -> None:
        err = ErrorData(code="timeout", message="timed out")
        assert err.stacktrace is None

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown response type"):
            parse_response({"type": "weird", "id": 1})

    def test_success_extra_fields_allowed(self) -> None:
        data = {"type": "success", "id": 1, "result": {}, "extra": "foo"}
        resp = parse_response(data)
        assert isinstance(resp, SuccessResponse)
        assert resp.model_dump()["extra"] == "foo"
