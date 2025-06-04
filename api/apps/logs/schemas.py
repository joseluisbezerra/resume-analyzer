from uuid import UUID

from pydantic import (
    BaseModel,
    Field
)

from datetime import (
    datetime,
    timezone
)


class LogEntry(BaseModel):
    request_id: UUID
    user_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # noqa: E501
    query: str
    result: str
