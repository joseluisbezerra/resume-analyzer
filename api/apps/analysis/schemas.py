from pydantic import BaseModel
from apps.logs.schemas import LogEntry


class AnalyzeResponse(BaseModel):
    message: str
    log: LogEntry
