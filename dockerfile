# Use Python 3.12 slim as the base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy pyproject.toml first for dependency caching
COPY pyproject.toml .

# Set environment variable for Python version (used by uv)
ENV UV_PYTHON=python3.12

# Install Uvicorn + dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --no-dev

# Copy application code
COPY ./demo_code ./demo_code

# Expose port 80 for FastAPI
EXPOSE 80

# Run Uvicorn pointing to your FastAPI app
CMD ["uv", "run", "uvicorn", "demo_code.fast_api:app", "--host", "0.0.0.0", "--port", "80"]
