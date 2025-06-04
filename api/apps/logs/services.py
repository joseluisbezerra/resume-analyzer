from datetime import datetime
from uuid import UUID

from typing import (
    Optional,
    List
)

from database import db
from apps.logs.schemas import LogEntry


async def get_logs(
    request_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> List[LogEntry]:

    query = {}

    if request_id:
        query["request_id"] = str(request_id)

    if user_id:
        query["user_id"] = str(user_id)

    timestamp_filter = {}

    if start_date:
        timestamp_filter["$gte"] = start_date

    if end_date:
        timestamp_filter["$lte"] = end_date

    if timestamp_filter:
        query["timestamp"] = timestamp_filter

    logs_cursor = db.logs.find(query).sort("timestamp", -1)

    return await logs_cursor.to_list(length=limit)
