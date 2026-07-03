"""Typed configuration for BiDiClient."""

from typing import Literal

from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """Configuration for BiDiClient."""

    timeout: float = Field(default=30.0, description="Global timeout in seconds")
    max_retries: int = Field(default=3, description="Reconnect attempts")
    retry_delay: float = Field(default=1.0, description="Initial delay between retries")
    retry_backoff: float = Field(default=2.0, description="Exponential multiplier")
    max_queue: int = Field(default=1000, description="Maximum event queue size")
    drop_policy: Literal["oldest", "newest", "block"] = Field(
        default="oldest", description="What to do when the queue is full"
    )
    log_level: str = Field(default="INFO", description="Logging level")
