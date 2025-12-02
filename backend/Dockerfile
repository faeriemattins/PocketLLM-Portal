FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for building llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ ./backend/

# Copy download_model.py from workspace root into the image
COPY download_model.py .

# Copy entrypoint script into the backend folder and make executable
COPY backend/entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Use entrypoint to download models on first start, then launch the app
ENTRYPOINT ["/app/backend/entrypoint.sh"]
