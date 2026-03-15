FROM python:3.11-slim

WORKDIR /app
ENV ADK_FORCE_LOCAL_STORAGE=1

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly upgrade certifi so Python HTTP requests have the latest root certificates
RUN pip install --upgrade certifi

# Install playwright and its dependencies
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

COPY . .

ENV PYTHONUNBUFFERED=1
ENV GOOGLE_CLOUD_PROJECT=promptoptmizer

EXPOSE 8000

CMD ["gunicorn", "main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300", \
     "--workers", "1", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "debug"]