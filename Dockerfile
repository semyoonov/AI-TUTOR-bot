FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY req.txt .
RUN pip install -r req.txt
COPY . .