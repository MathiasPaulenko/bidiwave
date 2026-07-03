"""Tests de RemoteValue y type narrowing."""

from bidiwave.protocol.remote_value import (
    ArrayValue,
    BigIntValue,
    BooleanValue,
    HandleValue,
    NullValue,
    NumberValue,
    ObjectValue,
    RemoteValue,
    StringValue,
    UndefinedValue,
)


def test_parse_string():
    val = RemoteValue.parse({"type": "string", "value": "hello"})
    assert isinstance(val, StringValue)
    assert val.value == "hello"


def test_parse_number():
    val = RemoteValue.parse({"type": "number", "value": 42})
    assert isinstance(val, NumberValue)
    assert val.value == 42


def test_parse_boolean():
    val = RemoteValue.parse({"type": "boolean", "value": True})
    assert isinstance(val, BooleanValue)
    assert val.value is True


def test_parse_null():
    val = RemoteValue.parse({"type": "null"})
    assert isinstance(val, NullValue)


def test_parse_undefined():
    val = RemoteValue.parse({"type": "undefined"})
    assert isinstance(val, UndefinedValue)


def test_parse_bigint():
    val = RemoteValue.parse({"type": "bigint", "value": "123456789"})
    assert isinstance(val, BigIntValue)
    assert val.value == "123456789"


def test_parse_object_with_handle():
    val = RemoteValue.parse({"type": "object", "handle": "h1"})
    assert isinstance(val, ObjectValue)
    assert val.handle == "h1"


def test_parse_array():
    val = RemoteValue.parse({"type": "array", "value": [1, 2, 3]})
    assert isinstance(val, ArrayValue)
    assert val.value == [1, 2, 3]


def test_parse_function_returns_handle():
    val = RemoteValue.parse({"type": "function", "handle": "f1"})
    assert isinstance(val, HandleValue)
    assert val.handle == "f1"
    assert val.type == "function"


def test_type_narrowing_with_match():
    val = RemoteValue.parse({"type": "string", "value": "title"})
    match val:
        case StringValue(value=title):
            assert title == "title"
        case _:
            raise AssertionError("Expected StringValue")
