# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy pyproject.toml first for caching
COPY pyproject.toml .

ENV UV_PYTHON=python3.12


# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --no-dev

# Copy the app code
COPY ./demo_code ./demo_code

# Expose port for FastAPI
EXPOSE 80

# Run Uvicorn pointing to your file
CMD ["uv", "run", "uvicorn", "demo_code.fast_api:app", "--host", "0.0.0.0", "--port", "80"]

