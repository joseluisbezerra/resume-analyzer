import os
import logging
import requests
import numpy as np

from PIL import Image
from uuid import UUID
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from paddleocr import PaddleOCR
from pdf2image import convert_from_path

from celery_app import celery

load_dotenv()

DATA_DIR = Path("/shared")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

ocr_engine = PaddleOCR(
    ocr_version='PP-OCRv3',
    use_textline_orientation=True,
    lang='pt'
)

logger = logging.getLogger("analyze_resumes")


@celery.task(name="worker.analyze_resumes_task")
def analyze_resumes_task(file_names: List[str], log_id: UUID, query=''):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    try:
        result = {
            "summaries": []
        }

        for file_name in file_names:
            file_path = DATA_DIR / file_name

            extracted_text = []
            images = []

            if file_name.lower().endswith(".pdf"):
                images += convert_from_path(str(file_path))
            else:
                images.append(Image.open(file_path))

            for image in images:
                image_np = np.array(image.convert("RGB"))
                ocr_result = ocr_engine.predict(image_np)
                text = "\n".join(ocr_result[0]["rec_texts"])
                extracted_text.append(text)

            summary = summarize(" ".join(extracted_text))
            result["summaries"].append(summary)

            file_path.unlink(missing_ok=True)

        if (query.strip() != ''):
            result["analysis"] = match_resume_to_question(
                summaries=result.summaries,
                question=query
            )

        db.logs.find_one_and_update(
            {"id": str(log_id)},
            {"$set": {"status": 'PROCESSED', "result": result}},
        )

        logger.info("Processing completed successfully for log_id: %s", log_id)
    except Exception as error:
        for file_name in file_names:
            file_path = DATA_DIR / file_name
            file_path.unlink(missing_ok=True)

        db.logs.find_one_and_update(
            {"id": str(log_id)},
            {"$set": {"status": 'PROCESSING_FAILED'}},
        )

        logger.exception("Error while processing resumes: %s", error)


def summarize(resume: str) -> dict:
    prompt = (
        "You are an expert in analyzing resumes. Read the resume below and return a structured summary in English, "  # noqa: E501
        "even if the resume is written in another language. Extract and translate the following information:\n"  # noqa: E501
        "- Full name\n"
        "- A concise professional summary (max 3 sentences)\n"
        "- List of relevant skills (keywords only)\n"
        "- Full address or city/country if full address is unavailable\n"
        "- Languages spoken\n\n"
        "Resume:\n"
        f"{resume}"
    )

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "summary": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "address": {"type": "string"},
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                },
                "required": [
                    "name",
                    "skills",
                    "summary",
                    "address",
                    "languages"
                ]
            }
        }
    )

    return response.json()


def match_resume_to_question(summaries: list[dict], question: str) -> dict:
    prompt = (
        "You are an expert in resume screening and candidate-job matching.\n"
        "Below is a list of structured resumes and a job-related question written in any language.\n"  # noqa: E501
        "First, translate the question into English. Then, based on the translated question, identify which resume best fits the requirements.\n"  # noqa: E501
        "Provide the following in your response:\n"
        "1. The name of the most suitable candidate (or None if none match);\n"
        "2. A justification explaining why that candidate was selected (or why none match);\n"  # noqa: E501
        "3. A brief summary of how the candidate's profile aligns (or doesn't) with the job described.\n"  # noqa: E501
        "Be as objective and specific as possible.\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Resumes:\n"
        f"{summaries}"
    )

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "best_candidate": {"type": ["string", "null"]},
                    "justification": {"type": "string"},
                    "alignment_summary": {"type": "string"}
                },
                "required": [
                    "best_candidate",
                    "justification",
                    "alignment_summary"
                ]
            }
        }
    )

    return response.json()
