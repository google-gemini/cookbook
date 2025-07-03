# Use a specific version for reproducibility
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Set environment variables to prevent Python from writing .pyc files and to run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Install system dependencies required for the project
# Add any needed libs here, e.g., build-essential for some pip packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages (leverages Docker cache)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

# Expose the port your app will run on
EXPOSE 8000

# Command to run the application (can be overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
