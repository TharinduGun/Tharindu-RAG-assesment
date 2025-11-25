
# Stage 1: Build dependencies layer

FROM python:3.10-slim AS builder

# Do not generate .pyc files and send logs straight to stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create working directory for the build stage
WORKDIR /app

# Install system packages needed for building dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency list first to leverage Docker layer caching.
COPY requirements.txt .

# Install Python dependencies into a dedicated directory (/install).
# This path will be copied into the final runtime image.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime image
# contains python base image + installed dependencies + app source code

FROM python:3.10-slim AS runtime

# Same Python env behaviour in the final image.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory for the application.
WORKDIR /app

# Copy installed site-packages and scripts from the builder stage.
COPY --from=builder /install /usr/local

# Copy the application source code into the image.
# This includes:
# - main.py (FastAPI app)
# - rag_engine.py, models.py
# - data/attention.pdf
# - any other support files (e.g. app_streamlit.py, README.md,)
COPY . .

# Expose the port used by the FastAPI/Uvicorn server.
EXPOSE 8000

# Default command: start the FastAPI app via Uvicorn.
# Environment variables such as GEMINI_API_KEY and GEMINI_MODEL are expected to be provided at runtime
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
