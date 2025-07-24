FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy source code
COPY . .

# Install the package
RUN pip install --no-deps -e .

# Create production user
RUN useradd --create-home --shell /bin/bash --uid 1000 ai_user
RUN chown -R ai_user:ai_user /app
USER ai_user

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Production optimizations
ENV PYTHONOPTIMIZE=2
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ai_interlinq; print('OK')" || exit 1

# Production command
CMD ["ai-interlinq", "serve", "--host", "0.0.0.0", "--port", "8765", "--max-connections", "10000"]
