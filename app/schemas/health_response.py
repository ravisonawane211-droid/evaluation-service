
from pydantic import BaseModel

from pydantic import Field
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.now(),
        description="Response timestamp",
    )
    version: str = Field(..., description="Application version")