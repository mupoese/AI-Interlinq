FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for performance testing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    htop \
    iotop \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .
RUN pip install -e .

# Create benchmark user
RUN useradd --create-home --shell /bin/bash benchmark_user
RUN chown -R benchmark_user:benchmark_user /app
USER benchmark_user

# Default benchmark command
CMD ["ai-interlinq", "benchmark", "--duration", "300", "--agents", "50", "--rate", "1000"]
