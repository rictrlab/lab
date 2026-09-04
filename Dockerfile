# Production image: FastAPI backend + problems bundle.
# Listens on $PORT (Render injects it; HF Spaces expects 7860).
# Build from the repo root:  docker build -f Dockerfile -t rictrlab-api .
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2
ENV OPENBLAS_NUM_THREADS=2

WORKDIR /app

# System deps (torch CPU needs a compiler only at build time for some pins)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY problems ./problems

EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
