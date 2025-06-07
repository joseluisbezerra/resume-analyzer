from uuid import UUID
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

from apps.utils.enums import LogStatus


class LogEntry(BaseModel):
    id: UUID
    request_id: UUID
    user_id: UUID
    timestamp: datetime
    query: str
    result: Dict
    status: LogStatus
