from fastapi import FastAPI

app = FastAPI(
    title="Resume Analyzer",
    description="""
        An intelligent Python-based application to automate résumé analysis using OCR and LLMs.
        It accepts multiple files (PDFs or images), extracts text via OCR, generates summaries, and answers custom queries about candidate profiles — all integrated with auditable logging via MongoDB.
    """,  # noqa: E501
)
