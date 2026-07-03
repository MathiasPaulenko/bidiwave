"""bidiwave — WebDriver BiDi for Python."""

from bidiwave.client import BiDiClient
from bidiwave.config import ClientConfig
from bidiwave.convenience.page import Page
from bidiwave.events.dispatcher import EventDispatcher
from bidiwave.events.handlers import AsyncHandler, Subscription
from bidiwave.exceptions import (
    BiDiError,
    CapabilityError,
    CommandError,
    ConnectionError,
    InvalidArgumentError,
    JavaScriptError,
    NoSuchFrameError,
    NoSuchWindowError,
    ProtocolError,
    SessionError,
    TimeoutError,
)
from bidiwave.modules.browsing import BrowsingContext
from bidiwave.modules.input import InputModule
from bidiwave.modules.network import NetworkModule
from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.capabilities import Capabilities
from bidiwave.protocol.events import (
    NetworkBeforeRequestSentEvent,
    NetworkFetchErrorEvent,
    NetworkResponseCompletedEvent,
)
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
from bidiwave.protocol.results import (
    Cookie,
    InputSource,
    KeyAction,
    LocateNodesResult,
    PointerAction,
    RealmInfo,
    WheelAction,
)
from bidiwave.transport.connection import TransportConfig

__version__ = "1.4.0"

__all__ = [
    "ArrayValue",
    "AsyncHandler",
    "BiDiClient",
    "BiDiError",
    "BigIntValue",
    "BooleanValue",
    "BrowsingContext",
    "Capabilities",
    "CapabilityError",
    "ClientConfig",
    "CommandError",
    "ConnectionError",
    "EventDispatcher",
    "HandleValue",
    "InvalidArgumentError",
    "JavaScriptError",
    "NoSuchFrameError",
    "NoSuchWindowError",
    "NullValue",
    "NumberValue",
    "ObjectValue",
    "Page",
    "ProtocolError",
    "RemoteValue",
    "SessionError",
    "StringValue",
    "Subscription",
    "TimeoutError",
    "TransportConfig",
    "UndefinedValue",
    "NetworkModule",
    "NetworkBeforeRequestSentEvent",
    "NetworkResponseCompletedEvent",
    "NetworkFetchErrorEvent",
    "InputModule",
    "InputSource",
    "KeyAction",
    "LocateNodesResult",
    "PointerAction",
    "RealmInfo",
    "WheelAction",
    "StorageModule",
    "Cookie",
    "__version__",
]
