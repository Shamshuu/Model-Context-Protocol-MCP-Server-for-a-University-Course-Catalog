# Use official slim Python 3.12 image
FROM python:3.12-slim

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    DATABASE_URL=sqlite:////app/data/catalog.db

# Install curl for container health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and data directory
COPY app/ ./app/
COPY data/ ./data/
COPY README.md .

# Expose server port
EXPOSE 8080

# Run the MCP server
CMD ["python", "-m", "app.main"]
