from fastapi import FastAPI
from apps.logs.routes import logs
from apps.analysis.routes import analysis

app = FastAPI(
    title="Resume Analyzer",
    description="An intelligent Python-based application to automate résumé analysis using OCR and LLMs. It accepts multiple files (PDFs or images), extracts text via OCR, generates summaries, and answers custom queries about candidate profiles — all integrated with auditable logging via MongoDB.",  # noqa: E501
)


app.include_router(logs, prefix="/api", tags=["logs"])
app.include_router(analysis, prefix="/api", tags=["analysis"])
