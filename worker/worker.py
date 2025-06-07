from typing import List
from uuid import UUID
from pathlib import Path
from paddleocr import PaddleOCR

from celery_app import celery

ocr_engine = PaddleOCR(ocr_version='PP-OCRv3', use_angle_cls=True, lang='pt')
DATA_DIR = Path("/shared")


@celery.task(name="worker.analyze_resumes_task")
def analyze_resumes_task(filenames: List[str], log_id: UUID, query=''):
    pass
