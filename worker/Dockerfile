FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        libgl1 \
        libglib2.0-0 \
        build-essential \
        python3-pip \
        && python3 -m ensurepip && \
        python3 -m pip install --upgrade pip setuptools && \
        rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]