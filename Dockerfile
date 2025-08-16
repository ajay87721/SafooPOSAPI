FROM python:3.10-bullseye

# Install unixODBC and ODBC libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        unixodbc \
        unixodbc-dev \
        libodbc1 \
        odbcinst \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api_server:app"]
