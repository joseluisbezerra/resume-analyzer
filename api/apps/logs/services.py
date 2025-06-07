from datetime import (
    datetime,
    timezone
)

from uuid import (
    UUID,
    uuid4
)

from typing import (
    Optional,
    List
)

from database import db
from apps.logs.schemas import LogEntry
from apps.utils.enums import LogStatus


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


async def get_log_by_id(id: UUID) -> Optional[LogEntry]:
    log = await db.logs.find_one({"id": str(id)})

    if log:
        return LogEntry(**log)

    return None


async def create_log_entry(
    request_id: UUID,
    user_id: UUID,
    query="",
) -> LogEntry:
    log_dict = {
        "id": str(uuid4()),
        "request_id": str(request_id),
        "user_id": str(user_id),
        "timestamp": datetime.now(timezone.utc),
        "query": query,
        "result": {},
        "status": LogStatus.PROCESSING
    }

    await db.logs.insert_one(log_dict)

    return LogEntry(**log_dict)
