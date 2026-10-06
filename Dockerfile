FROM python:3.13-slim

WORKDIR /app

# Python runtime settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# System packages required by some Python dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Install CPU-only PyTorch.
# This prevents pip from pulling the massive CUDA/NVIDIA stack.
RUN pip install \
    --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.14.1

# Install the remaining application dependencies
RUN pip install \
    --no-cache-dir \
    -r requirements.txt

# Copy application source
COPY app ./app

# Copy required application data
COPY data ./data

# API port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]