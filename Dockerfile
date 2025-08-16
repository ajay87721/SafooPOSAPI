# Use full Debian base (not slim) to ensure ODBC packages exist
FROM python:3.10-bullseye

# Install unixODBC and required libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unixodbc \
        unixodbc-dev \
        odbcinst \
        libodbc1 \
        && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY main.py .

# Expose port
EXPOSE 5000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
