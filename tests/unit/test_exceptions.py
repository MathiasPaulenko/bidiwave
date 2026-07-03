"""Tests for the exception hierarchy and map_error."""

from bidiwave.exceptions import (
    BiDiError,
    CommandError,
    InvalidArgumentError,
    JavaScriptError,
    NoSuchFrameError,
    NoSuchWindowError,
    map_error,
)


def test_map_error_invalid_argument():
    err = map_error("invalid argument", "bad param")
    assert isinstance(err, InvalidArgumentError)
    assert isinstance(err, CommandError)
    assert isinstance(err, BiDiError)
    assert err.code == "invalid argument"
    assert err.message == "bad param"


def test_map_error_javascript_error():
    err = map_error("javascript error", "SyntaxError")
    assert isinstance(err, JavaScriptError)
    assert err.code == "javascript error"


def test_map_error_no_such_frame():
    err = map_error("no such frame", "frame not found")
    assert isinstance(err, NoSuchFrameError)


def test_map_error_no_such_window():
    err = map_error("no such window", "window not found")
    assert isinstance(err, NoSuchWindowError)


def test_map_error_unknown_code_returns_command_error():
    err = map_error("unknown code", "something went wrong")
    assert isinstance(err, CommandError)
    assert not isinstance(err, InvalidArgumentError)
    assert err.code == "unknown code"


def test_command_error_has_code_and_message():
    err = CommandError(code="test", message="msg")
    assert err.code == "test"
    assert err.message == "msg"
    assert str(err) == "msg"
