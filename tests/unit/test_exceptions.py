"""Tests for the exception hierarchy and map_error."""

import pytest

from bidiwave.exceptions import (
    BiDiError,
    CommandError,
    DetachedShadowRootError,
    ElementNotInteractableError,
    InsecureCertificateError,
    InvalidArgumentError,
    InvalidWebExtensionError,
    JavaScriptError,
    MoveTargetOutOfBoundsError,
    NoSuchAlertError,
    NoSuchCookieError,
    NoSuchElementError,
    NoSuchFrameError,
    NoSuchShadowRootError,
    NoSuchUserContextError,
    NoSuchWindowError,
    ProtocolTimeoutError,
    SessionNotCreatedError,
    StaleElementReferenceError,
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


@pytest.mark.parametrize(
    "code,exc_cls",
    [
        ("no such element", NoSuchElementError),
        ("no such cookie", NoSuchCookieError),
        ("stale element reference", StaleElementReferenceError),
        ("element not interactable", ElementNotInteractableError),
        ("insecure certificate", InsecureCertificateError),
        ("move target out of bounds", MoveTargetOutOfBoundsError),
        ("no such alert", NoSuchAlertError),
        ("no such shadow root", NoSuchShadowRootError),
        ("detached shadow root", DetachedShadowRootError),
        ("invalid web extension", InvalidWebExtensionError),
        ("no such user context", NoSuchUserContextError),
        ("session not created", SessionNotCreatedError),
        ("timeout", ProtocolTimeoutError),
    ],
)
def test_map_error_new_codes(code: str, exc_cls: type[CommandError]) -> None:
    err = map_error(code, "test message")
    assert isinstance(err, exc_cls)
    assert isinstance(err, CommandError)
    assert err.code == code
