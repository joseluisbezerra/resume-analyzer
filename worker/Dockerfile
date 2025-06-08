FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-por \
        build-essential \
        python3-pip && \
    python3 -m pip install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]