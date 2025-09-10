# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy pyproject.toml first for caching
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv sync

# Copy the app code
COPY ./demo-code ./demo-code

# Expose port for FastAPI
EXPOSE 8000

# Run Uvicorn pointing to your file
CMD ["uvicorn", "demo-code.fast_api:app", "--host", "0.0.0.0", "--port", "8000"]