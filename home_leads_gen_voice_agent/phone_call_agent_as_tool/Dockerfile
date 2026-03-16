FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade certifi

# Explicitly install playwright first to prevent the module error
RUN pip install playwright

# Download the playwright browsers
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

# Copy the rest of your application code
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start the Voice API using asyncio
CMD ["uvicorn", "home_leads_gen_voice_agent.phone_call_agent_as_tool.voice_api:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]