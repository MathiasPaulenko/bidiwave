"""Excepciones de bidiwave."""


class BiDiError(Exception):
    """Base para todos los errores de bidiwave."""

    def __init__(self, message: str = "", code: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ConnectionError(BiDiError):
    """Error de conexión WebSocket."""


class TimeoutError(BiDiError):
    """Timeout esperando respuesta o navegación."""


class CapabilityError(BiDiError):
    """El browser no soporta la capability requerida."""


class ProtocolError(BiDiError):
    """Mensaje del protocolo inválido o inesperado."""


class SessionError(BiDiError):
    """Sesión inválida o expirada."""


class CommandError(BiDiError):
    """El browser rechazó un comando."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message=message, code=code)


class InvalidArgumentError(CommandError):
    """Argumento inválido."""


class NoSuchFrameError(CommandError):
    """Context no encontrado."""


class NoSuchWindowError(CommandError):
    """Window no encontrado."""


class JavaScriptError(CommandError):
    """Error al evaluar JavaScript."""


ERROR_CODE_MAP: dict[str, type[CommandError]] = {
    "invalid argument": InvalidArgumentError,
    "no such frame": NoSuchFrameError,
    "no such window": NoSuchWindowError,
    "javascript error": JavaScriptError,
}


def map_error(code: str, message: str) -> CommandError:
    """Mapea un código de error BiDi a la excepción correcta."""
    error_cls = ERROR_CODE_MAP.get(code, CommandError)
    return error_cls(code=code, message=message)