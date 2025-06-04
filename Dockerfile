FROM python:3.12.9-slim

WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api /api

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
