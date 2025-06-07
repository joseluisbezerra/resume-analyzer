# Resume Analyzer

An intelligent Python-based application to automate résumé analysis using OCR and LLMs.
It accepts multiple files (PDFs or images), extracts text via OCR, generates summaries, and answers custom queries about candidate profiles — all integrated with auditable logging via MongoDB.

## Installation

1. After cloning the project, create an .env file from the .env.example file as well as add the missing environment variables:

```
cp .env.example .env
```

2. Create and start the containers:

```
docker compose up -d --build
```

3. Test the installation by accessing the development server, API documentation is available at http://127.0.0.1:8000/docs/.
