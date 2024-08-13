FROM python:3.12-slim-bullseye AS base
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libgl1 \
        libgl1-mesa-dri \
        libglib2.0-0 \
        gcc\
        python3-dev\
        libzbar0\
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt
# RUN pip3 install "uvicorn[standard]" gunicorn
