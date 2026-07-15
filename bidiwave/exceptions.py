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


ERROR_CODE_MAP: dict[str, type[CommandError]] = {
    "invalid argument": InvalidArgumentError,
    "no such frame": NoSuchFrameError,
    "no such window": NoSuchWindowError,
    "javascript error": JavaScriptError,
    "invalid session": InvalidSessionError,
    "session not found": SessionNotFoundError,
    "unable to capture screen": UnableToCaptureScreenError,
    "unknown command": UnknownCommandError,
    "unsupported operation": UnsupportedOperationError,
}


def map_error(code: str, message: str) -> CommandError:
    """Maps a BiDi error code to the correct exception."""
    error_cls = ERROR_CODE_MAP.get(code, CommandError)
    return error_cls(code=code, message=message)