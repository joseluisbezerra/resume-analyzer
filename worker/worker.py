import os
import logging
import requests
import json

from PIL import Image
from uuid import UUID
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pdf2image import convert_from_path
import pytesseract


from celery_app import celery

load_dotenv()

DATA_DIR = Path("/shared")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

logger = logging.getLogger("analyze_resumes")


@celery.task(name="worker.analyze_resumes_task")
def analyze_resumes_task(file_names: List[str], log_id: UUID, query=''):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    try:
        logger.info("Processing started successfully for log_id: %s", log_id)

        result = {
            "summaries": []
        }

        for file_name in file_names:
            file_path = DATA_DIR / file_name

            extracted_text = []
            images = []

            logger.info("OCR started successfully for file: %s", file_name)

            if file_name.lower().endswith(".pdf"):
                images += convert_from_path(str(file_path))
            else:
                images.append(Image.open(file_path))

            for image in images:
                text = pytesseract.image_to_string(image, lang='por')
                extracted_text.append(text)

            logger.info("Summarize started successfully for file: %s", file_name)  # noqa: E501

            summary = summarize(" ".join(extracted_text))
            result["summaries"].append(summary)

            file_path.unlink(missing_ok=True)

            logger.info("OCR and summarize completed successfully for file: %s", file_name)  # noqa: E501

        if (query.strip() != ''):
            logger.info("Match resume to question started successfully")

            result["analysis"] = match_resume_to_question(
                summaries=result["summaries"],
                question=query
            )

            logger.info("Match resume to question completed successfully")

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
        "http://ollama:11434/api/chat",
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

    return json.loads(response.json()["message"]["content"])


def match_resume_to_question(summaries: list[dict], question: str) -> str:
    prompt = (
        "You are an expert in resume analysis and candidate-job matching.\n\n"
        "Task:\n"
        "- You will be given a job-related question (which may be written in any language).\n"  # noqa: E501
        "- A list of structured candidate resumes will also be provided.\n"
        "- Internally, translate the question into English if needed.\n"
        "- Then, evaluate the resumes based on the meaning of the question.\n"
        "- Select the single most suitable candidate, or respond 'None' if no candidate matches well.\n\n"  # noqa: E501
        "Your response must include:\n"
        "1. The name of the best-matching candidate (or 'None');\n"
        "2. A clear and objective justification for your choice (or lack thereof);\n"  # noqa: E501
        "3. A concise summary of how the selected candidate aligns (or does not align) with the job requirements.\n\n"  # noqa: E501
        "Guidelines:\n"
        "- Do not include the translated question in your response.\n"
        "- Be specific and only use information present in the resumes.\n"
        "- Avoid vague or generic statements.\n\n"
        f"Question:\n{question}\n\n"
        f"Resumes:\n{summaries}"
    )

    response = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "llama3.2:latest",
            "prompt": prompt,
            "stream": False,
        }
    )

    return response.json()["response"]
