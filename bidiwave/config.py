"""Typed configuration for BiDiClient."""

from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """Configuration for BiDiClient."""

    timeout: float = Field(default=30.0, description="Global timeout in seconds")
    max_retries: int = Field(default=3, description="Reconnect attempts")
    retry_delay: float = Field(default=1.0, description="Initial delay between retries")
    retry_backoff: float = Field(default=2.0, description="Exponential multiplier")
    log_level: str = Field(default="INFO", description="Logging level")
