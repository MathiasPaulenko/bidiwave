"""Excepciones de bidiwave."""


class BiDiError(Exception):
    """Base para todos los errores de bidiwave."""

    def __init__(self, message: str = "", code: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ConnectionError(BiDiError):
    """Error de conexión WebSocket."""


class CommandError(BiDiError):
    """El browser rechazó un comando."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message=message, code=code)