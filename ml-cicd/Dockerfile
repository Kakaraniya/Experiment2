FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements-docker.txt ./
RUN pip install --no-cache-dir --default-timeout=120 --retries=5 -r requirements-docker.txt

COPY src ./src
COPY scripts ./scripts
COPY models ./models
COPY data ./data

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
