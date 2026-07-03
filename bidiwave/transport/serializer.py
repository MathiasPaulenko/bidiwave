"""Serialization of BiDi messages."""

import json
from typing import Any


def serialize_command(command_id: int, method: str, params: dict[str, Any]) -> str:
    """Serializes a command to a JSON string."""
    return json.dumps(
        {
            "id": command_id,
            "method": method,
            "params": params,
        }
    )


def deserialize_message(raw: str) -> dict[str, Any]:
    """Deserializes a JSON message from the browser."""
    result: dict[str, Any] = json.loads(raw)
    return result