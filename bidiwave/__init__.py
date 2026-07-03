"""bidiwave — WebDriver BiDi for Python."""

from bidiwave.client import BiDiClient
from bidiwave.exceptions import BiDiError, CommandError, ConnectionError

__version__ = "0.1.0"

__all__ = [
    "BiDiClient",
    "BiDiError",
    "CommandError",
    "ConnectionError",
    "__version__",
]
