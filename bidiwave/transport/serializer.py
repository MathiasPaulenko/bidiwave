"""Serialización de mensajes BiDi."""

import json
from typing import Any


def serialize_command(command_id: int, method: str, params: dict[str, Any]) -> str:
    """Serializa un comando a JSON string."""
    return json.dumps(
        {
            "id": command_id,
            "method": method,
            "params": params,
        }
    )


def deserialize_message(raw: str) -> dict[str, Any]:
    """Deserializa un mensaje JSON del browser."""
    result: dict[str, Any] = json.loads(raw)
    return result