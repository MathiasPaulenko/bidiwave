"""Configuración tipada del BiDiClient."""

from typing import Literal

from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """Configuración del BiDiClient."""

    timeout: float = Field(default=30.0, description="Timeout global en segundos")
    max_retries: int = Field(default=3, description="Reconnect attempts")
    retry_delay: float = Field(default=1.0, description="Delay inicial entre retries")
    retry_backoff: float = Field(default=2.0, description="Multiplicador exponencial")
    max_queue: int = Field(default=1000, description="Tamaño máximo de la event queue")
    drop_policy: Literal["oldest", "newest", "block"] = Field(
        default="oldest", description="Qué hacer cuando la queue se llena"
    )
    log_level: str = Field(default="INFO", description="Nivel de logging")
