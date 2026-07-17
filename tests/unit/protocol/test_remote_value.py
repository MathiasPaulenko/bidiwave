"""Tests de RemoteValue y type narrowing."""

from bidiwave.protocol.remote_value import (
    ArrayBufferValue,
    ArrayValue,
    BigIntValue,
    BooleanValue,
    ErrorValue,
    GeneratorValue,
    HandleValue,
    HTMLCollectionValue,
    NodeListValue,
    NodeValue,
    NullValue,
    NumberValue,
    ObjectValue,
    PromiseValue,
    ProxyValue,
    RemoteValue,
    StringValue,
    TypedArrayValue,
    UndefinedValue,
    WeakMapValue,
    WeakSetValue,
    WindowValue,
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


def test_parse_function_without_handle():
    """With the default result ownership ("none") the browser omits the
    handle — parsing must not raise a validation error."""
    val = RemoteValue.parse({"type": "function"})
    assert isinstance(val, HandleValue)
    assert val.handle is None
    assert val.type == "function"


def test_parse_symbol_without_handle():
    val = RemoteValue.parse({"type": "symbol"})
    assert isinstance(val, HandleValue)
    assert val.handle is None


def test_type_narrowing_with_match():
    val = RemoteValue.parse({"type": "string", "value": "title"})
    match val:
        case StringValue(value=title):
            assert title == "title"
        case _:
            raise AssertionError("Expected StringValue")


def test_parse_weakmap():
    val = RemoteValue.parse({"type": "weakmap", "handle": "wm1"})
    assert isinstance(val, WeakMapValue)
    assert val.handle == "wm1"


def test_parse_weakset():
    val = RemoteValue.parse({"type": "weakset", "handle": "ws1"})
    assert isinstance(val, WeakSetValue)
    assert val.handle == "ws1"


def test_parse_generator():
    val = RemoteValue.parse({"type": "generator", "handle": "gen1"})
    assert isinstance(val, GeneratorValue)
    assert val.handle == "gen1"


def test_parse_error():
    val = RemoteValue.parse({
        "type": "error",
        "value": {"name": "TypeError", "message": "bad call"},
        "handle": "err1",
    })
    assert isinstance(val, ErrorValue)
    assert val.value["name"] == "TypeError"
    assert val.handle == "err1"


def test_parse_proxy():
    val = RemoteValue.parse({"type": "proxy", "handle": "px1"})
    assert isinstance(val, ProxyValue)
    assert val.handle == "px1"


def test_parse_promise():
    val = RemoteValue.parse({"type": "promise", "handle": "pr1"})
    assert isinstance(val, PromiseValue)
    assert val.handle == "pr1"


def test_parse_typedarray():
    val = RemoteValue.parse({"type": "typedarray", "value": [1, 2, 3], "handle": "ta1"})
    assert isinstance(val, TypedArrayValue)
    assert val.value == [1, 2, 3]
    assert val.handle == "ta1"


def test_parse_arraybuffer():
    val = RemoteValue.parse({"type": "arraybuffer", "value": [10, 20], "handle": "ab1"})
    assert isinstance(val, ArrayBufferValue)
    assert val.value == [10, 20]


def test_parse_nodelist():
    val = RemoteValue.parse({"type": "nodelist", "value": [{"type": "node", "sharedId": "n1"}]})
    assert isinstance(val, NodeListValue)
    assert len(val.value) == 1


def test_parse_htmlcollection():
    val = RemoteValue.parse({"type": "htmlcollection", "value": [], "handle": "hc1"})
    assert isinstance(val, HTMLCollectionValue)
    assert val.handle == "hc1"
    assert val.value == []


def test_parse_window():
    val = RemoteValue.parse({"type": "window", "handle": "win1"})
    assert isinstance(val, WindowValue)
    assert val.handle == "win1"


def test_parse_node_with_node_properties():
    val = RemoteValue.parse({
        "type": "node",
        "sharedId": "node-1",
        "value": {"nodeType": 1, "localName": "div"},
        "nodeProperties": {"nodeType": 1, "localName": "div", "namespaceURI": "http://www.w3.org/1999/xhtml"},
    })
    assert isinstance(val, NodeValue)
    assert val.shared_id == "node-1"
    assert val.node_properties["localName"] == "div"
    assert val.node_properties["namespaceURI"] == "http://www.w3.org/1999/xhtml"


def test_parse_object_with_nested_remote_value():
    val = RemoteValue.parse({
        "type": "object",
        "value": [
            ["key1", {"type": "string", "value": "hello"}],
            ["key2", {"type": "number", "value": 42}],
        ],
    })
    assert isinstance(val, ObjectValue)
    assert isinstance(val.value["key1"], StringValue)
    assert val.value["key1"].value == "hello"
    assert isinstance(val.value["key2"], NumberValue)
    assert val.value["key2"].value == 42


def test_parse_array_with_nested_remote_value():
    val = RemoteValue.parse({
        "type": "array",
        "value": [
            {"type": "string", "value": "a"},
            {"type": "number", "value": 1},
            {"type": "boolean", "value": True},
        ],
    })
    assert isinstance(val, ArrayValue)
    assert isinstance(val.value[0], StringValue)
    assert val.value[0].value == "a"
    assert isinstance(val.value[1], NumberValue)
    assert val.value[1].value == 1
    assert isinstance(val.value[2], BooleanValue)
    assert val.value[2].value is True
