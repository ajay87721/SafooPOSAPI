# Use a Debian-based Python image
FROM python:3.10-slim

# Install unixODBC (required for pyodbc to work)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unixodbc \
        unixodbc-dev \
        libodbc1 \
        odbcinst \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY main.py .

# Expose port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
