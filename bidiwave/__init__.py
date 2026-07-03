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
from bidiwave.modules.cdp import CDPModule
from bidiwave.modules.emulation import EmulationModule
from bidiwave.modules.input import InputModule
from bidiwave.modules.log import LogModule
from bidiwave.modules.network import NetworkModule
from bidiwave.modules.permissions import PermissionsModule
from bidiwave.modules.preload import PreloadModule
from bidiwave.modules.storage import StorageModule
from bidiwave.protocol.capabilities import Capabilities
from bidiwave.protocol.events import (
    BrowsingContextNavigationCompletedEvent,
    BrowsingContextUserPromptOpenedEvent,
    NetworkBeforeRequestSentEvent,
    NetworkDataReceivedEvent,
    NetworkFetchErrorEvent,
    NetworkResponseCompletedEvent,
    NetworkResponseStartedEvent,
    ScriptRealmCreatedEvent,
    ScriptRealmDestroyedEvent,
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
    AddCacheOverrideResult,
    AddPreloadScriptResult,
    Cookie,
    InputSource,
    KeyAction,
    LocateNodesResult,
    PointerAction,
    RealmInfo,
    UserContextInfo,
    Viewport,
    WheelAction,
)
from bidiwave.transport.connection import TransportConfig

__version__ = "1.6.2"

__all__ = [
    "AddPreloadScriptResult",
    "AddCacheOverrideResult",
    "ArrayValue",
    "AsyncHandler",
    "BiDiClient",
    "BiDiError",
    "BigIntValue",
    "BooleanValue",
    "BrowsingContext",
    "Capabilities",
    "CDPModule",
    "CapabilityError",
    "ClientConfig",
    "CommandError",
    "ConnectionError",
    "EmulationModule",
    "EventDispatcher",
    "HandleValue",
    "InvalidArgumentError",
    "JavaScriptError",
    "LogModule",
    "NoSuchFrameError",
    "NoSuchWindowError",
    "NullValue",
    "NumberValue",
    "ObjectValue",
    "Page",
    "PermissionsModule",
    "PreloadModule",
    "ProtocolError",
    "RemoteValue",
    "SessionError",
    "StringValue",
    "Subscription",
    "TimeoutError",
    "TransportConfig",
    "UndefinedValue",
    "Viewport",
    "NetworkModule",
    "NetworkBeforeRequestSentEvent",
    "NetworkResponseCompletedEvent",
    "NetworkResponseStartedEvent",
    "NetworkDataReceivedEvent",
    "NetworkFetchErrorEvent",
    "ScriptRealmCreatedEvent",
    "ScriptRealmDestroyedEvent",
    "BrowsingContextUserPromptOpenedEvent",
    "BrowsingContextNavigationCompletedEvent",
    "InputModule",
    "InputSource",
    "KeyAction",
    "LocateNodesResult",
    "PointerAction",
    "RealmInfo",
    "UserContextInfo",
    "WheelAction",
    "StorageModule",
    "Cookie",
    "__version__",
]
