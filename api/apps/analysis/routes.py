import shutil
from uuid import UUID
from http import HTTPStatus
from pathlib import Path
from fastapi import (
    HTTPException,
    UploadFile,
    APIRouter,
    File,
    Form
)
from typing import (
    Optional,
    List
)

from apps.analysis.schemas import AnalyzeResponse
from apps.logs.services import create_log_entry
from celery_app import celery

analysis = APIRouter()
UPLOAD_FOLDER = Path("/shared")


@analysis.post(
    "/analyze-resumes/",
    response_model=AnalyzeResponse,
    summary="Analyze resumes (PDF, PNG, JPEG)",
    response_description="Task initiation message and log data"
)
async def analyze_resumes(
    files: List[UploadFile] = File(...),
    query: Optional[str] = Form(None),
    request_id: UUID = Form(...),
    user_id: UUID = Form(...)
):
    """
    Initiates analysis of one or more resume files.

    This endpoint receives multiple files (PDF or image format), stores them temporarily,
    creates an audit log entry, and sends an asynchronous Celery task for OCR and NLP processing.

    - **files**: List of uploaded resume files (PDF, JPEG, PNG)
    - **query**: Optional string for additional filtering or metadata
    - **request_id**: UUID used to track the request
    - **user_id**: UUID of the user performing the request

    Returns a JSON response indicating how many files were accepted for analysis and
    a log object with tracking details.
    """  # noqa: E501

    files_names = []

    for file in files:
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:  # noqa: E501
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Unsupported file type: {file.filename}"
            )

        file_location = UPLOAD_FOLDER / file.filename

        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        files_names.append(file.filename)

    log = await create_log_entry(
        request_id=request_id,
        user_id=user_id,
        query=query
    )

    celery.send_task(
        "worker.analyze_resumes_task",
        args=[files_names, log.id, query]
    )

    return {
        "message": f"Analysis of {len(files)} file(s) successfully started.",
        "log": log
    }
