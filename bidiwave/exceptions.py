"""bidiwave exceptions."""


class BiDiError(Exception):
    """Base for all bidiwave errors."""

    def __init__(self, message: str = "", code: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class BiDiConnectionError(BiDiError):
    """WebSocket connection error."""


class BiDiTimeoutError(BiDiError, TimeoutError):
    """Timeout waiting for response or navigation.

    Also a builtin ``TimeoutError`` so callers can catch either class.
    """


class CapabilityError(BiDiError):
    """The browser does not support the required capability."""


class ProtocolError(BiDiError):
    """Invalid or unexpected protocol message."""


class SessionError(BiDiError):
    """Invalid or expired session."""


class CommandError(BiDiError):
    """The browser rejected a command."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message=message, code=code)


class InvalidArgumentError(CommandError):
    """Invalid argument."""


class NoSuchFrameError(CommandError):
    """Context not found."""


class NoSuchWindowError(CommandError):
    """Window not found."""


class JavaScriptError(CommandError):
    """Error evaluating JavaScript."""


class InvalidSessionError(CommandError):
    """Invalid or expired session."""


class SessionNotFoundError(CommandError):
    """Session not found."""


class UnableToCaptureScreenError(CommandError):
    """Unable to capture screen."""


class UnknownCommandError(CommandError):
    """Unknown command."""


class UnsupportedOperationError(CommandError):
    """Unsupported operation."""


class NoSuchElementError(CommandError):
    """Element not found."""


class NoSuchCookieError(CommandError):
    """Cookie not found."""


class StaleElementReferenceError(CommandError):
    """Element reference is stale."""


class ElementNotInteractableError(CommandError):
    """Element not interactable."""


class InsecureCertificateError(CommandError):
    """Insecure certificate."""


class MoveTargetOutOfBoundsError(CommandError):
    """Move target out of bounds."""


class NoSuchAlertError(CommandError):
    """No such alert."""


class NoSuchShadowRootError(CommandError):
    """No such shadow root."""


class DetachedShadowRootError(CommandError):
    """Detached shadow root."""


class InvalidWebExtensionError(CommandError):
    """Invalid web extension."""


class NoSuchUserContextError(CommandError):
    """No such user context."""


class SessionNotCreatedError(CommandError):
    """Session not created."""


class ProtocolTimeoutError(CommandError):
    """Protocol-level timeout error from the browser."""


class InvalidSessionIdError(CommandError):
    """Invalid session id."""


class NoSuchHandleError(CommandError):
    """No such handle."""


class NoSuchHistoryEntryError(CommandError):
    """No such history entry."""


class NoSuchInterceptError(CommandError):
    """No such intercept."""


class NoSuchNetworkCollectorError(CommandError):
    """No such network collector."""


class NoSuchNodeError(CommandError):
    """No such node."""


class NoSuchRequestError(CommandError):
    """No such request."""


class NoSuchScriptError(CommandError):
    """No such script."""


class NoSuchStoragePartitionError(CommandError):
    """No such storage partition."""


class UnableToCloseBrowsingContextError(CommandError):
    """Unable to close browsing context."""


class UnableToSetFileInputError(CommandError):
    """Unable to set file input."""


class UnderspecifiedStoragePartitionError(CommandError):
    """Underspecified storage partition."""


class UnknownBiDiError(CommandError):
    """Unknown error."""


ERROR_CODE_MAP: dict[str, type[CommandError]] = {
    "invalid argument": InvalidArgumentError,
    "invalid session": InvalidSessionError,
    "invalid session id": InvalidSessionIdError,
    "javascript error": JavaScriptError,
    "no such alert": NoSuchAlertError,
    "no such cookie": NoSuchCookieError,
    "no such element": NoSuchElementError,
    "no such frame": NoSuchFrameError,
    "no such handle": NoSuchHandleError,
    "no such history entry": NoSuchHistoryEntryError,
    "no such intercept": NoSuchInterceptError,
    "no such network collector": NoSuchNetworkCollectorError,
    "no such node": NoSuchNodeError,
    "no such request": NoSuchRequestError,
    "no such script": NoSuchScriptError,
    "no such shadow root": NoSuchShadowRootError,
    "detached shadow root": DetachedShadowRootError,
    "no such storage partition": NoSuchStoragePartitionError,
    "no such user context": NoSuchUserContextError,
    "no such window": NoSuchWindowError,
    "session not created": SessionNotCreatedError,
    "session not found": SessionNotFoundError,
    "unable to capture screen": UnableToCaptureScreenError,
    "unable to close browsing context": UnableToCloseBrowsingContextError,
    "unable to set file input": UnableToSetFileInputError,
    "underspecified storage partition": UnderspecifiedStoragePartitionError,
    "unknown command": UnknownCommandError,
    "unknown error": UnknownBiDiError,
    "unsupported operation": UnsupportedOperationError,
    "stale element reference": StaleElementReferenceError,
    "element not interactable": ElementNotInteractableError,
    "insecure certificate": InsecureCertificateError,
    "move target out of bounds": MoveTargetOutOfBoundsError,
    "invalid web extension": InvalidWebExtensionError,
    "timeout": ProtocolTimeoutError,
}


def map_error(code: str, message: str) -> CommandError:
    """Maps a BiDi error code to the correct exception."""
    error_cls = ERROR_CODE_MAP.get(code, CommandError)
    return error_cls(code=code, message=message)