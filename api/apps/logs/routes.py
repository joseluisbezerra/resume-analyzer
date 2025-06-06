from uuid import UUID
from http import HTTPStatus
from datetime import datetime
from fastapi import (
    HTTPException,
    APIRouter,
    Query,
    Path
)

from typing import (
    List,
    Optional
)

from apps.logs.schemas import LogEntry
from apps.logs.services import (
    get_logs,
    get_log_by_id
)

logs = APIRouter()


@logs.get(
    "/logs",
    response_model=List[LogEntry],
    summary="Retrieve system logs",
    description="Returns a list of log entries, optionally filtered by request ID, user ID, and a date/time range.",  # noqa: E501
)
async def list_logs(
    request_id: Optional[UUID] = Query(
        None,
        description="Filter logs by the request ID"
    ),
    user_id: Optional[UUID] = Query(
        None,
        description="Filter logs by the user ID"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Filter logs from this date/time (ISO 8601 format)"  # noqa: E501
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter logs up to this date/time (ISO 8601 format)"  # noqa: E501
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of logs to return (1–1000)"
    )
) -> List[LogEntry]:

    """
    Retrieve audit log entries based on optional filters.

    - **request_id**: Filter logs by the unique request identifier.
    - **user_id**: Filter logs by the user responsible for the action.
    - **start_date**: Return logs created at or after this date/time.
    - **end_date**: Return logs created at or before this date/time.
    - **limit**: Max number of logs to return (default: 100).

    Returns a list of logs matching the filters.
    """

    return await get_logs(request_id, user_id, start_date, end_date, limit)


@logs.get(
    "/logs/{id}",
    response_model=LogEntry,
    summary="Retrieve a log by ID",
    description="Returns a single log entry based on its unique identifier.",
)
async def retrieve_log_by_id(
    id: UUID = Path(..., description="The UUID of the log to retrieve")
) -> LogEntry:
    """
    Retrieve a specific log entry by its UUID.

    - **id**: UUID of the log to retrieve.

    Returns the log if found, otherwise raises 404.
    """
    log = await get_log_by_id(id)

    if not log:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Log not found"
        )

    return log
