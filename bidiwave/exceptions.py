"""bidiwave exceptions."""


class BiDiError(Exception):
    """Base for all bidiwave errors."""

    def __init__(self, message: str = "", code: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class BiDiConnectionError(BiDiError):
    """WebSocket connection error."""


class BiDiTimeoutError(BiDiError):
    """Timeout waiting for response or navigation."""


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


class TimeoutError(CommandError):
    """Timeout."""


ERROR_CODE_MAP: dict[str, type[CommandError]] = {
    "invalid argument": InvalidArgumentError,
    "no such frame": NoSuchFrameError,
    "no such window": NoSuchWindowError,
    "javascript error": JavaScriptError,
    "invalid session": InvalidSessionError,
    "session not found": SessionNotFoundError,
    "session not created": SessionNotCreatedError,
    "unable to capture screen": UnableToCaptureScreenError,
    "unknown command": UnknownCommandError,
    "unsupported operation": UnsupportedOperationError,
    "no such element": NoSuchElementError,
    "no such cookie": NoSuchCookieError,
    "stale element reference": StaleElementReferenceError,
    "element not interactable": ElementNotInteractableError,
    "insecure certificate": InsecureCertificateError,
    "move target out of bounds": MoveTargetOutOfBoundsError,
    "no such alert": NoSuchAlertError,
    "no such shadow root": NoSuchShadowRootError,
    "detached shadow root": DetachedShadowRootError,
    "invalid web extension": InvalidWebExtensionError,
    "no such user context": NoSuchUserContextError,
    "timeout": TimeoutError,
}


def map_error(code: str, message: str) -> CommandError:
    """Maps a BiDi error code to the correct exception."""
    error_cls = ERROR_CODE_MAP.get(code, CommandError)
    return error_cls(code=code, message=message)